from pydantic import BaseModel
from typing import List, Optional

class CourtLetterSchema(BaseModel):
    case_summary: str
    statement_of_facts: List[str]
    legal_grounds: List[str]
    relief_sought: List[str]
    pre_conditions: List[str]
    annexures: List[str]
    verification: str

class CaseRequest(BaseModel):
    narrative: str
    plaintiff_name: str
    plaintiff_address: str
    defendant_name: str
    defendant_address: str