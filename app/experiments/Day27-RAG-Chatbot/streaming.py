import time
import streamlit as st


def stream_response(text: str, delay: float = 0.015):
    """
    Display a fake streaming effect word by word.
    Returns the full generated text.
    """

    placeholder = st.empty()

    current = ""

    for word in text.split():

        current += word + " "

        placeholder.markdown(current + "▌")

        time.sleep(delay)

    placeholder.markdown(current)

    return current