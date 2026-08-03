import os

from dotenv import load_dotenv

from openai import OpenAI

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

loader = PyPDFLoader("app/experiments/Day23-CompleteRAG/documents/AI.pdf")

documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(
    chunks,
    embedding
)

retriever = db.as_retriever(
    search_kwargs={"k":3}
)

print("="*50)
print("🤖 First RAG Chatbot")
print("="*50)

while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    prompt = f"""
Answer ONLY using the context below.

If the answer is not in the context, say:
"I don't know."

Context:

{context}

Question:

{question}
"""

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        max_tokens=300
    )

    print("\nAssistant:\n")

    print(response.choices[0].message.content)