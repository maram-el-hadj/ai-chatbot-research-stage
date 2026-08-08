import os

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# OPENROUTER
# =========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

BASE_URL = (
    "https://openrouter.ai/api/v1"
)

MODEL_NAME = (
    "deepseek/deepseek-chat-v3-0324"
)


# =========================================================
# EMBEDDINGS
# =========================================================

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# TEXT SPLITTING
# =========================================================

CHUNK_SIZE = 500

CHUNK_OVERLAP = 100


# =========================================================
# RETRIEVER
# =========================================================

TOP_K = 3


# =========================================================
# LLM GENERATION
# =========================================================

TEMPERATURE = 0.2

MAX_TOKENS = 500


# =========================================================
# APPLICATION
# =========================================================

APP_NAME = "DocuMind AI"  # walla akhtar wahed m les noms elli fo9
APP_ICON = "🤖"
APP_DESCRIPTION = "Chat with your PDF using Retrieval-Augmented Generation (RAG)."


# =========================================================
# EXPORT
# =========================================================

EXPORT_FILENAME = (
    "conversation.pdf"
)