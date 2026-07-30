import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3-0324",
    max_tokens=1000  
)

prompt = ChatPromptTemplate.from_template(
    """
You are an AI teacher.

Explain {topic}

for a {level} student.
"""
)

chain = prompt | llm 

response = chain.invoke(
    {
        "topic": "Embeddings",
        "level": "beginner"
    }
)

print(response.content)