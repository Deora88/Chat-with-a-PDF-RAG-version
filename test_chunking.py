from chunking import chunk_text

sample_text = "word " * 1200  # simulate 1200 words

chunks = chunk_text(sample_text, chunk_size=500, overlap=50)

print(f"Total words: 1200")
print(f"Number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    word_count = len(chunk.split())
    print(f"Chunk {i+1}: {word_count} words")
