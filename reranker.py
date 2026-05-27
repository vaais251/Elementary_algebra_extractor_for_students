import sys
import numpy as np
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from hybrid_search import hybrid_retrieve

# Initialize the models
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def mmr_select(documents: list, cross_encoder_scores: list, top_k: int = 5, lambda_mult: float = 0.75) -> list:
    """
    Selects top_k documents from a candidate list using Maximal Marginal Relevance (MMR).
    
    Args:
        documents: A list of candidate documents.
        cross_encoder_scores: A list of raw scores predicted by the CrossEncoder for each document.
        top_k: The number of documents to select.
        lambda_mult: Diversity parameter between 0 (max diversity) and 1 (max relevance).
        
    Returns:
        A list of selected diverse documents.
    """
    if not documents:
        return []
    
    # Compute vector embeddings for all candidate documents
    doc_texts = [doc.page_content for doc in documents]
    doc_embeddings = np.array(embeddings.embed_documents(doc_texts))
    
    # Normalize the embeddings to unit vectors for easy cosine similarity computation
    norms = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
    # Avoid division by zero
    norms[norms == 0] = 1e-9
    norm_embeddings = doc_embeddings / norms
    
    # Normalize cross-encoder scores using min-max scaling (0 to 1)
    scores = np.array(cross_encoder_scores, dtype=float)
    min_score = np.min(scores)
    max_score = np.max(scores)
    if max_score > min_score:
        normalized_scores = (scores - min_score) / (max_score - min_score)
    else:
        # If all scores are equal, treat them all as 1.0
        normalized_scores = np.ones_like(scores)
        
    # Iteratively select top_k documents
    selected_indices = []
    unselected_indices = list(range(len(documents)))
    
    # Limit top_k to actual number of documents
    k = min(top_k, len(documents))
    
    # First pick: document with the highest normalized cross-encoder score
    first_pick = int(np.argmax(normalized_scores))
    selected_indices.append(first_pick)
    unselected_indices.remove(first_pick)
    
    while len(selected_indices) < k:
        best_mmr_score = -float('inf')
        best_idx = -1
        
        for idx in unselected_indices:
            # Calculate similarity to all selected documents
            # Since vectors are normalized, dot product is cosine similarity
            similarities = [np.dot(norm_embeddings[idx], norm_embeddings[sel_idx]) for sel_idx in selected_indices]
            max_sim_to_selected = max(similarities)
            
            # MMR formula
            mmr_score = (lambda_mult * normalized_scores[idx]) - ((1.0 - lambda_mult) * max_sim_to_selected)
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_idx = idx
                
        selected_indices.append(best_idx)
        unselected_indices.remove(best_idx)
        
    return [documents[idx] for idx in selected_indices]

def rerank_documents(cross_encoder_scores: list, documents: list, top_k: int = 5) -> list:
    """
    Reranks a list of retrieved documents by passing them into mmr_select
    using their cross-encoder scores.
    """
    if not documents:
        return []
        
    # Store cross-encoder scores in metadata for reference/printing
    for doc, score in zip(documents, cross_encoder_scores):
        if doc.metadata is None:
            doc.metadata = {}
        doc.metadata["cross_encoder_score"] = float(score)
        
    # Pass into mmr_select to get diverse list
    diverse_docs = mmr_select(documents, cross_encoder_scores, top_k=top_k)
    return diverse_docs

if __name__ == "__main__":
    # Reconfigure stdout for Windows environment (supports math symbols)
    sys.stdout.reconfigure(encoding='utf-8')
    
    query = "what is  Multi-Agent LLM Orchestration"
    print(f"Query: '{query}'")
    print("Retrieving candidate documents...")
    
    # Retrieve 10 candidate documents using hybrid search
    candidates = hybrid_retrieve(query, top_k=10)
    print(f"Retrieved {len(candidates)} candidates.")
    
    if not candidates:
        print("No candidates retrieved.")
    else:
        # Construct list of pairs for cross-encoder scoring
        pairs = [[query, doc.page_content] for doc in candidates]
        
        # Predict relevance scores using cross-encoder
        print("Scoring candidates with CrossEncoder...")
        scores = model.predict(pairs)
        
        print("\nReranking documents with MMR selection...")
        # Rerank and select top 5 using MMR
        diverse_docs = rerank_documents(scores, candidates, top_k=5)
        
        print(f"\n{'='*20} Top MMR Selected Diverse Results {'='*20}")
        for i, doc in enumerate(diverse_docs):
            score = doc.metadata.get("cross_encoder_score", "N/A")
            print(f"\n--- Result {i+1} (Cross-Encoder Score: {score:.4f}) ---")
            print(f"Source: {doc.metadata.get('source', 'unknown')} | Page: {doc.metadata.get('page', 'unknown')}")
            print("Content:")
            print(doc.page_content)
            print("-" * 50)
