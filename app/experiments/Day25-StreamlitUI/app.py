import os
import tempfile
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# =====================================
# Streamlit Page Configuration
# =====================================

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 RAG Chatbot")

st.caption(
    "Upload a PDF and chat with your document using Retrieval-Augmented Generation."
)

# =====================================
# Sidebar
# =====================================

with st.sidebar:

    st.header("⚙️ Configuration")

    st.success("Model: DeepSeek")

    st.success("Embedding: MiniLM")

    st.success("Vector Database: FAISS")

    st.success("Retriever: Top 3")

# =====================================
# Session State
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# =====================================
# Upload PDF
# =====================================

uploaded_file = st.file_uploader(
    "📄 Upload a PDF document",
    type=["pdf"]
)

# =====================================
# Build the RAG Pipeline
# =====================================

if (
    uploaded_file is not None
    and uploaded_file.name != st.session_state.pdf_name
):

    with st.spinner("⏳ Processing PDF..."):

        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

            tmp.write(uploaded_file.getbuffer())

            pdf_path = tmp.name

        # Load PDF
        loader = PyPDFLoader(pdf_path)

        documents = loader.load()

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(documents)

        # Create embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Create FAISS vector database
        vector_db = FAISS.from_documents(
            chunks,
            embeddings
        )

        # Create retriever
        retriever = vector_db.as_retriever(
            search_kwargs={"k": 8}
        )

        # Save retriever in Streamlit Session
        st.session_state.retriever = retriever

        # Save PDF name
        st.session_state.pdf_name = uploaded_file.name

        # Save chunks (useful later)
        st.session_state.chunks = chunks

        # Delete temporary PDF
        if os.path.exists(pdf_path):

            os.remove(pdf_path)

    st.success("✅ PDF processed successfully!")

    st.info(f"Chunks created : {len(chunks)}")

# =====================================
# Display Previous Messages
# =====================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =====================================
# Chat Input & Logic
# =====================================

question = st.chat_input("💬 Ask a question about your PDF...")

if question:

    # 🟢 Handled Summary check after receiving user question
    question_lower = question.lower()

    if "summarize" in question_lower or "summary" in question_lower:
        query_text = f"Give a detailed summary of the uploaded document.\n\nUser request: {question}"
    else:
        query_text = question

    # Display user message
    with st.chat_message("user"):

        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Check if PDF exists
    if st.session_state.retriever is None:

        answer = "⚠️ Please upload a PDF first."

    else:

        with st.spinner("🤖 Thinking..."):

            # Retrieve relevant chunks using modified query text
            docs = st.session_state.retriever.invoke(query_text)

            # 📌 Save Retrieved Docs in Session State
            st.session_state.last_docs = docs

            context = "\n\n".join(
                doc.page_content
                for doc in docs
            )

            # Prompt
            system_prompt = f"""
You are a helpful AI assistant using Retrieval-Augmented Generation (RAG).

Your job is to answer ONLY using the provided context.

Rules:
- Use the retrieved context as your main source.
- If the answer is clearly present, answer naturally.
- If the user asks for a summary, summarize the retrieved context.
- If the information is not present in the context, reply:
"I don't know based on the uploaded document."
- Never invent facts.

Retrieved Context:
{context}
"""

            messages = [

                {
                    "role": "system",
                    "content": system_prompt
                }

            ]

            # Add previous conversation
            for msg in st.session_state.messages:

                messages.append(msg)

            try:

                response = client.chat.completions.create(

                    model="deepseek/deepseek-chat-v3-0324",

                    messages=messages,

                    max_tokens=500

                )

                if response.choices:

                    answer = response.choices[0].message.content

                else:

                    answer = "No response received."

            except Exception as e:

                answer = f"❌ Error:\n\n{e}"

    # Display assistant answer
    with st.chat_message("assistant"):

        st.markdown(answer)

    st.session_state.messages.append(

        {

            "role": "assistant",

            "content": answer

        }

    )

# =====================================
# Sidebar Information
# =====================================

with st.sidebar:

    st.divider()

    if st.session_state.pdf_name:

        st.success(f"📄 {st.session_state.pdf_name}")

    if "chunks" in st.session_state:

        st.info(f"Chunks : {len(st.session_state.chunks)}")

# =====================================
# Clear Chat Button
# =====================================

if st.sidebar.button("🗑️ Clear Chat"):

    st.session_state.messages = []
    
    # Clean last_docs on clear chat if exists
    if "last_docs" in st.session_state:
        del st.session_state["last_docs"]

    st.rerun()

# =====================================
# Retrieved Chunks Viewer
# =====================================

if "last_docs" in st.session_state:

    with st.expander("📚 Retrieved Chunks"):

        for i, doc in enumerate(st.session_state.last_docs):

            st.markdown(f"### Chunk {i+1}")

            st.write(doc.page_content)

            st.divider()