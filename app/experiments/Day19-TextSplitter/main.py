from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("app/documents/AI.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Original pages: {len(documents)}")
print(f"Chunks: {len(chunks)}")

print("\nFirst chunk:\n")
print(chunks[0].page_content)