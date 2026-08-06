import os
import tempfile

from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ==========================================
# Load Environment
# ==========================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ==========================================
# Build Vector Database
# ==========================================

def build_vectorstore(uploaded_file):
    """
    Create a FAISS vector database from an uploaded PDF.
    """

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(
        chunks,
        embeddings
    )

    retriever = db.as_retriever(
        search_kwargs={"k": 3}
    )

    os.remove(pdf_path)

    return retriever


# ==========================================
# Retrieve Context
# ==========================================

def retrieve_context(retriever, question):
    """
    Retrieve the most relevant chunks.
    """

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    return context, docs


# ==========================================
# Generate Answer
# ==========================================

def ask_llm(retriever, question, history=None):
    if history is None:
        history = []

    docs = None
    if retriever is not None:
        context, docs = retrieve_context(retriever, question)
        prompt = f"""You are an AI assistant answering questions using the provided document context.

Context:
{context}

Question:
{question}"""
    else:
        prompt = question

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324",
        messages=messages,
        temperature=0.2,
        max_tokens=500
    )

    answer = response.choices[0].message.content
    return answer, docs