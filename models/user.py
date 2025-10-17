"""
ユーザー認証モデル
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'info_sharing'}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    mfa_backup_codes = Column(Text)  # JSONBの代わりにTextで保存
    created_at = Column(DateTime, default=func.current_timestamp())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # リレーション
    webauthn_credentials = relationship("WebAuthnCredential", back_populates="user")
    webauthn_challenges = relationship("WebAuthnChallenge", back_populates="user")

class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"
    __table_args__ = {'schema': 'info_sharing'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('info_sharing.users.id'), nullable=False)
    credential_id = Column(String(255), unique=True, nullable=False)
    public_key = Column(Text, nullable=False)
    sign_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # リレーション
    user = relationship("User", back_populates="webauthn_credentials")

class WebAuthnChallenge(Base):
    __tablename__ = "webauthn_challenges"
    __table_args__ = {'schema': 'info_sharing'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('info_sharing.users.id'), nullable=False)
    challenge_type = Column(String(50), nullable=False)
    challenge_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    expires_at = Column(DateTime, nullable=False)
    
    # リレーション
    user = relationship("User", back_populates="webauthn_challenges")

class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = {'schema': 'info_sharing'}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), nullable=False)
    consent_type = Column(String(50), nullable=False)
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    consent_data = Column(Text)  # JSONBの代わりにTextで保存
    created_at = Column(DateTime, default=func.current_timestamp())
