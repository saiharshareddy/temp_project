import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.config import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE, TOP_P

# Load model on CPU
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map={"": "cpu"}  # forces CPU usage
)
torch.set_num_threads(4)


def extract_json_from_text(text: str) -> str:
    """Extract the JSON substring from LLM response and clean it."""
    json_start = text.find('{')
    json_end = text.rfind('}') + 1

    if json_start == -1 or json_end == 0:
        print("❌ JSON not found in LLM output. Full output was:\n", text)
        raise ValueError("❌ JSON not found in LLM output")

    json_string = text[json_start:json_end]

    # Clean up common LLM errors
    json_string = re.sub(r",\s*}", "}", json_string)
    json_string = re.sub(r",\s*]", "]", json_string)
    json_string = re.sub(r"[^\x00-\x7F]+", "", json_string)

    return json_string


def reformat_resume(resume_text: str, format_example: str = "", format_type: int = 1) -> dict:
    """Send resume text to LLM and receive structured JSON response."""
    if not resume_text.strip():
        raise ValueError("❌ Resume text is empty")

    # Clean resume text
    resume_text = resume_text.replace("\n", " ").strip()

    # Format-aware prompt
    prompt = f"""
You are an AI resume parser.

Extract the following information from the resume and return ONLY a valid JSON object:

- name
- title
- contact
- summary
- skills (as a list)
- experience (as a list of objects: position, company, years, description)
- education (as a list of objects: degree, institution, year)

Use actual values extracted from the resume text below. DO NOT use placeholder text.
DO NOT return explanations, commentary, or markdown.

{f"(Use format type {format_type} to align section logic if helpful)" if format_type else ''}

--- Resume Text ---
{resume_text}
"""

    print("📤 Prompting LLM...")

    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(model.device)
    output = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    raw_output = tokenizer.decode(output[0], skip_special_tokens=True)
    print("🧾 Raw LLM output:\n", raw_output)

    # Save output to inspect if needed
    with open("temp_files/llm_raw_output.txt", "w", encoding="utf-8") as f:
        f.write(raw_output)

    # Extract and parse JSON
    json_string = extract_json_from_text(raw_output)
    structured = json.loads(json_string)

    print("✅ Structured JSON parsed successfully.")
    return structured
