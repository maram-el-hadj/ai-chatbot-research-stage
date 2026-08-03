from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

texts = [
    "Artificial Intelligence is the science of building intelligent systems.",
    "Machine Learning is a subset of Artificial Intelligence.",
    "Deep Learning uses neural networks.",
    "Football is a popular sport.",
    "Pizza is an Italian dish."
]

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_texts(texts, embedding)

retriever = db.as_retriever(
    search_kwargs={"k":2}
)

query = "What is AI?"

results = retriever.invoke(query)

print("Retrieved documents:\n")

for i, doc in enumerate(results, start=1):
    print(f"Document {i}:")
    print(doc.page_content)
    print("-"*50)
similarity = db.similarity_search(
    "Artificial Intelligence",
    k=2
)

retrieved = retriever.invoke(
    "Artificial Intelligence"
)

print("Similarity Search")

for doc in similarity:
    print(doc.page_content)

print("\nRetriever")

for doc in retrieved:
    print(doc.page_content)    