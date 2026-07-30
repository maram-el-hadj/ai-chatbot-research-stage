from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple words."
)

formatted = prompt.invoke(
    {
        "topic": "Embeddings"
    }
)

print(formatted)