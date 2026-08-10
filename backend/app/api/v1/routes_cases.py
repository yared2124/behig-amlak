import base64
import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas_court import CaseRequest
from app.services.legal_engine import generate_court_report
from app.services.pdf_generator import create_pdf

router = APIRouter()

@router.post("/generate-court-letter")
async def generate_court_letter(request: CaseRequest):
    if not request.narrative or len(request.narrative) < 50:
        raise HTTPException(status_code=400, detail="Narrative must be at least 50 characters long.")
    
    plaintiff = {"name": request.plaintiff_name, "address": request.plaintiff_address}
    defendant = {"name": request.defendant_name, "address": request.defendant_address}
    
    try:
        report_json = generate_court_report(request.narrative, plaintiff, defendant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")
    
    report_id = str(uuid.uuid4())[:8]
    try:
        pdf_bytes = create_pdf(report_json, report_id, plaintiff, defendant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation Error: {str(e)}")
    
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    return {
        "report_id": report_id,
        "preview": report_json,
        "pdf_base64": pdf_base64
    }