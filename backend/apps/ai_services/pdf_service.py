import PyPDF2
import pdfplumber
import io
import os
from django.conf import settings


class PDFService:
    def process_pdf(self, pdf_document):
        try:
            file_path = pdf_document.file.path
            content = ''
            page_count = 0

            try:
                with pdfplumber.open(file_path) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            content += text + '\n\n'
            except Exception:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    page_count = len(pdf_reader.pages)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text + '\n\n'

            return {
                'content': content.strip(),
                'page_count': page_count,
            }

        except Exception as e:
            return {
                'content': f'Error processing PDF: {str(e)}',
                'page_count': 0,
            }

    def extract_sections(self, content, max_length=500):
        sections = []
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 50:
                sections.append(para.strip()[:max_length])
        return sections

    def search_in_pdf(self, content, query):
        results = []
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if query.lower() in para.lower():
                results.append({
                    'index': i,
                    'text': para[:500] + '...' if len(para) > 500 else para,
                })
        return results
