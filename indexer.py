import sys
import pickle
from chunking import get_chunked_docs
from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer for BM25."""
    return text.lower().split()

def main():
    # Reconfigure stdout for Windows math symbols
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Get the chunked documents
    print("Fetching chunked documents...")
    docs = get_chunked_docs()
    
    # 2. Tokenize all document contents for BM25
    print("Tokenizing documents for BM25...")
    corpus = [tokenize(doc.page_content) for doc in docs]
    
    # 3. Build the BM25 index
    print("Building BM25 index...")
    bm25 = BM25Okapi(corpus)
    
    # 4. Save the BM25 index and documents to disk
    index_path = "bm25_index.pkl"
    print(f"Saving BM25 index to '{index_path}'...")
    with open(index_path, "wb") as f:
        pickle.dump({"bm25": bm25, "documents": docs}, f)
    print("Index saved successfully.")
    
    # 5. Test search using BM25
    query = "EduMaestro solves both problems simultaneously"
    print(f"\nSearching for '{query}'...")
    
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    
    # Get the top result
    top_idx = scores.argsort()[-1]
    
    print("\n--- Top Result ---")
    print("Metadata:", docs[top_idx].metadata)
    print("Content:")
    print(docs[top_idx].page_content)

if __name__ == "__main__":
    main()
