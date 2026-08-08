import os
import hashlib
import shutil

import streamlit as st
from openai import OpenAI

from config import (
    APP_NAME,
    APP_ICON,
    APP_DESCRIPTION,
    OPENROUTER_API_KEY,
    BASE_URL,
    MODEL_NAME,
)

from rag import (
    build_vectorstore_from_paths,
    stream_rag_answer,
)

from sources import render_sources

from error_handler import (
    handle_api_error,
    validate_pdf,
    validate_question,
)

from history import (
    create_chat,
    load_chat,
    list_chats,
    delete_chat,
    rename_chat,
    add_message,
)

from pdf_export import export_chat


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "data",
    "uploads",
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
)


# =========================================================
# SESSION STATE
# =========================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "active_chat_id" not in st.session_state:

    chats = list_chats()

    if chats:
        st.session_state.active_chat_id = (
            chats[0]["id"]
        )

    else:
        st.session_state.active_chat_id = (
            create_chat("New Chat")
        )

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "retriever_chat_id" not in st.session_state:
    st.session_state.retriever_chat_id = None

if "last_docs" not in st.session_state:
    st.session_state.last_docs = None

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "show_delete_id" not in st.session_state:
    st.session_state.show_delete_id = None


# =========================================================
# CHAT PDF DIRECTORY
# =========================================================

def get_chat_upload_dir(chat_id):

    folder = os.path.join(
        UPLOAD_DIR,
        str(chat_id),
    )

    os.makedirs(
        folder,
        exist_ok=True,
    )

    return folder


# =========================================================
# GET CHAT PDFS
# =========================================================

def get_chat_pdf_paths(chat_id):

    folder = get_chat_upload_dir(
        chat_id
    )

    paths = []

    for filename in os.listdir(folder):

        if filename.lower().endswith(".pdf"):

            paths.append(
                os.path.join(
                    folder,
                    filename,
                )
            )

    return sorted(paths)


# =========================================================
# FILE HASH
# =========================================================

def get_file_hash(uploaded_file):

    data = uploaded_file.getvalue()

    return hashlib.md5(
        data
    ).hexdigest()


# =========================================================
# SAVE UPLOADED PDF
# =========================================================

def save_uploaded_pdfs(
    chat_id,
    uploaded_files,
):

    folder = get_chat_upload_dir(
        chat_id
    )

    saved = []

    for uploaded_file in uploaded_files:

        if not validate_pdf(
            uploaded_file
        ):
            continue

        filename = os.path.basename(
            uploaded_file.name
        )

        file_path = os.path.join(
            folder,
            filename,
        )

        uploaded_hash = get_file_hash(
            uploaded_file
        )

        if os.path.exists(
            file_path
        ):

            try:

                with open(
                    file_path,
                    "rb",
                ) as f:

                    existing_hash = hashlib.md5(
                        f.read()
                    ).hexdigest()

                if existing_hash == uploaded_hash:
                    continue

            except Exception:
                pass

        with open(
            file_path,
            "wb",
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        saved.append(
            file_path
        )

    return saved


# =========================================================
# LOAD RETRIEVER FOR CHAT
# =========================================================

def restore_chat_retriever(
    chat_id
):

    pdf_paths = get_chat_pdf_paths(
        chat_id
    )

    if not pdf_paths:

        st.session_state.retriever = None

        st.session_state.retriever_chat_id = (
            chat_id
        )

        st.session_state.last_docs = None

        return

    try:

        with st.spinner(
            "📚 Loading your documents..."
        ):

            retriever, _ = (
                build_vectorstore_from_paths(
                    pdf_paths
                )
            )

        st.session_state.retriever = (
            retriever
        )

        st.session_state.retriever_chat_id = (
            chat_id
        )

        st.session_state.last_docs = None

    except Exception as error:

        st.session_state.retriever = None

        st.session_state.retriever_chat_id = (
            chat_id
        )

        handle_api_error(
            error
        )


# =========================================================
# CHAT TITLE
# =========================================================

def generate_chat_title(
    question
):

    try:

        response = (
            client.chat.completions.create(

                model=MODEL_NAME,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Create a short title "
                            "of 2 to 4 words for "
                            "this conversation. "
                            "Return only the title."
                        ),
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],

                temperature=0.2,

                max_tokens=20,
            )
        )

        title = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return title[:45]

    except Exception:

        return question[:35]


# =========================================================
# CSS
# =========================================================

def load_css():

    if st.session_state.dark_mode:

        background = "#111827"
        sidebar = "#161B22"
        text = "#F8FAFC"
        secondary = "#94A3B8"
        border = "#2A3441"
        hover = "#1F2937"

    else:

        background = "#FFFFFF"
        sidebar = "#F8FAFC"
        text = "#111827"
        secondary = "#64748B"
        border = "#E2E8F0"
        hover = "#F1F5F9"

    st.markdown(
        f"""
        <style>

        @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
        );

        html,
        body,
        [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background-color: {background};
            color: {text};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {sidebar};
            border-right: 1px solid {border};
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {sidebar};
        }}

        .block-container {{
            max-width: 1050px;
            padding-top: 1.5rem;
            padding-bottom: 5rem;
        }}

        h1,
        h2,
        h3 {{
            font-weight: 700 !important;
        }}

        .stButton > button {{
            border-radius: 10px;
            font-weight: 500;
            border: 1px solid {border};
        }}

        .stButton > button:hover {{
            background-color: {hover};
        }}

        .stChatMessage {{
            border-radius: 14px;
            margin-bottom: 8px;
        }}

        .sidebar-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 3px;
        }}

        .sidebar-subtitle {{
            color: {secondary};
            font-size: 13px;
        }}

        .section-label {{
            color: {secondary};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-top: 10px;
            margin-bottom: 8px;
        }}

        .welcome-screen {{
            text-align: center;
            padding: 85px 20px 45px 20px;
        }}

        .welcome-screen h1 {{
            font-size: 42px;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .welcome-screen p {{
            color: {secondary};
            font-size: 17px;
        }}

        .simple-footer {{
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid {border};
            font-size: 13px;
            color: {secondary};
        }}

        .simple-footer .author {{
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .simple-footer a {{
            color: {text};
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
        }}

        .simple-footer a:hover {{
            text-decoration: underline;
        }}

        [data-testid="stSidebarCollapseButton"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }}

        [data-testid="stSidebarCollapseButton"] button {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            cursor: pointer !important;
        }}

        footer {{
            visibility: hidden;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


load_css()


# =========================================================
# ACTIVE CHAT
# =========================================================

current_chat = load_chat(
    st.session_state.active_chat_id
)

if current_chat is None:

    new_chat_id = create_chat(
        "New Chat"
    )

    st.session_state.active_chat_id = (
        new_chat_id
    )

    current_chat = load_chat(
        new_chat_id
    )


messages = current_chat.get(
    "messages",
    [],
)


# =========================================================
# RESTORE PDF WHEN CHANGING CHAT
# =========================================================

if (
    st.session_state.retriever_chat_id
    != st.session_state.active_chat_id
):

    restore_chat_retriever(
        st.session_state.active_chat_id
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    logo_path = os.path.join(
        BASE_DIR,
        "assets",
        "logo.png",
    )

    if os.path.exists(
        logo_path
    ):

        st.image(
            logo_path,
            width=48,
        )

    st.markdown(
        f"""
        <div class="sidebar-title">
            {APP_ICON} {APP_NAME}
        </div>

        <div class="sidebar-subtitle">
            {APP_DESCRIPTION}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True,
    ):

        new_chat_id = create_chat(
            "New Chat"
        )

        st.session_state.active_chat_id = (
            new_chat_id
        )

        st.session_state.retriever = None

        st.session_state.retriever_chat_id = (
            new_chat_id
        )

        st.session_state.last_docs = None

        st.rerun()

    st.markdown(
        '<div class="section-label">RECENT CHATS</div>',
        unsafe_allow_html=True,
    )

    chats = list_chats()

    for chat in chats:

        chat_id = chat["id"]

        title = chat.get(
            "title",
            "New Chat",
        )

        active = (
            chat_id
            == st.session_state.active_chat_id
        )

        col1, col2 = st.columns(
            [0.84, 0.16]
        )

        with col1:

            if st.button(
                f"💬 {title}",
                key=f"chat_{chat_id}",
                use_container_width=True,
                type=(
                    "primary"
                    if active
                    else "secondary"
                ),
            ):

                st.session_state.active_chat_id = (
                    chat_id
                )

                st.session_state.retriever = None

                st.session_state.retriever_chat_id = (
                    None
                )

                st.session_state.last_docs = None

                st.rerun()

        with col2:

            if st.button(
                "⋮",
                key=f"menu_{chat_id}",
                use_container_width=True,
            ):

                if (
                    st.session_state.show_delete_id
                    == chat_id
                ):

                    st.session_state.show_delete_id = (
                        None
                    )

                else:

                    st.session_state.show_delete_id = (
                        chat_id
                    )

                st.rerun()

        if (
            st.session_state.show_delete_id
            == chat_id
        ):

            if st.button(
                "Delete chat",
                key=f"delete_{chat_id}",
                use_container_width=True,
            ):

                delete_chat(
                    chat_id
                )

                chat_folder = (
                    get_chat_upload_dir(
                        chat_id
                    )
                )

                if os.path.exists(
                    chat_folder
                ):

                    shutil.rmtree(
                        chat_folder,
                        ignore_errors=True,
                    )

                remaining = list_chats()

                if remaining:

                    st.session_state.active_chat_id = (
                        remaining[0]["id"]
                    )

                else:

                    st.session_state.active_chat_id = (
                        create_chat(
                            "New Chat"
                        )
                    )

                st.session_state.retriever = None

                st.session_state.retriever_chat_id = (
                    None
                )

                st.session_state.last_docs = None

                st.session_state.show_delete_id = (
                    None
                )

                st.rerun()

    st.divider()

    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
    )

    if dark_mode != st.session_state.dark_mode:

        st.session_state.dark_mode = (
            dark_mode
        )

        st.rerun()

    if st.button(
        "📄 Export PDF",
        use_container_width=True,
    ):

        if messages:

            try:

                export_path = export_chat(
                    messages,
                    filename=(
                        "conversation.pdf"
                    ),
                )

                with open(
                    export_path,
                    "rb",
                ) as pdf_file:

                    st.download_button(
                        "⬇ Download PDF",
                        data=pdf_file,
                        file_name="conversation.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            except Exception as error:

                handle_api_error(
                    error
                )

        else:

            st.info(
                "No messages to export."
            )

    st.markdown(
        """
        <div class="simple-footer">
            <div class="author">
                Created by Maram El Hadj
            </div>
            <a href="https://github.com/maram-el-hadj" target="_blank">
                <svg height="15" width="15" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
                GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True,  # <-- unsafe_allow_html added!
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    f"{APP_ICON} {APP_NAME}"
)

st.caption(
    APP_DESCRIPTION
)


# =========================================================
# PDF UPLOAD
# =========================================================

uploaded_files = st.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload one or more PDF documents.",
)


# =========================================================
# PROCESS NEW PDFs
# =========================================================

if uploaded_files:

    new_files = []

    for uploaded_file in uploaded_files:

        if not validate_pdf(
            uploaded_file
        ):
            continue

        file_hash = get_file_hash(
            uploaded_file
        )

        filename = os.path.basename(
            uploaded_file.name
        )

        unique_key = (
            f"{st.session_state.active_chat_id}"
            f"_{filename}"
            f"_{file_hash}"
        )

        if unique_key not in (
            st.session_state.processed_files
        ):

            new_files.append(
                uploaded_file
            )

            st.session_state.processed_files.add(
                unique_key
            )

    if new_files:

        try:

            with st.spinner(
                "📚 Indexing your PDF..."
            ):

                save_uploaded_pdfs(
                    st.session_state.active_chat_id,
                    new_files,
                )

                pdf_paths = (
                    get_chat_pdf_paths(
                        st.session_state.active_chat_id
                    )
                )

                retriever, _ = (
                    build_vectorstore_from_paths(
                        pdf_paths
                    )
                )

                st.session_state.retriever = (
                    retriever
                )

                st.session_state.retriever_chat_id = (
                    st.session_state.active_chat_id
                )

                st.session_state.last_docs = None

            st.success(
                f"✅ {len(new_files)} PDF(s) ready."
            )

        except Exception as error:

            handle_api_error(
                error
            )


# =========================================================
# PDF STATUS
# =========================================================

pdf_paths = get_chat_pdf_paths(
    st.session_state.active_chat_id
)

if pdf_paths:

    st.caption(
        f"📚 {len(pdf_paths)} PDF(s) connected to this chat."
    )


# =========================================================
# WELCOME SCREEN
# =========================================================

if not messages:

    st.markdown(
        """
        <div class="welcome-screen">
            <h1>Ask your documents.</h1>
            <p>Upload a PDF and ask questions about its content.</p>
        </div>
        """,
        unsafe_allow_html=True,  # <-- unsafe_allow_html added!
    )


# =========================================================
# CHAT HISTORY
# =========================================================

for message in messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# SOURCES
# =========================================================

if st.session_state.last_docs:

    render_sources(
        st,
        st.session_state.last_docs,
    )


# =========================================================
# QUESTION
# =========================================================

question = st.chat_input(
    "Ask a question about your document..."
)


# =========================================================
# QUESTION PROCESSING
# =========================================================

if question:

    if (
        st.session_state.retriever
        is None
    ):

        st.warning(
            "📄 Please upload a PDF first."
        )

        st.stop()

    if not validate_question(
        question
    ):

        st.stop()

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    if len(messages) == 0:

        title = generate_chat_title(
            question
        )

        rename_chat(
            st.session_state.active_chat_id,
            title,
        )

    add_message(
        st.session_state.active_chat_id,
        "user",
        question,
    )

    with st.chat_message(
        "assistant"
    ):

        placeholder = st.empty()

        full_response = ""

        retrieved_docs = []

        try:

            for (
                chunk,
                docs,
            ) in stream_rag_answer(
                st.session_state.retriever,
                question,
                history=messages,
            ):

                retrieved_docs = docs

                full_response += chunk

                placeholder.markdown(
                    full_response + "▌"
                )

            placeholder.markdown(
                full_response
            )

            st.session_state.last_docs = (
                retrieved_docs
            )

        except Exception as error:

            handle_api_error(
                error
            )

            st.stop()

    add_message(
        st.session_state.active_chat_id,
        "assistant",
        full_response,
    )

    st.rerun()