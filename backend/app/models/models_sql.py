from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.core.database import Base

class ReportHistory(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    plaintiff_name = Column(String)
    defendant_name = Column(String)
    narrative = Column(Text)
    generated_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)