import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.core.ingestion import parse_and_chunk_file
from app.core.vector_store import store_manager
from app.core.rag_agent import rag_engine

app = FastAPI(title="Runtime RAG Generator API", version="1.0.0")

class QueryRequest(BaseModel):
    session_id: str
    question: str

class QueryResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: List[dict]

@app.post("/api/v1/ingest")
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Accepts dynamic files at runtime, parses them, and indexes them in an isolated session."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
        
    session_id = str(uuid.uuid4())
    all_chunks = []

    for file in files:
        try:
            content = await file.read()
            chunks = parse_and_chunk_file(content, file.filename)
            all_chunks.extend(chunks)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing {file.filename}: {str(e)}")

    chunk_count = store_manager.create_session_store(session_id, all_chunks)

    return {
        "status": "success",
        "session_id": session_id,
        "files_processed": [f.filename for f in files],
        "total_chunks_indexed": chunk_count
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(payload: QueryRequest):
    """Executes grounded agent query over session-indexed knowledge base."""
    if not store_manager.session_exists(payload.session_id):
        raise HTTPException(status_code=404, detail="Invalid session_id or session expired.")

    try:
        result = rag_engine.query_session(payload.session_id, payload.question)
        return QueryResponse(
            session_id=payload.session_id,
            question=payload.question,
            answer=result["answer"],
            sources=result["retrieved_sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
