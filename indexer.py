import sys
from chunking import get_chunked_docs
from langchain_elasticsearch import ElasticsearchStore, BM25Strategy

def main():
    # Reconfigure stdout for Windows math symbols
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Get the chunked documents
    print("Fetching chunked documents...")
    docs = get_chunked_docs()
    
    # 2. Connect to Elasticsearch and index the documents
    print("Connecting to Elasticsearch and indexing documents...")
    # Initialize ElasticsearchStore with BM25 retrieval strategy
    store = ElasticsearchStore.from_documents(
        docs,
        es_url="http://localhost:9200",
        index_name="edumaestro-bm25",
        strategy=BM25Strategy()
    )
    print("Indexing complete.")
    
    # 3. Test search using BM25
    query = "EduMaestro solves both problems simultaneously"
    print(f"\nSearching for '{query}'...")
    
    results = store.similarity_search(query, k=1)
    
    if results:
        print("\n--- Top Result ---")
        print("Metadata:", results[0].metadata)
        print("Content:")
        print(results[0].page_content)
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
