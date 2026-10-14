import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def display_sources(sources):
    if not sources:
        st.caption("No source references were returned.")
        return

    for index, source in enumerate(sources, start=1):
        filename = source.get("source", "Unknown file")
        page = source.get("page")
        score = source.get("score")

        page_text = f" · Page {page}" if page is not None else ""
        score_text = f"{score:.3f}" if isinstance(score, (int, float)) else "N/A"

        st.markdown(
            f"**{index}. {filename}**{page_text}\n\nRelevance score: `{score_text}`"
        )


st.set_page_config(
    page_title="DocMind | Research Assistant", page_icon="📘", layout="wide"
)

st.markdown(
    """
<style>
    /* Overall application */
    .stApp {
        background: #0B1120;
        color: #E5E7EB;
    }

    /* Main content spacing */
    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263247;
    }

    /* Headings */
    h1, h2, h3 {
        color: #F8FAFC !important;
        letter-spacing: -0.5px;
    }

    /* Supporting text */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #94A3B8 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #2563EB;
        color: white;
        border: 1px solid #3B82F6;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: #1D4ED8;
        border-color: #60A5FA;
        color: white;
    }

    /* Text input */
    [data-testid="stChatInput"] {
        border-radius: 14px;
    }

    [data-testid="stChatInput"] textarea {
        color: #F8FAFC;
    }

    /* Expandable source sections */
    [data-testid="stExpander"] {
        background: #111827;
        border: 1px solid #263247;
        border-radius: 12px;
    }

    /* Horizontal dividers */
    hr {
        border-color: #263247;
    }

    /* Uploaded file area */
    [data-testid="stFileUploader"] {
        background: #111827;
        border-radius: 12px;
    }

    /* Keep links visible against the dark background */
    a {
        color: #60A5FA !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


st.title("📘 DocMind")
st.caption("Your AI-powered document research assistant")
st.write(
    "Upload a document, ask questions, and explore answers "
    "grounded in relevant passages."
)

st.divider()

# Session state keeps the UI's document status and chat history.
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: upload documents.
with st.sidebar:
    st.header("📂 Your Documents")

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        if st.button("Process Document", use_container_width=True):
            try:
                with st.spinner("Processing document..."):
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        },
                        timeout=120,
                    )

                if response.ok:
                    result = response.json()
                    st.session_state.document_uploaded = True
                    st.session_state.uploaded_filename = result["filename"]
                    st.session_state.messages = []

                    st.success("Document processed successfully!")
                    st.write(f"**File:** {result['filename']}")
                    st.write(f"**Chunks:** {result['chunks_created']}")
                else:
                    st.error(response.json().get("detail", "Upload failed."))

            except requests.RequestException:
                st.error("Could not connect to the API. Make sure FastAPI is running.")

    if st.session_state.document_uploaded:
        st.success("Document ready")
        st.caption(st.session_state.uploaded_filename)

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# Main chat area.
st.subheader("💬 Ask your document")

if not st.session_state.document_uploaded:
    st.info("Upload and process a document using the sidebar to get started.")
else:
    # Display previous messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("📚 Sources"):
                    display_sources(message["sources"])

            if message.get("passages"):
                with st.expander("🔎 Retrieved passages"):
                    for index, passage in enumerate(message["passages"], start=1):
                        with st.expander(f"Passage {index}"):
                            st.write(passage)

    question = st.chat_input("Ask a question about your document...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching the document and generating an answer..."):
                try:
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question, "top_k": 3},
                        timeout=180,
                    )

                    if response.ok:
                        result = response.json()
                        answer = result["answer"]
                        sources = result.get("sources", [])
                        passages = [
                            item["text"]
                            for item in result.get("retrieved_passages", [])
                        ]

                        st.markdown(answer)

                        if sources:
                            with st.expander("📚 Sources"):
                                display_sources(sources)

                        if passages:
                            with st.expander("🔎 Retrieved passages"):
                                for index, passage in enumerate(passages, start=1):
                                    with st.expander(f"Passage {index}"):
                                        st.write(passage)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                                "passages": passages,
                            }
                        )
                    else:
                        detail = response.json().get(
                            "detail", "Question request failed."
                        )
                        st.error(detail)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": f"Error: {detail}"}
                        )

                except requests.RequestException:
                    st.error(
                        "Could not connect to the API. Check that FastAPI is running."
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "Unable to reach the DocMind API.",
                        }
                    )
