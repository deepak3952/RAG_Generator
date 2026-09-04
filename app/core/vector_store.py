import uuid
from typing import Dict, List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

class SessionVectorStoreManager:
    """Manages isolated, in-memory vector stores indexed by session/tenant ID."""
    
    def __init__(self):
        self._stores: Dict[str, FAISS] = {}
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def create_session_store(self, session_id: str, documents: List[Document]) -> int:
        """Builds an isolated vector store for a specific user runtime session."""
        if not documents:
            raise ValueError("No documents provided for indexing.")
            
        vector_store = FAISS.from_documents(documents, self._embeddings)
        self._stores[session_id] = vector_store
        return len(documents)

    def get_retriever(self, session_id: str, k: int = 4):
        """Returns retriever handle for session."""
        if session_id not in self._stores:
            raise KeyError(f"Session '{session_id}' not found. Upload documents first.")
        return self._stores[session_id].as_retriever(search_kwargs={"k": k})

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._stores

# Global Singleton Manager
store_manager = SessionVectorStoreManager()

