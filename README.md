# AlphaSentinel: Automated 10-K Discrepancy Detector

## Title
AlphaSentinel  
An Agentic RAG System for Financial Due Diligence

## Overview
AlphaSentinel is a specialized Quantitative Finance Agent designed to automate "Risk Arbitrage" due diligence. It uses a LangGraph workflow to cross-reference unstructured "sales" data (Earnings Call Transcripts) against legally binding "risk" data (SEC 10-K/10-Q Filings).

The agent extracts key forward-looking claims from company executives and autonomously verifies them against the company's official regulatory filings using semantic search and an LLM-based "Judge." The output is a "Trust Score" and a detailed discrepancy report, enabling analysts to identify when management optimism contradicts regulatory reality.

## Reason for picking up this project
This project was chosen to strictly align with the advanced requirements of the MAT496 course while simulating a real-world Quantitative Finance problem:

- **LangGraph State & Nodes:** The core logic is built as a state machine. The agent moves between "Extracting Claims," "Retrieving Evidence," and "Adjudicating Truth."

- **RAG (Retrieval Augmented Generation):** It uses advanced RAG techniques to index massive 10-K documents (100+ pages) and retrieve only the specific paragraphs relevant to a CEO's claim.

- **Alpha Generation:** Converting unstructured text data into a structured signal (Trust Score) that can be used for investment decision-making.

- **Deep Financial Analysis:** It automates a task that typically requires hours of human expert reading, demonstrating the power of LLMs in the financial domain.

## Video Summary Link
https://youtu.be/VNnaGP4YikU

## Plan
I plan to execute these steps to complete my project.

- [DONE] Environment Setup: Fork repo, setup venv, and install dependencies.  
- [DONE] Data Pipeline: Curate 10-K PDFs and Transcripts for analysis.  
- [DONE] Vector Database: Build RAG ingestion pipeline for 10-Ks.  
- [DONE] Node 1 - The Listener: LangGraph node to parse transcripts.  
- [DONE] Node 2 - The Auditor: Retrieval node to find evidence in 10-K.  
- [DONE] Node 3 - The Judge: Logic node to compare Claim vs. Evidence.  
- [DONE] Deployment: Streamlit UI construction.  
- [DONE] Video: Recording and submission.  

## Conclusion
This project successfully demonstrates the application of Agentic AI in Quantitative Finance. AlphaSentinel effectively utilizes a **LangGraph** state machine to orchestrate a complex workflow: extracting unstructured claims from executive transcripts, retrieving legally binding evidence via a **RAG pipeline** (ChromaDB), and adjudicating discrepancies using an LLM. 

I achieved the objective of transforming unstructured text into a structured "Risk Score," providing a deployable prototype for automated due diligence. The system effectively highlights the "Alpha" hidden in the gap between sales guidance and regulatory reality.
