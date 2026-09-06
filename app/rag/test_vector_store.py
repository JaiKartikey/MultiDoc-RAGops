from ingest import ingest_document

def main():
    vector_store = ingest_document("data/company.txt")

    print("created Vector_Store")

    query =input("Ask Something!")

    results= vector_store.search(query, top_k =5)

    print("Search Results")

    for i, result in enumerate(results):
        print(f"result {i+1}")
        print(f"Score: {result['score']}")
        print(f"Chunk: {result['chunk']}")

if __name__ == "__main__":
    main()

