from vectorstore import create_tables, store_embeddings, get_embeddings
from retriever import search_venues

def main():
    print("Using MPNet embeddings model...")

    try:
        embedding_model = get_embeddings()
    except Exception as e:
        print(f"Failed to initialize MPNet embedding model: {e}")
        return

    create_tables()
    store_embeddings(embedding_model)

    query = input("Enter your search query:").strip()
    results = search_venues(query, embedding_model)

    print("\nTop 5 venues found:")
    if isinstance(results, dict) and "context" in results:
        for venue_doc in results["context"]:
            metadata = venue_doc.metadata
            venue_id = metadata.get("venue_id", "N/A")
            name = metadata.get("name", "N/A")
            location = metadata.get("location", "N/A")
            print(f"ID: {venue_id}, Name: {name}, Location: {location}")
    else:
        print("No venues found.")
        if isinstance(results, dict):
            print("Error:", results.get("error", "Unknown error"))
        else:
            print("Unexpected result format:", results)

if __name__ == "__main__":
    main()
