import streamlit as st

st.title("🤖 RAG Chatbot")

question = st.chat_input("Ask me something")

if question:

    st.chat_message("user").write(question)

    st.chat_message("assistant").write(
        "This is a fake answer."
    )
with st.sidebar:

    st.header("Settings")

    st.write("Model")

    st.write("Vector DB")

    st.write("Retriever")

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)    