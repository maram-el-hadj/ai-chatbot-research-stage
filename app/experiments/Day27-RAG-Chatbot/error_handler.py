import streamlit as st

from openai import (
    APIError,
    RateLimitError,
    AuthenticationError,
)


# =========================================================
# API ERROR HANDLER
# =========================================================

def handle_api_error(error):
    """
    Display friendly and understandable error messages.
    """

    # -----------------------------------------------------
    # Rate Limit
    # -----------------------------------------------------

    if isinstance(
        error,
        RateLimitError,
    ):

        st.error(
            "⚠️ API rate limit reached. "
            "Please try again later."
        )

        return


    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    if isinstance(
        error,
        AuthenticationError,
    ):

        st.error(
            "🔑 API authentication failed. "
            "Please check your OpenRouter API key."
        )

        return


    # -----------------------------------------------------
    # General API Error
    # -----------------------------------------------------

    if isinstance(
        error,
        APIError,
    ):

        st.error(
            "❌ OpenRouter API error. "
            "Please try again."
        )

        return


    # -----------------------------------------------------
    # Unknown Error
    # -----------------------------------------------------

    st.error(
        f"❌ Something went wrong: {error}"
    )


# =========================================================
# PDF VALIDATION
# =========================================================

def validate_pdf(uploaded_file):
    """
    Validate an uploaded PDF file.
    """

    if uploaded_file is None:

        return False


    # -----------------------------------------------------
    # Check extension
    # -----------------------------------------------------

    filename = uploaded_file.name.lower()

    if not filename.endswith(".pdf"):

        st.warning(
            "📄 Please upload a PDF document."
        )

        return False


    # -----------------------------------------------------
    # Check MIME type
    # -----------------------------------------------------

    file_type = uploaded_file.type

    if file_type not in [
        "application/pdf",
        None,
        "",
    ]:

        st.warning(
            "📄 The uploaded file does not appear "
            "to be a valid PDF."
        )

        return False


    # -----------------------------------------------------
    # Check file size
    # -----------------------------------------------------

    try:

        file_size = uploaded_file.size

        if file_size == 0:

            st.warning(
                "📄 The uploaded PDF is empty."
            )

            return False

    except Exception:

        pass


    return True


# =========================================================
# QUESTION VALIDATION
# =========================================================

def validate_question(question):
    """
    Validate the user's question.
    """

    if question is None:

        return False


    if not isinstance(
        question,
        str,
    ):

        return False


    if not question.strip():

        return False


    return True