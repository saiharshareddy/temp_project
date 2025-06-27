from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from app.services.pdf_utils import extract_text_from_pdf, save_resume_as_pdf
from app.services.llm_formatter import reformat_resume
from app.config import TEMP_FOLDER
import uuid

router = APIRouter()

@router.post("/upload-resume/")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    format_type: int = Form(...)
):
    # ✅ Validate input
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

    if format_type not in [1, 2]:
        return JSONResponse(status_code=400, content={"error": "Invalid format type selected."})

    # ✅ Extract resume text from uploaded PDF
    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)
    print("📝 Extracted Resume Text:\n", resume_text)

    # ✅ Use LLM to parse structured content
    format_example = request.app.state.format_templates[format_type]  # Optional, for format guidance
    structured_data = reformat_resume(resume_text, format_example)
    print("📦 Structured Resume Data:\n", structured_data)

    # ✅ Inject format-specific section labels
    if format_type == 1:
        labels = {
            "summary_label": "Professional Summary",
            "skills_label": "Skills",
            "experience_label": "Experience",
            "education_label": "Education"
        }
        template_file = "format1.html"
    elif format_type == 2:
        labels = {
            "summary_label": "Profile",
            "skills_label": "Core Competencies",
            "experience_label": "Work History",
            "education_label": "Academic Background"
        }
        template_file = "format2.html"

    # ✅ Merge labels with LLM data for rendering
    render_data = {**structured_data, **labels}

    # ✅ Generate output PDF
    output_path = f"{TEMP_FOLDER}/formatted_{uuid.uuid4().hex}.pdf"
    save_resume_as_pdf(render_data, template_file, output_path)

    # ✅ Return downloadable PDF
    return FileResponse(output_path, filename="formatted_resume.pdf", media_type='application/pdf')
