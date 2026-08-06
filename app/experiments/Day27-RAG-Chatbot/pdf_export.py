from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm


def export_chat(messages, filename="conversation.pdf"):
    """
    Export the chat conversation to a PDF file.
    """

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = HexColor("#2563EB")

    normal = styles["BodyText"]
    normal.spaceAfter = 10

    story = []

    story.append(Paragraph("RAG Chatbot Conversation", title_style))

    story.append(Paragraph("<br/><br/>", normal))

    for msg in messages:

        role = msg["role"].capitalize()

        content = msg["content"].replace("\n", "<br/>")

        story.append(
            Paragraph(
                f"<b>{role}:</b> {content}",
                normal
            )
        )

    doc.build(story)

    return filename