from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.vector_store import store_manager

SYSTEM_PROMPT = """You are an agentic RAG assistant. Your objective is to answer user questions using strictly the context provided below.

RULES FOR GROUNDEDNESS:
1. Answer ONLY using the provided retrieved context.
2. If the answer cannot be directly derived from the context, explicitly respond with: "I cannot find sufficient information in the provided documents to answer this question."
3. Cite sources in your answer using format: [Source: <filename>, Page: <page_number>] where available.

Context:
{context}

Question:
{question}
"""

class RAGAgentEngine:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def query_session(self, session_id: str, question: str) -> Dict[str, Any]:
        retriever = store_manager.get_retriever(session_id)
        retrieved_docs = retriever.invoke(question)

        # Context Formatting
        formatted_context = ""
        sources = []
        for i, doc in enumerate(retrieved_docs, start=1):
            fn = doc.metadata.get("source_filename", "Unknown")
            page = doc.metadata.get("page", "N/A")
            sources.append({"file": fn, "page": page, "content_snippet": doc.page_content[:150]})
            formatted_context += f"\n--- Document Snippet {i} [File: {fn}, Page: {page}] ---\n{doc.page_content}\n"

        # Answer Generation
        answer = self.chain.invoke({
            "context": formatted_context,
            "question": question
        })

        return {
            "answer": answer,
            "retrieved_sources": sources,
            "chunks_retrieved_count": len(retrieved_docs)
        }

rag_engine = RAGAgentEngine()

