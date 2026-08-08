from typing import List


# =========================================================
# EXTRACT SOURCES
# =========================================================

def extract_sources(docs) -> List[str]:
    """
    Extract unique PDF names and page numbers
    from retrieved LangChain documents.
    """

    if not docs:
        return []

    sources = []

    for doc in docs:

        metadata = getattr(
            doc,
            "metadata",
            {}
        )

        source = metadata.get(
            "source",
            "Document"
        )

        page = metadata.get(
            "page",
            None
        )

        # PDF filename
        try:
            import os

            filename = os.path.basename(
                source
            )

        except Exception:

            filename = "Document"

        # LangChain pages start from 0
        if page is not None:

            page_number = page + 1

            source_text = (
                f"📄 {filename} · "
                f"Page {page_number}"
            )

        else:

            source_text = (
                f"📄 {filename}"
            )

        if source_text not in sources:

            sources.append(
                source_text
            )

    return sources


# =========================================================
# RENDER SOURCES
# =========================================================

def render_sources(
    st,
    docs
):
    """
    Display the PDF sources retrieved
    by the RAG pipeline.
    """

    sources = extract_sources(
        docs
    )

    if not sources:
        return

    with st.expander(
        "📚 Sources",
        expanded=False,
    ):

        st.caption(
            "Information retrieved from your documents:"
        )

        for source in sources:

            st.markdown(
                f"- {source}"
            )