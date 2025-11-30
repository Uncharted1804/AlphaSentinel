import os
from typing import TypedDict, List
from dotenv import load_dotenv

# LangChain / LangGraph Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# --- THE FIX IS HERE: Import directly from pydantic ---
from pydantic import BaseModel, Field 
from langgraph.graph import StateGraph, END

# Load API Keys
load_dotenv()

# --- CONFIGURATION ---
PDF_PATH = "data/sec_filing.pdf"
TRANSCRIPT_PATH = "data/transcript.txt"
MODEL_NAME = "gpt-4o"  

# --- 1. DEFINE THE STATE ---
class AgentState(TypedDict):
    transcript_text: str       
    claims: List[str]          
    verification_results: List[dict] 

# --- 2. SETUP THE RAG ENGINE ---
print("Initializing Vector Database... (This may take a moment)")
embeddings = OpenAIEmbeddings()

# Load and chunk the 10-K PDF
if os.path.exists(PDF_PATH):
    try:
        loader = PyPDFLoader(PDF_PATH)
        docs = loader.load()
        # Text splitting (chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Create the Vector Store
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()
        print("RAG System Ready: PDF Indexed.")
    except Exception as e:
        print(f" Error loading PDF: {e}")
        vectorstore = None
else:
    print(f"ERROR: Could not find {PDF_PATH}. Make sure the file exists in the 'data' folder.")
    vectorstore = None

# --- 3. DEFINE THE NODES ---

def extract_claims_node(state: AgentState):
    print("--- NODE 1: Extracting Claims ---")
    transcript = state['transcript_text']
    
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a financial analyst. Read the following earnings call transcript.
        Extract the top 3 most important "Forward Looking Statements" or aggressive claims made by the executives.
        Focus on specific numbers, growth targets, or product timelines.
        
        Return ONLY a python list of strings. Example: ["We expect 50% growth", "Cybertruck delivery in Q3"]
        
        TRANSCRIPT:
        {text}
        """
    )
    
    chain = prompt | llm
    # Limit text to first 15k chars to fit context window if transcript is huge
    response = chain.invoke({"text": transcript[:15000]}) 
    
    # Cleaning the output to get a clean list
    clean_content = response.content.strip()
    # Simple cleanup to handle if LLM returns markdown code blocks
    if "```" in clean_content:
        clean_content = clean_content.split("```")[1].replace("python", "").replace("json", "")
    
    # Convert string representation of list to actual list
    try:
        import ast
        claims_list = ast.literal_eval(clean_content)
        if not isinstance(claims_list, list):
            claims_list = [clean_content]
    except:
        # Fallback if parsing fails
        claims_list = [clean_content]
    
    return {"claims": claims_list}

def verify_claims_node(state: AgentState):
    print("--- NODE 2: Verifying Claims against 10-K ---")
    claims = state['claims']
    results = []
    
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    
    if not vectorstore:
        return {"verification_results": [{"error": "No PDF loaded"}]}

    for claim in claims:
        # A. Retrieve Evidence
        relevant_docs = retriever.invoke(claim)
        evidence_text = " ".join([d.page_content for d in relevant_docs[:2]]) 
        
        # B. Compare Claim vs Evidence
        prompt = ChatPromptTemplate.from_template(
            """
            You are a strict compliance auditor.
            
            CLAIM MADE BY CEO: "{claim}"
            
            EVIDENCE FROM SEC FILING (10-K):
            "{evidence}"
            
            Task:
            1. Does the evidence support, contradict, or add risk context to the claim?
            2. Assign a "Risk Score" from 1 (Safe) to 10 (High Discrepancy).
            3. Write a short verdict.
            
            Return format: Risk Score | Verdict
            """
        )
        
        chain = prompt | llm
        response = chain.invoke({"claim": claim, "evidence": evidence_text})
        
        results.append({
            "claim": claim,
            "evidence_snippet": evidence_text[:200] + "...",
            "analysis": response.content
        })
        
    return {"verification_results": results}

# --- 4. BUILD THE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("extract_claims", extract_claims_node)
workflow.add_node("verify_claims", verify_claims_node)

workflow.set_entry_point("extract_claims")
workflow.add_edge("extract_claims", "verify_claims")
workflow.add_edge("verify_claims", END)

app = workflow.compile()

# --- 5. EXECUTION FUNCTION ---
def run_analysis():
    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"Error: {TRANSCRIPT_PATH} not found.")
        return
        
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcript_text = f.read()
        
    inputs = {"transcript_text": transcript_text, "claims": [], "verification_results": []}
    
    print("Starting AlphaSentinel Agent...")
    result = app.invoke(inputs)
    
    print("\n\n====== FINAL REPORT ======")
    for res in result['verification_results']:
        print(f"\n CLAIM: {res.get('claim')}")
        print(f" VERDICT: {res.get('analysis')}")
        print("-" * 60)

if __name__ == "__main__":
    run_analysis()