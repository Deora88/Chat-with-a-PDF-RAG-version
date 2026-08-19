from flask import Flask, request, render_template
import os
import uuid
from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

from chunking import chunk_text

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

UPLOAD_FOLDER = "uploads"

# Groq client for generating answers
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Embedding model, loaded once when the server starts (not per-request —
# loading it is slow, so we want to pay that cost only once)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB client, saves to disk in ./chroma_db so data survives restarts
chroma_client = chromadb.PersistentClient(path="./chroma_db")


@app.errorhandler(413)
def file_too_large(e):
    return {"error": "File is too large. Maximum allowed size is 10MB."}, 413


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return {"error": "No file part in request"}, 400

    file = request.files["file"]

    if file.filename == "":
        return {"error": "No file selected"}, 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # 1. Extract text (same as before)
    reader = PdfReader(save_path)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    # 2. Chunk the text
    chunks = chunk_text(extracted_text, chunk_size=500, overlap=50)

    # 3. Generate a document_id and create a ChromaDB collection for it
    document_id = str(uuid.uuid4())
    collection_name = f"doc_{document_id.replace('-', '')}"
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # 4. Embed all chunks and store them
    embeddings = embedding_model.encode(chunks).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    return {
        "document_id": document_id,
        "filename": file.filename,
        "num_pages": len(reader.pages),
        "char_count": len(extracted_text),
        "num_chunks": len(chunks)
    }


@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()

    document_id = data.get("document_id")
    question = data.get("question")

    if not document_id or not question:
        return {"error": "document_id and question are both required"}, 400

    collection_name = f"doc_{document_id.replace('-', '')}"

    try:
        collection = chroma_client.get_collection(name=collection_name)
    except Exception:
        return {"error": "Document not found"}, 404

    # 1. Embed the question
    question_embedding = embedding_model.encode([question]).tolist()

    # 2. Retrieve the most relevant chunks (top 4)
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=4
    )
    relevant_chunks = results["documents"][0]

    # 3. Build a prompt using ONLY the retrieved chunks, not the whole document
    context = "\n\n---\n\n".join(relevant_chunks)

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based only on the provided document excerpts. If the excerpts don't contain the answer, say so."
                },
                {
                    "role": "user",
                    "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"
                }
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return {"error": f"Something went wrong calling the AI model: {str(e)}"}, 500

    return {
        "document_id": document_id,
        "question": question,
        "answer": answer,
        "chunks_used": len(relevant_chunks)
    }


if __name__ == "__main__":
    app.run(debug=True , port=5001)
