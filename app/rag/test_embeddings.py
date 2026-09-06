from embeddings import create_embedding

def test_create_embedding():
    text = "RAG is a powerful technique for building AI applications that can answer questions based on a large corpus of documents."
    embedding =create_embedding(text)

    print ("Created embedding:")
    print("length of embedding:", len(embedding))

    print("first 10 values of embedding:", embedding[:10])


if __name__ == "__main__":
    test_create_embedding()