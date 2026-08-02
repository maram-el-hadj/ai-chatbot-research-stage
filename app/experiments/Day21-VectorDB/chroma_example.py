from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

texts = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Pizza"
]

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_texts(
    texts,
    embedding
)

results = db.similarity_search(
    "AI",
    k=2
)

for doc in results:
    print(doc.page_content)