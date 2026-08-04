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

loader = PyPDFLoader("app/experiments/Day24-ConversationalRAG/documents/AI.pdf")
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

# Step 2: Add Conversation History array before the loop
history = []

print("="*50)
print("🤖 First RAG Chatbot (With Memory)")
print("="*50)

while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    # Step 3: Append user question to history and prepare full messages list
    history.append(
        {
            "role": "user",
            "content": question
        }
    )

    messages = history.copy()
    messages.append(
        {
            "role": "user",
            "content": f"""
Use ONLY the context below.

Context:
{context}

Question:
{question}
"""
        }
    )

    # Step 4: Send the dynamic `messages` list instead of hardcoded array
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324",
        messages=messages,
        max_tokens=300
    )

    answer = response.choices[0].message.content

    print("\nAssistant:\n")
    print(answer)

    # Step 5: Save Assistant Response to history for the next iteration
    history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )