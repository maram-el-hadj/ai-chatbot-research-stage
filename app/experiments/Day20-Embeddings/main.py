from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [
    "Artificial Intelligence",
    "Machine Learning",
    "Football"
]

vectors = embedding.embed_documents(texts)

print(len(vectors))

print(len(vectors[0]))