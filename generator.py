import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

class TutorResponse(BaseModel):
    answer: str = Field(description="The direct explanation based strictly on the evidence passages.")
    citations: List[int] = Field(description="The IDs of the passages used to formulate the answer.")
    worked_solution: Optional[str] = Field(None, description="Step-by-step math solution, or null if not applicable.")
    lesson_outline: str = Field(description="A brief 5-minute lesson plan.")

# Initialize the LLM with temperature 0 to minimize hallucinations
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.environ.get("GOOGLE_API_KEY")
)

# Bind the structured output to force the response format
structured_llm = llm.with_structured_output(TutorResponse)

# Create a ChatPromptTemplate with the exact required system message
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an educational tutor. Answer ONLY using the provided evidence passages. If the passages do not contain sufficient information, output 'Insufficient evidence' in the answer field. Cite passage IDs inline."),
    ("human", "Query: {query}\n\nEvidence:\n{evidence}")
])

def generate_tutor_response(query: str, evidence: str) -> TutorResponse:
    """
    Synthesizes a final answer using Gemini 1.5 Flash based strictly on evidence passages,
    enforcing a structured output.
    
    Args:
        query (str): The user's query.
        evidence (str): The retrieved evidence passages.
        
    Returns:
        TutorResponse: The structured tutor response object.
    """
    chain = prompt | structured_llm
    return chain.invoke({"query": query, "evidence": evidence})

if __name__ == "__main__":
    test_query = "How do I solve x^2 - 5x + 6 = 0?"
    mock_evidence = (
        "[ID: 1] To solve a quadratic equation by factoring, find two numbers that multiply to the "
        "constant term and add to the linear coefficient. For x^2 - 5x + 6 = 0, the constant term is 6 "
        "and the linear coefficient is -5. The numbers -2 and -3 multiply to 6 and add to -5. "
        "Therefore, the equation factors as (x - 2)(x - 3) = 0, which gives the solutions x = 2 and x = 3."
    )
    
    print("Sending request to Gemini model...")
    try:
        response = generate_tutor_response(test_query, mock_evidence)
        print("\nResulting Structured Tutor Response:")
        try:
            print(response.model_dump_json(indent=2))
        except AttributeError:
            import json
            print(json.dumps(response.dict(), indent=2))
    except Exception as e:
        print(f"\nError invoking Gemini model: {e}")
        print("\n[NOTE] If you see a PERMISSION_DENIED/403 or 404 error, please check that GOOGLE_API_KEY in your .env file is valid and active.")
