# (feat): Court letter generation endpoint.
# Description: Accepts narrative, runs RAG, returns JSON preview.
# PDF generation is temporarily disabled (install weasyprint to re-enable).

import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas_court import CaseRequest
from app.services.legal_engine import generate_court_report

# IMPORTANT: PDF generation is disabled for now.
# To enable, install weasyprint and uncomment the import and pdf_base64 logic.
# from app.services.pdf_generator import create_pdf
# import base64

router = APIRouter()

@router.post("/generate-court-letter")
async def generate_court_letter(request: CaseRequest):
    """
    Generates a court letter based on the user's legal narrative.
    Returns a JSON preview and a placeholder for PDF (PDF disabled).
    """
    # Validate input
    if not request.narrative or len(request.narrative) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative must be at least 50 characters long."
        )

    # Prepare party data
    plaintiff = {
        "name": request.plaintiff_name,
        "address": request.plaintiff_address
    }
    defendant = {
        "name": request.defendant_name,
        "address": request.defendant_address
    }

    # Step 1: Run the LangGraph engine (Issue Spotting -> RAG -> Generate JSON)
    try:
        report_json = generate_court_report(request.narrative, plaintiff, defendant)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Engine Error: {str(e)}"
        )

    # Step 2: Generate a unique report ID
    report_id = str(uuid.uuid4())[:8]

    # Step 3: PDF generation is temporarily disabled.
    # Uncomment the following lines when weasyprint is installed.
    # try:
    #     pdf_bytes = create_pdf(report_json, report_id, plaintiff, defendant)
    #     pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"PDF Generation Error: {str(e)}"
    #     )
    pdf_base64 = ""  # Placeholder – no PDF available

    # Return the response
    return {
        "report_id": report_id,
        "preview": report_json,
        "pdf_base64": pdf_base64,
        "message": "PDF generation is temporarily disabled. The court letter preview is available in JSON format. Install weasyprint to enable PDF export."
    }