import os
from typing import List, Tuple, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    BASE_URL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
)

from prompt import SYSTEM_PROMPT


# ==========================================
# OpenRouter Client
# ==========================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
)


# ==========================================
# Embeddings
# ==========================================

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# ==========================================
# Load PDFs
# ==========================================

def load_pdfs(pdf_paths: List[str]):
    """
    Load multiple PDF files.
    """

    all_documents = []

    for pdf_path in pdf_paths:

        if not os.path.exists(pdf_path):
            continue

        loader = PyPDFLoader(pdf_path)

        documents = loader.load()

        all_documents.extend(documents)

    if not all_documents:
        raise ValueError(
            "No readable PDF documents were found."
        )

    return all_documents


# ==========================================
# Build Vector Store From Multiple PDFs
# ==========================================

def build_vectorstore_from_paths(
    pdf_paths: List[str]
) -> Tuple[Any, int]:

    documents = load_pdfs(pdf_paths)

    # --------------------------------------
    # Split documents
    # --------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(
        documents
    )

    if not chunks:

        raise ValueError(
            "No text chunks could be created."
        )

    # --------------------------------------
    # FAISS
    # --------------------------------------

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings,
    )

    # --------------------------------------
    # Retriever
    # --------------------------------------

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": TOP_K
        }
    )

    return retriever, len(chunks)


# ==========================================
# Build Vector Store From Uploaded Files
# ==========================================

def build_vectorstore(uploaded_files):

    """
    Save uploaded PDFs and create a FAISS retriever.

    Kept for compatibility with the existing app.
    """

    import tempfile

    pdf_paths = []

    for uploaded_file in uploaded_files:

        suffix = ".pdf"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(
                uploaded_file.getbuffer()
            )

            pdf_paths.append(
                tmp.name
            )

    try:

        return build_vectorstore_from_paths(
            pdf_paths
        )

    finally:

        for path in pdf_paths:

            if os.path.exists(path):

                os.remove(path)


# ==========================================
# Retrieve Context
# ==========================================

def retrieve_context(
    retriever,
    question: str
):

    if retriever is None:

        raise ValueError(
            "No PDF has been loaded."
        )

    docs = retriever.invoke(
        question
    )

    if not docs:

        return "", []

    context_parts = []

    for doc in docs:

        page = doc.metadata.get(
            "page",
            None
        )

        source = doc.metadata.get(
            "source",
            "document"
        )

        if page is not None:

            page_number = page + 1

            context_parts.append(
                f"[Source: {os.path.basename(source)} | "
                f"Page: {page_number}]\n"
                f"{doc.page_content}"
            )

        else:

            context_parts.append(
                f"[Source: {os.path.basename(source)}]\n"
                f"{doc.page_content}"
            )

    context = "\n\n".join(
        context_parts
    )

    return context, docs


# ==========================================
# Build Messages
# ==========================================

def build_messages(
    retriever,
    question: str,
    history=None
):

    if retriever is None:

        raise ValueError(
            "Please upload a PDF first."
        )

    context, docs = retrieve_context(
        retriever,
        question
    )

    if not context.strip():

        raise ValueError(
            "I couldn't find relevant information "
            "in the uploaded document."
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # --------------------------------------
    # Conversation History
    # --------------------------------------

    if history:

        for message in history:

            role = message.get(
                "role"
            )

            content = message.get(
                "content"
            )

            if (
                role in [
                    "user",
                    "assistant"
                ]
                and content
            ):

                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

    # --------------------------------------
    # RAG Prompt
    # --------------------------------------

    rag_prompt = f"""
Answer the user's question using ONLY the
information contained in the retrieved context.

RETRIEVED CONTEXT
=================

{context}

USER QUESTION
=============

{question}

STRICT RULES
============

1. Use only the retrieved context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer cannot be found in the context,
   say exactly:

"I couldn't find this information in the uploaded document."

5. If possible, mention the source PDF and page.
"""

    messages.append(
        {
            "role": "user",
            "content": rag_prompt,
        }
    )

    return messages, docs


# ==========================================
# Normal RAG Answer
# ==========================================

def ask_llm(
    retriever,
    question: str,
    history=None
):

    messages, docs = build_messages(
        retriever,
        question,
        history
    )

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=messages,

        temperature=TEMPERATURE,

        max_tokens=MAX_TOKENS,
    )

    answer = (
        response
        .choices[0]
        .message
        .content
    )

    return answer, docs


# ==========================================
# REAL RAG STREAMING
# ==========================================

def stream_rag_answer(
    retriever,
    question: str,
    history=None
):

    messages, docs = build_messages(
        retriever,
        question,
        history
    )

    stream = client.chat.completions.create(

        model=MODEL_NAME,

        messages=messages,

        temperature=TEMPERATURE,

        max_tokens=MAX_TOKENS,

        stream=True,
    )

    for chunk in stream:

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if delta is None:
            continue

        content = delta.content

        if content:

            yield content, docs