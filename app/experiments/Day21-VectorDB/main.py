from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

texts = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Football",
    "Pizza"
]

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_texts(
    texts,
    embedding
)
query = "Soccer"

results = db.similarity_search(query, k=2)

print("\nResults:\n")

for doc in results:
    print(doc.page_content)

print("Vector database created successfully!")

print("Number of documents:", db.index.ntotal)