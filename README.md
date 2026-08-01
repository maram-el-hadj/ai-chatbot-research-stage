
# Progress

## Day 08

- Connected to an LLM API.
- Built the first AI chatbot.

## Day 09

- Added conversation memory.
- Added system prompts.
- Improved chatbot architecture.

## Day 10
- Implemented Prompt Engineering strategies.

- Configured specialized system persona constraints.

- Integrated Zero-shot and Few-shot prompting methodologies.

## Day 11

- Configured LLM parameters (`temperature`, `max_tokens`).
- Implemented response control strategies for different use cases.
- Analyzed token usage and context window constraints.

## Day 12

- Refactored project into advanced software architecture (`app/core`, `app/services`, `app/utils`).
- Restructured imports to improve code organization and separation of concerns.
- Created `docs/Day12.md` documenting software architecture principles, refactoring benefits, and scalability for future RAG integration.
- Maintained core chatbot functionality while ensuring modularity, reusability, and maintainability.

## Day 13

- Implemented session memory control and sliding context windows.
- Managed token limits to prevent API context errors.
- Added dynamic history trimming and session reset capabilities.

## Day 14

- Analyzed AI chatbot orchestration frameworks.
- Created a technical benchmark comparing LangChain, LlamaIndex, Haystack, and Semantic Kernel.
- Structured Phase 2 framework integration roadmap.

# Day 15 — Introduction to LangChain

### What I Learned
- Discovered **LangChain** and how it simplifies building LLM applications through modular architecture.
- Learned to use **`PromptTemplate`** for generating dynamic, reusable prompts instead of manual string concatenation.

### Project Improvements & Practice
- Installed `langchain`, `langchain-openai`, and `langchain-core` in a clean environment.
- Created a prototype demonstrating how `ChatPromptTemplate` formats input variables (`topic`).
- Conducted a benchmark comparing **Pure Python** vs **LangChain**.

### Skills & Deliverables
- **Skills:** LangChain Basics, Prompt Templates, Modular Prompting, Framework Architecture.
- **Deliverables:** Prototype code (`main.py`), comparison notes (`comparison.md`), documentation, and GitHub commit.

## ✅ Day 16

- Learned PromptTemplate, ChatModel and OutputParser in LangChain.
- Built my first LangChain pipeline connected to an LLM.
- Compared prompt behavior using different variables.
- Prepared the project for more advanced LangChain components.

## ✅ Day 17

- Learned the LangChain Expression Language (LCEL).
- Built reusable pipelines with PromptTemplate, ChatModel and OutputParser.
- Explored invoke(), batch() and stream() methods.
- Improved my understanding of modular LLM workflows.

## ✅ Day 18

- Learned how LangChain loads external documents.
- Extracted text and metadata from a PDF using PyPDFLoader.
- Understood the difference between raw text and Document objects.
- Started building the foundation of a Retrieval-Augmented Generation (RAG) pipeline.

## ✅ Day 19

- Learned how to split documents into smaller chunks using LangChain.
- Compared fixed-size chunking with overlapping chunks.
- Prepared document chunks for embedding generation.
- Advanced one step further in the RAG pipeline.

## ✅ Day 20

- Learned how embedding models convert text into numerical vectors.
- Generated embeddings locally using Hugging Face.
- Compared embeddings for different sentences.
- Prepared document vectors for semantic search in RAG systems.