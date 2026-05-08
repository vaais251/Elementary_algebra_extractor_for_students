import sys
from chunking import get_chunked_docs
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def main():
    # Reconfigure stdout for Windows math symbols
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Fetch chunked documents
    print("Fetching chunked documents...")
    docs = get_chunked_docs()
    
    # 2. Initialize HuggingFace embeddings
    print("Initializing HuggingFace embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 3. Create FAISS index
    print("Creating FAISS index...")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # 4. Save index locally
    index_path = "faiss_index"
    print(f"Saving FAISS index locally to '{index_path}'...")
    vectorstore.save_local(index_path)
    print("Index saved successfully.")
    
    # 5. Semantic test search
    query = "What formula relates the sides of a right triangle?"
    print(f"\nRunning semantic search for query: '{query}'")
    
    results = vectorstore.similarity_search(query, k=1)
    
    if results:
        print("\n--- Top Result ---")
        print("Metadata:", results[0].metadata)
        print("Content:")
        print(results[0].page_content)
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
