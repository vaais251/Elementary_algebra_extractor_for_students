import re
from langchain_community.document_loaders import PyMuPDFLoader

def clean_text(text: str) -> str:
    # Remove standalone page numbers (e.g., just a number on a line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove headers assuming they start with "Header:"
    text = re.sub(r'^\s*Header:.*$', '', text, flags=re.MULTILINE)
    
    # Clean up excess whitespace without removing structure
    # Multiple newlines to two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def main():
    pdf_path = "sample_math.pdf"
    
    print(f"Loading {pdf_path}...")
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    
    print(f"Loaded {len(docs)} pages.")
    
    for i, doc in enumerate(docs):
        print(f"\n{'='*20} Page {i+1} {'='*20}")
        print("--- Original Metadata ---")
        print(doc.metadata)
        
        cleaned_content = clean_text(doc.page_content)
        
        print("\n--- Cleaned Content ---")
        print(cleaned_content)
        print("="*48)

if __name__ == "__main__":
    main()
