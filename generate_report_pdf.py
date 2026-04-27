from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def md_line_to_html(line: str) -> str:
    text = line.strip()
    if text.startswith("### "):
        return f"<b>{text[4:]}</b>"
    if text.startswith("## "):
        return f"<b>{text[3:]}</b>"
    if text.startswith("# "):
        return f"<b>{text[2:]}</b>"
    if text.startswith("- "):
        return f"- {text[2:]}"
    return text


def build_pdf(md_path: Path, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )

    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=6,
    )

    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = []
    first_heading = True
    for raw in md_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            story.append(Spacer(1, 4))
            continue

        html_line = md_line_to_html(raw)
        if raw.startswith("# "):
            style = title if first_heading else heading
            first_heading = False
        elif raw.startswith("## "):
            style = heading
        else:
            style = body

        story.append(Paragraph(html_line, style))

    doc.build(story)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    md_file = root / "PROJECT_REPORT.md"
    pdf_file = root / "SenseTrade_AI_Project_Report.pdf"
    build_pdf(md_file, pdf_file)
    print(pdf_file)

