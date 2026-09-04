import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Runtime RAG Generator", layout="wide")
st.title("⚡ Dynamic Runtime RAG Generator")

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Document Runtime Upload
st.sidebar.header("1. Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Select files to index (PDF, TXT, DOCX)", 
    accept_multiple_files=True,
    type=["pdf", "txt", "docx", "md"]
)

if st.sidebar.button("Build RAG Application"):
    if not uploaded_files:
        st.sidebar.error("Please upload at least one file.")
    else:
        files = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
        with st.spinner("Processing documents & building vector index..."):
            try:
                res = requests.post(f"{API_BASE_URL}/ingest", files=files)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.messages = []
                    st.sidebar.success(f"Success! Indexed {data['total_chunks_indexed']} chunks.")
                else:
                    st.sidebar.error(res.json().get("detail", "Ingestion failed."))
            except Exception as e:
                st.sidebar.error(f"Connection error: {e}")

# Main Chat Interface
st.header("2. Ask Grounded Questions")

if not st.session_state.session_id:
    st.info("👈 Upload documents in the sidebar and click **Build RAG Application** to begin.")
else:
    st.caption(f"Active RAG Session: `{st.session_state.session_id}`")

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle User Input
    if user_prompt := st.chat_input("Ask something about your uploaded documents..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving facts & generating response..."):
                payload = {
                    "session_id": st.session_state.session_id,
                    "question": user_prompt
                }
                res = requests.post(f"{API_BASE_URL}/query", json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("🔍 View Grounding Sources"):
                            for idx, src in enumerate(sources, 1):
                                st.write(f"**[{idx}] File:** {src['file']} | **Page:** {src['page']}")
                                st.caption(f"\"{src['content_snippet']}...\"")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = "Failed to fetch response."
                    st.error(err_msg)
