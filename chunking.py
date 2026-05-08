import re
import sys
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def clean_text(text: str) -> str:
    # Remove standalone page numbers (e.g., just a number on a line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove headers assuming they start with "Header:"
    text = re.sub(r'^\s*Header:.*$', '', text, flags=re.MULTILINE)
    
    # Clean up excess whitespace without removing structure
    # Multiple newlines to two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def get_chunked_docs() -> list[Document]:
    pdf_path = "sample_math.pdf"
    
    print(f"Loading {pdf_path}...")
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    
    # Clean the page content before splitting
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
        
    print(f"Loaded and cleaned {len(docs)} pages.")
    
    # Initialize the RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    
    # Split the documents into chunks
    chunked_docs = text_splitter.split_documents(docs)
    
    print(f"Split into {len(chunked_docs)} chunks.")
    
    # Inject custom metadata
    custom_metadata = {
        "doc_type": "textbook", 
        "grade_level": 10, 
        "topic_cluster": "Algebra", 
        "difficulty_score": 0.5
    }
    
    for chunk in chunked_docs:
        # Update the metadata dictionary
        chunk.metadata.update(custom_metadata)
        
    return chunked_docs

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    docs = get_chunked_docs()
    
    for i, chunk in enumerate(docs):
        # Print only the first 2 chunks
        if i < 2:
            print(f"\n{'='*20} Chunk {i+1} {'='*20}")
            print("--- Metadata ---")
            print(chunk.metadata)
            print("\n--- Content ---")
            print(chunk.page_content)
            print("="*48)
