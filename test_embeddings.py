from sentence_transformers import SentenceTransformer

# Load the embedding model (downloads it the first time you run this)
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "Muscle spindles detect changes in muscle length.",
    "Golgi tendon organs sense tension in tendons.",
    "The stock market closed higher today."
]

embeddings = model.encode(sentences)

print("Shape of embeddings:", embeddings.shape)
print("First 5 numbers of embedding 1:", embeddings[0][:5])

# Compare similarity: sentence 1 & 2 should be MORE similar to each other
# than either is to sentence 3 (unrelated topic)
from sentence_transformers import util

sim_1_2 = util.cos_sim(embeddings[0], embeddings[1])
sim_1_3 = util.cos_sim(embeddings[0], embeddings[2])

print("\nSimilarity between sentence 1 & 2 (both about muscles/tendons):", sim_1_2.item())
print("Similarity between sentence 1 & 3 (unrelated topics):", sim_1_3.item())
