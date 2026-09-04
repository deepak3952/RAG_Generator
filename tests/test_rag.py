import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from app.main import app
from app.core.vector_store import store_manager

client = TestClient(app)

def test_ingest_endpoint_no_files():
    """Test that submitting an ingestion request without files returns a 422 or 400 error."""
    response = client.post("/api/v1/ingest")
    assert response.status_code in [400, 422]

def test_query_endpoint_invalid_session():
    """Test querying a non-existent session returns 404."""
    payload = {
        "session_id": "non-existent-session-id",
        "question": "What is the capital of France?"
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 404
    assert "Invalid session_id" in response.json()["detail"]

@patch("app.core.vector_store.OpenAIEmbeddings")
@patch("app.core.rag_agent.ChatOpenAI")
def test_full_ingest_and_query_flow(mock_chat, mock_embeddings):
    """Test end-to-end flow: session creation, vector store setup, and querying."""
    # 1. Mock vector store initialization to prevent real API calls
    session_id = "test-session-123"
    docs = [Document(page_content="The key project deadline is October 15, 2026.", metadata={"source_filename": "plan.txt", "page": 1})]
    
    # Bypass OpenAI embeddings dependency during testing by initializing directly
    with patch.object(store_manager, "_embeddings", MagicMock()):
        with patch("langchain_community.vectorstores.FAISS.from_documents") as mock_faiss:
            mock_retriever = MagicMock()
            mock_retriever.invoke.return_value = docs
            mock_vectorstore = MagicMock()
            mock_vectorstore.as_retriever.return_value = mock_retriever
            mock_faiss.return_value = mock_vectorstore

            store_manager.create_session_store(session_id, docs)

    assert store_manager.session_exists(session_id) is True

    # 2. Query the active session
    with patch("app.core.rag_agent.rag_engine.chain.invoke") as mock_chain_invoke:
        mock_chain_invoke.return_value = "The project deadline is October 15, 2026 [Source: plan.txt, Page: 1]."
        
        payload = {
            "session_id": session_id,
            "question": "When is the deadline?"
        }
        
        response = client.post("/api/v1/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "October 15, 2026" in data["answer"]
        assert len(data["sources"]) > 0
        assert data["sources"][0]["file"] == "plan.txt"

