import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime

template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(template_dir))

def create_pdf(report_data: dict, report_id: str, plaintiff: dict, defendant: dict) -> bytes:
    template = env.get_template("court_letter.html")
    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "NotoSansEthiopic.ttf")
    
    html_content = template.render(
        report_id=report_id,
        generated_date=datetime.now().strftime("%B %d, %Y"),
        plaintiff_name=plaintiff["name"],
        plaintiff_address=plaintiff["address"],
        defendant_name=defendant["name"],
        defendant_address=defendant["address"],
        case_summary=report_data.get("case_summary", ""),
        statement_of_facts=report_data.get("statement_of_facts", []),
        legal_grounds=report_data.get("legal_grounds", []),
        relief_sought=report_data.get("relief_sought", []),
        pre_conditions=report_data.get("pre_conditions", []),
        annexures=report_data.get("annexures", []),
        verification=report_data.get("verification", ""),
        app_name="በህግ አምላክ (Behèg Amlak)",
        font_path=font_path
    )
    pdf_file = HTML(string=html_content).write_pdf()
    return pdf_file