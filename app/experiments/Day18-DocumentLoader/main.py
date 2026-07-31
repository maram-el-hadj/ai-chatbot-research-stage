from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("app/documents/AI.pdf")

documents = loader.load()

print(documents[0].page_content)
