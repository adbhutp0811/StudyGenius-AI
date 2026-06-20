import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable


def generate_resume_pdf(resume):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, spaceAfter=6)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#2563eb'))
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=4, leading=14)
    bold_style = ParagraphStyle('BoldNormal', parent=normal_style, fontName='Helvetica-Bold')

    elements.append(Paragraph(resume.full_name or 'Your Name', title_style))
    contact_info = f"{resume.email} | {resume.phone}"[:100]
    if resume.linkedin:
        contact_info += f" | LinkedIn"
    if resume.github:
        contact_info += f" | GitHub"
    elements.append(Paragraph(contact_info, normal_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
    elements.append(Spacer(1, 12))

    if resume.professional_summary:
        elements.append(Paragraph('Professional Summary', heading_style))
        elements.append(Paragraph(resume.professional_summary, normal_style))
        elements.append(Spacer(1, 12))

    if resume.skills:
        elements.append(Paragraph('Skills', heading_style))
        skills_text = ', '.join(resume.skills)
        elements.append(Paragraph(skills_text, normal_style))
        elements.append(Spacer(1, 12))

    if resume.experience:
        elements.append(Paragraph('Experience', heading_style))
        for exp in resume.experience[:3]:
            title = exp.get('title', '')
            company = exp.get('company', '')
            dates = exp.get('dates', '')
            desc = exp.get('description', '')
            elements.append(Paragraph(f"<b>{title}</b> at {company}", bold_style))
            if dates:
                elements.append(Paragraph(dates, normal_style))
            if desc:
                elements.append(Paragraph(desc[:300], normal_style))
            elements.append(Spacer(1, 6))

    if resume.education:
        elements.append(Paragraph('Education', heading_style))
        for edu in resume.education[:2]:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            year = edu.get('year', '')
            elements.append(Paragraph(f"<b>{degree}</b> - {institution}", bold_style))
            if year:
                elements.append(Paragraph(year, normal_style))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_blog_pdf(blog):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('BlogTitle', parent=styles['Title'], fontSize=22, spaceAfter=12)
    normal_style = ParagraphStyle('BlogNormal', parent=styles['Normal'], fontSize=11, spaceAfter=8, leading=16)

    elements.append(Paragraph(blog.title, title_style))
    elements.append(Spacer(1, 12))

    for line in blog.content.split('\n'):
        if line.strip():
            elements.append(Paragraph(line.strip(), normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_question_paper_pdf(paper):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('PaperTitle', parent=styles['Title'], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle('PaperHeading', parent=styles['Heading2'], fontSize=13, spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('PaperNormal', parent=styles['Normal'], fontSize=10, spaceAfter=6, leading=14)
    bold_style = ParagraphStyle('BoldNormal', parent=normal_style, fontName='Helvetica-Bold')

    elements.append(Paragraph(paper.title, title_style))
    info = f"Subject: {paper.subject_name} | Duration: {paper.time_duration_minutes} mins | Total Marks: {paper.total_marks}"
    elements.append(Paragraph(info, bold_style))
    elements.append(HRFlowable(width="100%", thickness=1))
    elements.append(Spacer(1, 12))

    questions = paper.questions

    mcqs = [q for q in questions if q.get('type') == 'mcq']
    short_answers = [q for q in questions if q.get('type') == 'short_answer']
    long_answers = [q for q in questions if q.get('type') == 'long_answer']

    if mcqs:
        elements.append(Paragraph('Section A: Multiple Choice Questions', heading_style))
        for i, q in enumerate(mcqs, 1):
            elements.append(Paragraph(f"{i}. {q.get('question', '')} ({q.get('marks', 1)} mark{'s' if q.get('marks', 1) > 1 else ''})", normal_style))
            for opt in q.get('options', []):
                elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{opt}", normal_style))
            elements.append(Spacer(1, 6))

    if short_answers:
        elements.append(Paragraph('Section B: Short Answer Questions', heading_style))
        for i, q in enumerate(short_answers, 1):
            elements.append(Paragraph(f"{i}. {q.get('question', '')} ({q.get('marks', 2)} marks)", normal_style))
            elements.append(Spacer(1, 6))

    if long_answers:
        elements.append(Paragraph('Section C: Long Answer Questions', heading_style))
        for i, q in enumerate(long_answers, 1):
            elements.append(Paragraph(f"{i}. {q.get('question', '')} ({q.get('marks', 5)} marks)", normal_style))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer
