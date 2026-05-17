import sys
from langchain_elasticsearch import ElasticsearchStore, BM25Strategy
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def rrf_fusion(bm25_docs, dense_docs, k=60):
    """
    Computes the Reciprocal Rank Fusion score for documents retrieved from two different methods.
    """
    rrf_scores = {}
    doc_lookup = {}
    
    # Process BM25 documents
    for rank, doc in enumerate(bm25_docs):
        # We use page_content as a unique identifier for simplicity
        key = doc.page_content
        doc_lookup[key] = doc
        if key not in rrf_scores:
            rrf_scores[key] = 0.0
        rrf_scores[key] += 1.0 / (k + rank + 1)
        
    # Process Dense documents
    for rank, doc in enumerate(dense_docs):
        key = doc.page_content
        doc_lookup[key] = doc
        if key not in rrf_scores:
            rrf_scores[key] = 0.0
        rrf_scores[key] += 1.0 / (k + rank + 1)
        
    # Sort keys by their RRF score in descending order
    sorted_keys = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Return sorted documents
    return [doc_lookup[key] for key in sorted_keys]

def hybrid_retrieve(query, top_k=5):
    bm25_docs = []
    # Initialize BM25 Retriever with a graceful connection check
    try:
        es_store = ElasticsearchStore(
            es_url="http://localhost:9200",
            index_name="edumaestro-bm25",
            strategy=BM25Strategy()
        )
        print("Retrieving from BM25 (Elasticsearch)...")
        bm25_docs = es_store.similarity_search(query, k=10)
    except Exception as e:
        print(f"\n[Warning] Could not connect to Elasticsearch at http://localhost:9200.")
        print(f"          Detail: {e}")
        print("          Falling back to Dense Search (FAISS) only.\n")

    # Initialize Dense Retriever
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    faiss_store = FAISS.load_local(
        "faiss_index", 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    print("Retrieving from Dense (FAISS)...")
    dense_docs = faiss_store.similarity_search(query, k=10)
    
    if not bm25_docs:
        print("Returning FAISS results directly (no BM25 results available).")
        return dense_docs[:top_k]
    
    # Fuse results using RRF
    print("Applying Reciprocal Rank Fusion (RRF)...")
    fused_docs = rrf_fusion(bm25_docs, dense_docs, k=60)
    
    return fused_docs[:top_k]

def main():
    # Reconfigure stdout for Windows math symbols
    sys.stdout.reconfigure(encoding='utf-8')
    
    query = "Two persistent problems define the current landscape of AI-assisted self-study:"
    print(f"Hybrid Search Query: '{query}'\n")
    
    # Fetch top 3 fused results
    top_docs = hybrid_retrieve(query, top_k=3)
    
    print(f"\n{'='*20} Top 3 Fused Results {'='*20}")
    for i, doc in enumerate(top_docs):
        print(f"\n--- Result {i+1} ---")
        print("Metadata:", doc.metadata)
        print("Content:")
        print(doc.page_content)

if __name__ == "__main__":
    main()
