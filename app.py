import streamlit as st
import os
import time
from graph import app as agent_app  # Import the agent we built

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AlphaSentinel | AI Due Diligence",
    page_icon="🛡️",
    layout="wide"
)

# --- CSS STYLING (Dark Mode / Financial Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #FAFAFA;
    }
    .stAlert {
        background-color: #262730;
        border: 1px solid #4B5563;
    }
    h1, h2, h3 {
        color: #00ADB5 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .metric-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00ADB5;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=80)
    st.title("AlphaSentinel")
    st.caption("v1.0.0 | Quant Risk Agent")
    
    st.markdown("---")
    
    st.subheader(" Data Source")
    st.info("Loaded: Tesla (TSLA) Q3 2023")
    
    with st.expander("System Status"):
        if os.path.exists("data/sec_filing.pdf"):
            st.success("10-K Filing Index (Ready)")
        else:
            st.error("10-K Missing")
            
        if os.path.exists("data/transcript.txt"):
            st.success("Earnings Transcript (Ready)")
        else:
            st.error("Transcript Missing")

    st.markdown("---")
    st.markdown("### Logic Flow")
    st.text("1. Ingest Transcript")
    st.text("2. Extract Claims (LLM)")
    st.text("3. Retrieve Evidence (RAG)")
    st.text("4. Judge & Score (GPT-4)")

# --- MAIN PAGE ---
st.title("AlphaSentinel Dashboard")
st.markdown("### Automated Discrepancy Detection & Risk Analysis")

# Run Button
if st.button("RUN ANALYSIS", type="primary"):
    
    # 1. Progress Bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🔍 Node 1: Reading Transcript & Extracting Claims...")
    progress_bar.progress(25)
    
    # 2. Run the Agent
    try:
        # Load Transcript
        with open("data/transcript.txt", "r", encoding="utf-8") as f:
            transcript_text = f.read()
            
        inputs = {"transcript_text": transcript_text, "claims": [], "verification_results": []}
        
        # Invoke Graph
        result = agent_app.invoke(inputs)
        
        progress_bar.progress(75)
        status_text.text("⚖️ Node 2 & 3: Cross-referencing 10-K & Adjudicating...")
        time.sleep(1) # Visual pause
        progress_bar.progress(100)
        status_text.text("Analysis Complete.")
        
        # 3. Display Results
        st.divider()
        st.subheader("Audit Report")
        
        results = result['verification_results']
        
        # Calculate Average Risk
        risk_scores = []
        for r in results:
            # Extract number from "Risk Score | Verdict" string roughly
            try:
                score = int([int(s) for s in r['analysis'].split() if s.isdigit()][0])
                risk_scores.append(score)
            except:
                pass
        
        avg_risk = sum(risk_scores)/len(risk_scores) if risk_scores else 0
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Claims Analyzed", len(results))
        with col2:
            st.metric("Risk Factor Found", f"{len([r for r in risk_scores if r > 5])} High Risk")
        with col3:
            st.metric("Overall Trust Score", f"{10 - avg_risk:.1f}/10")

        # Detailed Cards
        for i, item in enumerate(results):
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Claim #{i+1}</h4>
                    <p style="font-size: 1.1em; font-weight: bold;">"{item['claim']}"</p>
                    <hr>
                    <p style="color: #9CA3AF; font-size: 0.9em;">🔎 <b>Evidence (10-K):</b> ...{item['evidence_snippet']}...</p>
                    <p style="color: #FCD34D;">⚖️ <b>Verdict:</b> {item['analysis']}</p>
                </div>
                <br>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Analysis Failed: {e}")

else:
    st.info("Click 'RUN ANALYSIS' to start the due diligence agent.")