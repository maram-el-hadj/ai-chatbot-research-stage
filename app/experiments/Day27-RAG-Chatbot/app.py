import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Custom Modules
from history import (
    create_chat,
    save_chat,
    load_chat,
    list_chats,
    delete_chat,
    rename_chat,
    add_message
)
from streaming import stream_response
from pdf_export import export_chat
from rag import build_vectorstore, ask_llm

load_dotenv()

# Client OpenAI / OpenRouter for Title Summarization
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def generate_chat_title(first_question):
    try:
        res = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=[
                {"role": "system", "content": "Generate a concise 2-3 word title summarizing the prompt. Plain text only, no quotes, no markdown."},
                {"role": "user", "content": first_question}
            ],
            max_tokens=10
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return first_question[:25]

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
# Session State Initialization
# ==========================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

chats_list = list_chats()
if "active_chat_id" not in st.session_state:
    if chats_list:
        st.session_state.active_chat_id = chats_list[0]["id"]
    else:
        new_id = create_chat(title="New Chat")
        st.session_state.active_chat_id = new_id

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "last_docs" not in st.session_state:
    st.session_state.last_docs = None

# Track menu state for 3-dots popup
if "show_delete_id" not in st.session_state:
    st.session_state.show_delete_id = None

# ==========================================
# Custom CSS (Strictly Clean - NO RED)
# ==========================================
def load_css():
    if st.session_state.dark_mode:
        bg = "#111827"
        txt = "#FFFFFF"
        sb = "#1F2937"
        active_btn_bg = "#374151"
        github_icon_color = "#FFFFFF"
    else:
        bg = "#FFFFFF"
        txt = "#111827"
        sb = "#F8FAFC"
        active_btn_bg = "#E2E8F0"
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
    
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem !important;
        background-color: {sb};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sb};
        border-right: 1px solid #E5E7EB;
    }}

    /* KILL ALL RED BUTTON STYLES IN STREAMLIT */
    button[kind="primary"] {{
        background-color: {active_btn_bg} !important;
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
    }}

    footer {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# Load current active chat
current_chat = load_chat(st.session_state.active_chat_id)
if not current_chat:
    st.session_state.active_chat_id = create_chat()
    current_chat = load_chat(st.session_state.active_chat_id)

messages = current_chat.get("messages", [])

# ==========================================
# Sidebar UI
# ==========================================
with st.sidebar:
    st.markdown("# 🤖 AI Research Assistant")
    st.caption("Your intelligent PDF assistant")

    st.divider()

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, key="btn_new_chat"):
        new_id = create_chat(title="New Chat")
        st.session_state.active_chat_id = new_id
        st.session_state.last_docs = None
        st.rerun()

    # Document Uploader
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Supported format: PDF"
    )

    if uploaded_file and st.session_state.retriever is None:
        with st.spinner("📄 Indexing PDF..."):
            st.session_state.retriever = build_vectorstore(uploaded_file)
        st.success("✅ Document indexed!")

    st.markdown("<p style='font-size:12px; font-weight:700; color:#94A3B8; margin-top:15px; margin-bottom:5px;'>RECENTS</p>", unsafe_allow_html=True)
    
    # Recents List with clean 3 dots (⋮) toggle menu
    all_chats = list_chats()
    for chat in all_chats:
        is_active = (chat["id"] == st.session_state.active_chat_id)
        btn_label = f"💬 {chat['title']}"
        
        c1, c2 = st.columns([0.82, 0.18])
        with c1:
            if st.button(btn_label, key=f"chat_{chat['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.active_chat_id = chat["id"]
                st.session_state.last_docs = None
                st.rerun()
        with c2:
            if st.button("⋮", key=f"dots_{chat['id']}", use_container_width=True):
                if st.session_state.show_delete_id == chat["id"]:
                    st.session_state.show_delete_id = None
                else:
                    st.session_state.show_delete_id = chat["id"]
                st.rerun()
        
        # Display Delete action under the chat when 3-dots clicked
        if st.session_state.show_delete_id == chat["id"]:
            if st.button(f"🗑️ Delete", key=f"act_del_{chat['id']}", use_container_width=True):
                delete_chat(chat["id"])
                st.session_state.show_delete_id = None
                remaining = list_chats()
                if remaining:
                    st.session_state.active_chat_id = remaining[0]["id"]
                else:
                    st.session_state.active_chat_id = create_chat()
                st.rerun()

    st.divider()

    # Dark Mode
    dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    # Export PDF
    if st.button("📄 Export PDF", use_container_width=True, key="btn_export"):
        if messages:
            pdf_file = export_chat(messages, filename=f"chat_{st.session_state.active_chat_id[:6]}.pdf")
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇ Download PDF",
                    data=f,
                    file_name="conversation.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("No messages to export.")

    # Footer
    st.markdown(
        """
        <div class="sidebar-footer">
            <span>By <b>Maram Elhadj</b></span>
            <a href="https://github.com/maram-el-hadj" target="_blank">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# Main Chat Canvas
# ==========================================
st.title("🤖 AI Research Assistant")
st.caption("Ask questions about your documents or general concepts.")

if st.session_state.retriever is None and len(messages) == 0:
    st.info("📄 Upload a PDF to start RAG or type directly to chat with General Knowledge.")

# Display existing messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# Input Processing
# ==========================================
question = st.chat_input("Ask anything...")

if question:
    # 1. Show user message
    with st.chat_message("user"):
        st.markdown(question)
    
    # 2. Smart Title Summarization
    if len(messages) == 0:
        smart_title = generate_chat_title(question)
        rename_chat(st.session_state.active_chat_id, smart_title)

    add_message(st.session_state.active_chat_id, "user", question)

    # 3. Stream Assistant Answer
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            answer, docs = ask_llm(
                st.session_state.retriever,
                question,
                history=messages
            )
            st.session_state.last_docs = docs

        full_response = ""
        for chunk in stream_response(answer, delay=0.01):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)

    # Save Assistant response
    add_message(st.session_state.active_chat_id, "assistant", full_response)
    st.rerun()

# Document Sources
if st.session_state.last_docs:
    with st.expander("📚 Retrieved Context Sources"):
        for i, doc in enumerate(st.session_state.last_docs, 1):
            page = doc.metadata.get("page", 0)
            st.markdown(f"**Source {i} (Page {page + 1})**")
            st.write(doc.page_content[:400] + "...")