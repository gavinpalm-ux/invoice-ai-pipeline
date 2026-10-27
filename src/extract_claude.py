"""Extract structured invoice data with Claude.

The PDF goes to Claude as a document block. A forced tool call makes Claude
answer in a fixed JSON schema instead of free text, so the downstream
validation code never has to parse prose.
"""
import base64
import os
from pathlib import Path

EXTRACTION_TOOL = {
    "name": "record_invoice",
    "description": "Record the structured fields read from one vendor invoice.",
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor": {"type": "string"},
            "invoice_number": {"type": ["string", "null"], "description": "null if not printed on the invoice"},
            "invoice_date": {"type": ["string", "null"], "description": "YYYY-MM-DD"},
            "due_date": {"type": ["string", "null"], "description": "YYYY-MM-DD"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "amount": {"type": "number"},
                    },
                    "required": ["description", "amount"],
                },
            },
            "total": {"type": ["number", "null"], "description": "The total due as printed"},
            "gl_category": {"type": "string"},
            "confidence": {"type": "number", "description": "0-1: how sure you are every field is read correctly"},
            "notes": {"type": "string", "description": "Anything unclear, missing or unusual"},
        },
        "required": ["vendor", "invoice_number", "invoice_date", "due_date",
                     "line_items", "total", "gl_category", "confidence", "notes"],
    },
}

PROMPT = """You are an accounts-payable assistant. Read the attached invoice and record its fields.

Rules:
- Copy values exactly as printed. Never guess or fill in a field that isn't on the page; use null.
- Record the total exactly as printed, even if it disagrees with the line items. Mention any disagreement in notes.
- Choose gl_category from this list only: {categories}
- Lower your confidence if anything is blurry, missing, ambiguous or inconsistent."""


def extract(pdf_path: Path, config: dict) -> dict:
    import anthropic  # imported here so offline mode works without the SDK

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    pdf_b64 = base64.standard_b64encode(pdf_path.read_bytes()).decode()
    categories = ", ".join(config["gl_categories"].keys())

    response = client.messages.create(
        model=config["model"],
        max_tokens=config["max_tokens"],
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_invoice"},
        messages=[{
            "role": "user",
            "content": [
                {"type": "document",
                 "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                {"type": "text", "text": PROMPT.format(categories=categories)},
            ],
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return dict(block.input)
    raise RuntimeError(f"No structured output returned for {pdf_path.name}")
