import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text: str) -> str:
    """
    Clean chatbot Markdown and streaming artifacts
    before inserting text into the PDF.
    """

    if not text:
        return ""

    text = str(text)

    # -----------------------------------------
    # Remove streaming cursors
    # -----------------------------------------

    text = text.replace("█", "")
    text = text.replace("▌", "")

    # -----------------------------------------
    # Escape HTML-sensitive characters
    # -----------------------------------------

    text = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

    # -----------------------------------------
    # Bold
    # **text**
    # -----------------------------------------

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"<b>\1</b>",
        text,
        flags=re.DOTALL,
    )

    # -----------------------------------------
    # Italic
    # *text*
    # -----------------------------------------

    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"<i>\1</i>",
        text,
    )

    # -----------------------------------------
    # Inline code
    # `code`
    # -----------------------------------------

    text = re.sub(
        r"`([^`]+)`",
        r"<font name='Courier'>\1</font>",
        text,
    )

    # -----------------------------------------
    # Markdown headings
    # # Heading
    # -----------------------------------------

    text = re.sub(
        r"^#{1,6}\s+(.*)$",
        r"<b>\1</b>",
        text,
        flags=re.MULTILINE,
    )

    # -----------------------------------------
    # Markdown bullets
    # -----------------------------------------

    text = re.sub(
        r"^[\-\*]\s+",
        "• ",
        text,
        flags=re.MULTILINE,
    )

    # -----------------------------------------
    # New lines
    # -----------------------------------------

    text = text.replace(
        "\n",
        "<br/>",
    )

    return text.strip()


# =========================================================
# EXPORT CHAT TO PDF
# =========================================================

def export_chat(
    messages,
    filename="conversation.pdf",
):

    # =====================================================
    # DOCUMENT
    # =====================================================

    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        rightMargin=18 * mm,
        leftMargin=18 * mm,

        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )


    # =====================================================
    # BASE STYLES
    # =====================================================

    styles = getSampleStyleSheet()


    # =====================================================
    # TITLE
    # =====================================================

    title_style = ParagraphStyle(

        "ResearchBotTitle",

        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=20,

        leading=24,

        alignment=TA_CENTER,

        textColor=colors.HexColor(
            "#1E3A8A"
        ),

        spaceAfter=8,
    )


    subtitle_style = ParagraphStyle(

        "ResearchBotSubtitle",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=9,

        leading=13,

        alignment=TA_CENTER,

        textColor=colors.HexColor(
            "#64748B"
        ),

        spaceAfter=22,
    )


    # =====================================================
    # USER MESSAGE
    # =====================================================

    user_style = ParagraphStyle(

        "UserMessage",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=10.5,

        leading=16,

        textColor=colors.HexColor(
            "#0F172A"
        ),

        spaceAfter=5,

        keepWithNext=True,
    )


    # =====================================================
    # ASSISTANT MESSAGE
    # =====================================================

    assistant_style = ParagraphStyle(

        "AssistantMessage",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=10.5,

        leading=16,

        textColor=colors.HexColor(
            "#334155"
        ),

        spaceAfter=16,
    )


    # =====================================================
    # DOCUMENT CONTENT
    # =====================================================

    story = []


    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "ResearchBot",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI Research Assistant · Conversation Export",
            subtitle_style,
        )
    )


    # -----------------------------------------------------
    # Messages
    # -----------------------------------------------------

    for message in messages:

        role = message.get(
            "role",
            "",
        )

        content = message.get(
            "content",
            "",
        )

        if not content:
            continue

        cleaned_content = clean_text(
            content
        )


        # ---------------------------------------------
        # User
        # ---------------------------------------------

        if role == "user":

            story.append(
                Paragraph(
                    "<b>You</b>",
                    user_style,
                )
            )

            story.append(
                Paragraph(
                    cleaned_content,
                    assistant_style,
                )
            )


        # ---------------------------------------------
        # Assistant
        # ---------------------------------------------

        elif role == "assistant":

            story.append(
                Paragraph(
                    "<b>ResearchBot</b>",
                    user_style,
                )
            )

            story.append(
                Paragraph(
                    cleaned_content,
                    assistant_style,
                )
            )


        story.append(
            Spacer(
                1,
                4,
            )
        )


    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(
        story
    )


    return filename