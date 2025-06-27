from fastapi import FastAPI
from app.routes import resume
from app.templates_loader import load_format_templates

app = FastAPI()

# Load templates on startup
app.state.format_templates = load_format_templates()

# Mount the upload API
app.include_router(resume.router)

# Optional: serve static HTML
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
