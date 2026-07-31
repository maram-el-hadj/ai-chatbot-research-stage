import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3-0324",
    max_tokens=1000
)

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} for a {level} student."
)

parser = StrOutputParser()

chain = prompt | llm | parser

for chunk in chain.stream(
    {
        "topic":"Artificial Intelligence",
        "level":"beginner"
    }
):
    print(chunk, end="", flush=True)