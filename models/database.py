"""
データベース接続とセッション管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# データベースURL設定
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://medical_user:medical_password@localhost:5432/medical_records')

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 開発時はSQLログを出力
    pool_pre_ping=True,  # 接続の生存確認
    pool_recycle=300,  # 接続のリサイクル間隔
)

# セッションファクトリー作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス作成
Base = declarative_base()

def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """データベーステーブルを作成"""
    Base.metadata.create_all(bind=engine)
