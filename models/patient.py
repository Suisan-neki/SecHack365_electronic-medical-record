"""
患者情報モデル
"""
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {'schema': 'ehr_system'}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_kana = Column(String(100))
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    allergies = Column(Text)
    blood_type = Column(String(10))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # リレーション
    medical_records = relationship("MedicalRecord", back_populates="patient")
    encounters = relationship("Encounter", back_populates="patient")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    __table_args__ = {'schema': 'ehr_system'}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('ehr_system.patients.patient_id'), nullable=False)
    record_id = Column(String(50), unique=True, nullable=False, index=True)
    diagnosis = Column(Text)
    symptoms = Column(Text)
    treatment = Column(Text)
    medications = Column(Text)  # JSONBの代わりにTextで保存
    test_results = Column(Text)  # JSONBの代わりにTextで保存
    doctor_notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # リレーション
    patient = relationship("Patient", back_populates="medical_records")

class Encounter(Base):
    __tablename__ = "encounters"
    __table_args__ = {'schema': 'ehr_system'}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('ehr_system.patients.patient_id'), nullable=False)
    encounter_id = Column(String(50), unique=True, nullable=False, index=True)
    encounter_date = Column(DateTime, nullable=False)
    encounter_type = Column(String(50))
    chief_complaint = Column(Text)
    vital_signs = Column(Text)  # JSONBの代わりにTextで保存
    assessment = Column(Text)
    plan = Column(Text)
    provider_id = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # リレーション
    patient = relationship("Patient", back_populates="encounters")
