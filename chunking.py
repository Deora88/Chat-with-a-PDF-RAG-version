"""
Milestone 3 - Chunking

Splits a long piece of text into smaller overlapping chunks, so each chunk
is small enough and focused enough to produce a useful embedding.
"""


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks, measured in words.

    chunk_size: how many words per chunk
    overlap: how many words from the end of one chunk are repeated
             at the start of the next chunk
    """
    words = text.split()  # splits on whitespace, gives a list of words
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

        # move the window forward, but step back by `overlap` words
        # so the next chunk repeats the last `overlap` words of this one
        start += chunk_size - overlap

    return chunks
