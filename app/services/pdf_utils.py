import pdfkit
from jinja2 import Environment, FileSystemLoader

import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def save_resume_as_pdf(data: dict, template_name: str, output_path: str):
    # ✅ Explicit path to wkhtmltopdf
    path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Load HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name)
    html_out = template.render(data)

    # Render PDF
    pdfkit.from_string(html_out, output_path, configuration=config)
