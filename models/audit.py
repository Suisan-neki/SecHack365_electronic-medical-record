"""
監査ログモデル
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Text
from sqlalchemy.sql import func
from .database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    details = Column(Text)  # JSONBの代わりにTextで保存
    ip_address = Column(String(45))  # IPv6対応
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp(), index=True)
