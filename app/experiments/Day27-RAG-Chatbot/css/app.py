import os
import tempfile
import time
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ==========================================
# Load Environment Variables & OpenAI Client
# ==========================================
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ==========================================
# Streamlit Page Configuration
# ==========================================
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Theme & Session State Initialization
# ==========================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "chats" not in st.session_state:
    st.session_state.chats = [{"id": 1, "title": "New Chat", "messages": []}]

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = 1

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "chunks" not in st.session_state:
    st.session_state.chunks = []

def get_current_messages():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            return chat["messages"]
    return []

def generate_chat_title(first_question):
    try:
        res = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[
                {"role": "system", "content": "Generate a concise 2-4 word title summarizing the user prompt. Do not use quotes or markdown."},
                {"role": "user", "content": first_question}
            ],
            max_tokens=10
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return first_question[:20]

# ==========================================
# Custom CSS (Push Sidebar Content to Top)
# ==========================================
def load_css():
    if st.session_state.dark_mode:
        bg = "#111827"
        txt = "#FFFFFF"
        sb = "#1F2937"
        active_btn = "#374151"
        github_icon_color = "#FFFFFF"
    else:
        bg = "#FFFFFF"
        txt = "#111827"
        sb = "#F8FAFC"
        active_btn = "#E2E8F0"
        github_icon_color = "#111827"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background-color: {bg};
        color: {txt};
    }}
    
    /* Fix Sidebar Padding to align content at the VERY TOP */
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem !important;
        background-color: {sb};
    }}
    
    section[data-testid="stSidebar"] h1 {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {sb};
        border-right: 1px solid #E5E7EB;
        display: block !important;
    }}
    
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    button[kind="primary"] {{
        background-color: {active_btn} !important;
        color: {txt} !important;
        border: 1px solid #CBD5E1 !important;
    }}

    .sidebar-footer {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 12px;
        margin-top: 15px;
        font-size: 13px;
        color: #64748B;
        border-top: 1px solid #E2E8F0;
    }}

    .sidebar-footer a {{
        color: {github_icon_color};
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        transition: opacity 0.2s ease;
    }}

    .sidebar-footer a:hover {{
        opacity: 0.7;
    }}
    
    footer {{
        visibility: hidden;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# ==========================================
# Main Title Header
# ==========================================
st.markdown(
"""
# 🤖 AI Research Assistant

Chat with your PDF documents using Retrieval-Augmented Generation.
"""
)

# ==========================================
# Sidebar UI & Controls
# ==========================================
with st.sidebar:
    st.markdown(
        """
        # 🤖 AI Research Assistant
        Your intelligent PDF assistant.
        """
    )

    st.divider()

    if st.button("➕ New Chat", use_container_width=True):
        new_id = len(st.session_state.chats) + 1
        st.session_state.chats.append({"id": new_id, "title": f"Chat {new_id}", "messages": []})
        st.session_state.active_chat_id = new_id
        if "last_docs" in st.session_state:
            del st.session_state["last_docs"]
        st.rerun()

    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Supported format: PDF"
    )

    st.markdown("<p style='font-size:12px; font-weight:700; color:#94A3B8; margin-top:15px; margin-bottom:5px;'>RECENTS</p>", unsafe_allow_html=True)
    
    for chat in reversed(st.session_state.chats):
        is_active = (chat["id"] == st.session_state.active_chat_id)
        btn_label = f"💬 {chat['title']}"
        if st.button(btn_label, key=f"chat_btn_{chat['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.active_chat_id = chat["id"]
            st.rerun()

    st.divider()

    dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    current_messages = get_current_messages()
    conversation = ""
    for msg in current_messages:
        conversation += f"{msg['role'].capitalize()} :\n{msg['content']}\n\n"

    st.download_button(
        label="⬇ Download Chat",
        data=conversation,
        file_name="conversation.txt",
        mime="text/plain",
        use_container_width=True
    )

    github_svg = """
    <svg height="16" width="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
    </svg>
    """
    st.markdown(
        f"""
        <div class="sidebar-footer">
            <span>By <b>Maram Elhadj</b></span>
            <a href="https://github.com/maram-el-hadj" target="_blank">
                {github_svg} GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# Process PDF Document Upload
# ==========================================
if uploaded_file and st.session_state.retriever is None:
    with st.spinner("📄 Processing your document..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        st.session_state.chunks = chunks

        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(chunks, embedding)
        st.session_state.retriever = db.as_retriever(search_kwargs={"k": 3})

        os.remove(pdf_path)

    st.success("✅ PDF indexed successfully!")

# ==========================================
# Display Message History
# ==========================================
current_messages = get_current_messages()

if st.session_state.retriever is None and len(current_messages) == 0:
    st.info("📄 Upload a PDF from the sidebar to start chatting.")

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# Input Bar & Real-Time Streaming Logic
# ==========================================
question = st.chat_input("Ask anything...")

if question:
    current_messages.append({"role": "user", "content": question})

    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            if chat["title"] == "New Chat" or chat["title"].startswith("Chat "):
                chat["title"] = generate_chat_title(question)

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if st.session_state.retriever is not None:
            with st.spinner("🧠 Searching document..."):
                docs = st.session_state.retriever.invoke(question)
                st.session_state.last_docs = docs
                context = "\n\n".join(doc.page_content for doc in docs)

                system_prompt = f"""
You are a helpful AI Assistant.
Use the following context from the uploaded PDF to answer the user's question. 
If the answer cannot be found in the context, politely mention that it's not in the document, but you can answer using general knowledge.

Context:
{context}
"""
        else:
            system_prompt = "You are a helpful, smart, and friendly AI Assistant."

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in current_messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324",
                messages=formatted_messages,
                max_tokens=600
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"❌ Error: {e}"

        def stream_data():
            for word in answer.split(" "):
                yield word + " "
                time.sleep(0.02)

        full_response = st.write_stream(stream_data)

    current_messages.append({"role": "assistant", "content": full_response})
    st.rerun()

# ==========================================
# Retrieved Sources Expander
# ==========================================
if "last_docs" in st.session_state:
    with st.expander("📚 Retrieved Sources"):
        for i, doc in enumerate(st.session_state.last_docs, 1):
            page = doc.metadata.get("page", 0)
            st.markdown(f"**Chunk {i} (Page {page + 1})**")
            st.write(doc.page_content[:500] + "...")                                        


                                









# import os
# import tempfile
# import streamlit as st

# from dotenv import load_dotenv
# from openai import OpenAI

# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from streamlit_option_menu import option_menu

# # =====================================
# # Load Environment Variables
# # =====================================

# load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1"
# )

# # =====================================
# # Streamlit Page Configuration
# # =====================================

# st.set_page_config(
#     page_title="RAG Chatbot",
#     page_icon="🤖",
#     layout="wide"
# )
# # =====================================
# # Session State Initialization
# # =====================================
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "questions" not in st.session_state:
#     st.session_state.questions = 0

# if "retriever" not in st.session_state:
#     st.session_state.retriever = None

# if "pdf_name" not in st.session_state:
#     st.session_state.pdf_name = None 
# st.markdown(
# """
# # 🤖 AI Research Assistant

# ### Chat with your documents using Retrieval-Augmented Generation.
# """
# )

# st.caption(
#     "Upload a PDF and chat with your document using Retrieval-Augmented Generation."
# )
# col1,col2,col3=st.columns(3)

# with col1:

#     st.metric(
#         "Questions",
#         st.session_state.questions
#     )

# with col2:

#     if "chunks" in st.session_state:

#         st.metric(
#             "Chunks",
#             len(st.session_state.chunks)
#         )

# with col3:

#     if st.session_state.retriever:

#         st.success("🟢 Ready")

#     else:

#         st.warning("🟡 Upload PDF")

       
# # =====================================
# # Sidebar
# # =====================================

# with st.sidebar:
#     # 1. Calcul mta' l-path dynamic mta' el-logo
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     logo_path = os.path.join(current_dir, "assets", "logo.png")

#     # 2. Affichage mta' el-logo
#     if os.path.exists(logo_path):
#         st.image(logo_path, width=80)
#     else:
#         st.warning("⚠️ Logo image not found")

#     st.markdown("# AI Research Assistant")

#     st.caption("Powered by RAG")

#     st.divider()

#     uploaded_file = st.file_uploader(
#         "📄 Upload PDF",
#         type=["pdf"]
#     )

#     st.divider()

#     selected = option_menu(

#         menu_title=None,

#         options=[
#             "Chat",
#             "Statistics",
#             "About"
#         ],

#         icons=[
#             "chat",
#             "bar-chart",
#             "info-circle"
#         ],

#         default_index=0

#     )

#     st.divider()

#     st.subheader("Model")

#     st.success("🟢 DeepSeek")

#     st.write("Embedding : MiniLM")

#     st.write("Vector DB : FAISS")

#     st.write("Retriever : Top-5")

#     st.divider()

#     if st.button("🗑 New Chat"):

#         st.session_state.messages=[]

#         st.session_state.questions=0

#         st.rerun()

#     st.divider()

#     st.markdown("### 👩‍💻 Created by")

#     st.markdown("**Maram Elhadj**")

#     st.markdown(
#         "[🐙 GitHub](https://github.com/maram-el-hadj)"
#     )

#     st.markdown(
#         "[💼 LinkedIn](https://www.linkedin.com/in/maram-elhadj/)"
#     )

#     st.caption("Version 1.0")

# # =====================================
# # Upload PDF
# # =====================================

# uploaded_file = st.file_uploader(
#     "📄 Upload a PDF document",
#     type=["pdf"]
# )

# # =====================================
# # Build the RAG Pipeline
# # =====================================

# if (
#     uploaded_file is not None
#     and uploaded_file.name != st.session_state.pdf_name
# ):

#     with st.spinner("⏳ Processing PDF..."):

#         # Save uploaded PDF temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

#             tmp.write(uploaded_file.getbuffer())

#             pdf_path = tmp.name

#         # Load PDF
#         loader = PyPDFLoader(pdf_path)

#         documents = loader.load()

#         # Split documents into chunks
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200
#         )

#         chunks = splitter.split_documents(documents)

#         # Create embeddings
#         embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )

#         # Create FAISS vector database
#         vector_db = FAISS.from_documents(
#             chunks,
#             embeddings
#         )

#         # Create retriever
#         retriever = vector_db.as_retriever(
#             search_kwargs={"k": 8}
#         )

#         # Save retriever in Streamlit Session
#         st.session_state.retriever = retriever

#         # Save PDF name
#         st.session_state.pdf_name = uploaded_file.name

#         # Save chunks (useful later)
#         st.session_state.chunks = chunks

#         # Delete temporary PDF
#         if os.path.exists(pdf_path):

#             os.remove(pdf_path)

#     st.success("✅ PDF processed successfully!")

#     st.info(f"Chunks created : {len(chunks)}")

# # =====================================
# # Display Previous Messages
# # =====================================
# if len(st.session_state.messages)==0:

#     st.markdown("""

# ## 👋 Welcome

# Upload your PDF and start chatting.

# ---

# ### Features

# ✅ DeepSeek AI

# ✅ LangChain

# ✅ FAISS

# ✅ MiniLM Embeddings

# ✅ RAG Pipeline

# """)

# for message in st.session_state.messages:

#     with st.chat_message(message["role"]):

#         st.markdown(message["content"])

# # =====================================
# # Chat Input & Logic
# # =====================================

# question = st.chat_input("💬 Ask a question about your PDF...")

# if question:

#     # 🟢 Handled Summary check after receiving user question
#     question_lower = question.lower()

#     if "summarize" in question_lower or "summary" in question_lower:
#         query_text = f"Give a detailed summary of the uploaded document.\n\nUser request: {question}"
#     else:
#         query_text = question

#     # Display user message
#     with st.chat_message("user"):

#         st.markdown(question)

#     st.session_state.messages.append(
#         {
#             "role": "user",
#             "content": question
#         }
#     )

#     # Check if PDF exists
#     if st.session_state.retriever is None:

#         answer = "⚠️ Please upload a PDF first."

#     else:

#         with st.spinner("🤖 Thinking..."):

#             # Retrieve relevant chunks using modified query text
#             docs = st.session_state.retriever.invoke(query_text)

#             # 📌 Save Retrieved Docs in Session State
#             st.session_state.last_docs = docs

#             context = "\n\n".join(
#                 doc.page_content
#                 for doc in docs
#             )

#             # Prompt
#             system_prompt = f"""
# You are a helpful AI assistant using Retrieval-Augmented Generation (RAG).

# Your job is to answer ONLY using the provided context.

# Rules:
# - Use the retrieved context as your main source.
# - If the answer is clearly present, answer naturally.
# - If the user asks for a summary, summarize the retrieved context.
# - If the information is not present in the context, reply:
# "I don't know based on the uploaded document."
# - Never invent facts.

# Retrieved Context:
# {context}
# """

#             messages = [

#                 {
#                     "role": "system",
#                     "content": system_prompt
#                 }

#             ]

#             # Add previous conversation
#             for msg in st.session_state.messages:

#                 messages.append(msg)

#             try:

#                 response = client.chat.completions.create(

#                     model="deepseek/deepseek-chat-v3-0324",

#                     messages=messages,

#                     max_tokens=500

#                 )

#                 if response.choices:

#                     answer = response.choices[0].message.content

#                 else:

#                     answer = "No response received."

#             except Exception as e:

#                 answer = f"❌ Error:\n\n{e}"

#     # Display assistant answer
#     with st.chat_message("assistant"):

#         st.markdown(answer)

#     st.session_state.messages.append(

#         {

#             "role": "assistant",

#             "content": answer

#         }

#     )

# # =====================================
# # Sidebar Information
# # =====================================

# with st.sidebar:

#     st.divider()

#     if st.session_state.pdf_name:

#         st.success(f"📄 {st.session_state.pdf_name}")

#     if "chunks" in st.session_state:

#         st.info(f"Chunks : {len(st.session_state.chunks)}")

# # =====================================
# # Clear Chat Button
# # =====================================

# if st.sidebar.button("🗑️ Clear Chat"):

#     st.session_state.messages = []
    
#     # Clean last_docs on clear chat if exists
#     if "last_docs" in st.session_state:
#         del st.session_state["last_docs"]

#     st.rerun()

# # =====================================
# # Retrieved Chunks Viewer
# # =====================================

# if "last_docs" in st.session_state:

#     with st.expander("📚 Retrieved Chunks"):

#         for i, doc in enumerate(st.session_state.last_docs):

#             st.markdown(f"### Chunk {i+1}")

#             st.write(doc.page_content)

#             st.divider()
#             st.caption(
# """
# Created with ❤️ by Maram Elhadj

# AI Research Internship 2026
# """
# )





