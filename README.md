# ⚡ Dynamic Runtime RAG Generator Engine

> **Agentic Coding Assessment | Candidate Brief Solution**  
> A production-ready, dynamic Retrieval-Augmented Generation (RAG) system that accepts arbitrary documents at runtime, builds session-isolated vector indexes on the fly, and provides grounded answers with explicit citation attribution.

---

## 📋 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Key Features](#-key-features)
3. [Repository Structure](#-repository-structure)
4. [Prerequisites & Installation](#-prerequisites--installation)
5. [Running the Application](#-running-the-application)
6. [API Reference & Usage](#-api-reference--usage)
7. [Testing](#-testing)
8. [AI Agent Transcripts](#-ai-agent-transcripts)

---

## 🏗️ System Architecture

The application is structured into a dual-layer architecture: a **FastAPI** backend handling ingestion, vector stores, and agentic grounding logic, and a **Streamlit** frontend providing an intuitive user interface.

```
                    ┌─────────────────────────────────────────┐
                    │        Streamlit UI / Client            │
                    └────────────────────┬────────────────────┘
                                         │  HTTP / REST
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │          FastAPI Engine (main.py)       │
                    └────────────────────┬────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
                   ▼                                           ▼
  ┌─────────────────────────────────┐         ┌─────────────────────────────────┐
  │   Ingestion Pipeline            │         │   Session Vector Manager        │
  │  (ingestion.py)                 │         │  (vector_store.py)              │
  │  - PyPDF / Text / Docx Loaders   │         │  - Isolated FAISS Index per     │
  │  - Recursive Character Splitter │         │    session_id                    │
  └────────────────┬────────────────┘         │  - OpenAI Embeddings            │
                   │                          └────────────────┬────────────────┘
                   │ Pass Chunks                               │ Query Context
                   └─────────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────┐
                      │    Grounded RAG Agent Engine       │
                      │   (rag_agent.py)                   │
                      │   - Dynamic Context Formatting     │
                      │   - GPT-4o-mini Answer Generation  │
                      │   - Citation & Source Attribution  │
                      └────────────────────────────────────┘
```

---

## ✨ Key Features

* **Dynamic Ingestion at Runtime:** Upload `.pdf`, `.docx`, `.txt`, or `.md` files dynamically through the API/UI without server restarts or code changes.
* **Session Isolation:** Each runtime upload creates a unique `session_id` and isolated in-memory FAISS vector index, guaranteeing tenant/document privacy.
* **Groundedness & Strict Citation:** Prompting enforces strict groundedness—if the uploaded context does not contain the answer, the agent explicitly states so. Every answer includes precise source metadata (`filename` and `page`).
* **Format Agnostic:** Handles multi-document, heterogeneous file sets effortlessly.
* **Decoupled Architecture:** Clean separation between RESTful endpoints and interactive Web UI.

---

## 📁 Repository Structure

```text
rag-generator-assessment/
├── README.md                 # Complete documentation & setup guide
├── requirements.txt          # Python dependency specifications
├── .env.example              # Environment variables template
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI entry point & API routes
│   ├── ui.py                 # Streamlit client dashboard
│   └── core/
│       ├── __init__.py
│       ├── ingestion.py      # Multi-format document parser & text chunker
│       ├── rag_agent.py      # Agentic RAG engine with citation constraints
│       └── vector_store.py   # In-memory FAISS session vector store manager
├── tests/
│   ├── test_ingestion.py     # Ingestion & chunking unit tests
│   └── test_rag.py           # API integration & end-to-end RAG tests
└── transcripts/
    ├── claude_code_transcript.json  # Complete AI agent development transcript
    └── agent_summary.md             # Development log & methodology summary
```

---

## ⚙️ Prerequisites & Installation

### Requirements
* **Python:** 3.10 or higher
* **OpenAI API Key:** Required for embeddings (`text-embedding-3-small`) and completion (`gpt-4o-mini`).

### Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/deepak3952/RAG_Generator.git
   cd RAG_Generator
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and insert your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## 🚀 Running the Application

### Step 1: Start the FastAPI Backend Server
Launch the backend server using Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The REST API will be accessible at `http://localhost:8000`. Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

### Step 2: Start the Streamlit Frontend UI
In a separate terminal window (with virtualenv activated):
```bash
streamlit run app/ui.py
```
Open your browser at `http://localhost:8501`.

---

## 📡 API Reference & Usage

### 1. Ingest Documents (`POST /api/v1/ingest`)
Uploads document files, parses content, creates text chunks, and initializes a session vector store.

* **Request:** `multipart/form-data` containing one or more files in the `files` field.
* **Response Sample:**
  ```json
  {
    "status": "success",
    "session_id": "c9b1d2e3-4f56-7a89-b012-3456789abcde",
    "files_processed": ["financial_report.pdf", "product_specs.docx"],
    "total_chunks_indexed": 42
  }
  ```

### 2. Query Grounded RAG (`POST /api/v1/query`)
Executes an agent query against the document set stored for the given `session_id`.

* **Request Body (`application/json`):**
  ```json
  {
    "session_id": "c9b1d2e3-4f56-7a89-b012-3456789abcde",
    "question": "What were the key Q3 financial growth metrics?"
  }
  ```
* **Response Sample:**
  ```json
  {
    "session_id": "c9b1d2e3-4f56-7a89-b012-3456789abcde",
    "question": "What were the key Q3 financial growth metrics?",
    "answer": "Revenue increased by 18% YoY to $4.2M, driven primarily by enterprise SaaS subscriptions [Source: financial_report.pdf, Page: 3].",
    "sources": [
      {
        "file": "financial_report.pdf",
        "page": 3,
        "content_snippet": "In Q3, enterprise SaaS subscriptions saw accelerated growth, boosting total revenue by 18% YoY to reach $4.2M..."
      }
    ]
  }
  ```

---

## 🧪 Testing

Run unit and integration tests using `pytest`:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v
```

---

## 🤖 AI Agent Transcripts

In accordance with assessment submission requirements, the full execution logs and transcripts of the AI coding agents used during development are exported in the `transcripts/` directory.

* **Transcript File:** `transcripts/claude_code_transcript.json`
* **Agent Method Summary:** `transcripts/agent_summary.md`

To view or re-export agent session logs in Claude Code during active sessions:
```bash
/export
```
