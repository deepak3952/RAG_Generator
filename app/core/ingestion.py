import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}

def parse_and_chunk_file(file_bytes: bytes, filename: str) -> List[Document]:
    """Parses arbitrary file formats at runtime and splits them into chunks."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Supported: {SUPPORTED_EXTENSIONS}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(tmp_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(tmp_path, encoding="utf-8")
        elif ext == ".docx":
            loader = UnstructuredWordDocumentLoader(tmp_path)
        
        raw_docs = loader.load()
        
        # Preserve original source metadata
        for doc in raw_docs:
            doc.metadata["source_filename"] = filename

        # Dynamic chunking with standard overlap window
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        return text_splitter.split_documents(raw_docs)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
