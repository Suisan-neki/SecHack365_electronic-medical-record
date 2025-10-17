"""
Fakerを使ったダミーデータ生成スクリプト
"""
import os
import sys
import json
from datetime import datetime, timedelta
from faker import Faker
import random

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, init_db
from models.patient import Patient, MedicalRecord, Encounter
from models.user import User, WebAuthnCredential, WebAuthnChallenge, Consent
from models.audit import AuditLog

# 日本語対応のFaker
fake = Faker('ja_JP')

def generate_patients(count=50):
    """患者データを生成"""
    patients = []
    for i in range(count):
        patient = Patient(
            patient_id=f"P{str(i+1).zfill(3)}",
            name=fake.name(),
            name_kana=fake.kana_name(),
            birth_date=fake.date_of_birth(minimum_age=0, maximum_age=100),
            gender=random.choice(['男性', '女性', 'その他']),
            phone=fake.phone_number(),
            address=fake.address(),
            allergies=random.choice(['なし', 'ペニシリン', '卵', '乳製品', 'ナッツ', '花粉']),
            blood_type=random.choice(['A型', 'B型', 'AB型', 'O型']),
            created_at=fake.date_time_between(start_date='-2y', end_date='now')
        )
        patients.append(patient)
    return patients

def generate_medical_records(patients, count_per_patient=3):
    """医療記録を生成"""
    records = []
    diagnoses = [
        '高血圧', '糖尿病', '風邪', 'インフルエンザ', '胃潰瘍', '胃炎',
        '腰痛', '頭痛', '不眠症', 'うつ病', 'アレルギー性鼻炎', '喘息'
    ]
    medications = [
        {'name': '高血圧治療薬', 'dosage': '1錠', 'frequency': '1日1回'},
        {'name': 'コレステロール降下薬', 'dosage': '1錠', 'frequency': '1日1回'},
        {'name': '解熱鎮痛薬', 'dosage': '2錠', 'frequency': '1日3回'},
        {'name': '抗生物質', 'dosage': '1錠', 'frequency': '1日2回'}
    ]
    
    for patient in patients:
        for i in range(random.randint(1, count_per_patient)):
            record = MedicalRecord(
                patient_id=patient.patient_id,
                record_id=f"R{patient.patient_id[1:]}{str(i+1).zfill(2)}",
                diagnosis=random.choice(diagnoses),
                symptoms=fake.text(max_nb_chars=200),
                treatment=fake.text(max_nb_chars=300),
                medications=json.dumps(random.sample(medications, random.randint(1, 3))),
                test_results=json.dumps({
                    'blood_pressure': {
                        'systolic': random.randint(100, 180),
                        'diastolic': random.randint(60, 110)
                    },
                    'cholesterol': {
                        'ldl': random.randint(80, 200),
                        'hdl': random.randint(30, 80)
                    }
                }),
                doctor_notes=fake.text(max_nb_chars=500),
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            records.append(record)
    return records

def generate_encounters(patients, count_per_patient=2):
    """診療記録を生成"""
    encounters = []
    encounter_types = ['初診', '再診', '定期診察', '緊急診察', '術後診察']
    
    for patient in patients:
        for i in range(random.randint(1, count_per_patient)):
            encounter = Encounter(
                patient_id=patient.patient_id,
                encounter_id=f"E{patient.patient_id[1:]}{str(i+1).zfill(2)}",
                encounter_date=fake.date_time_between(start_date='-6m', end_date='now'),
                encounter_type=random.choice(encounter_types),
                chief_complaint=fake.text(max_nb_chars=100),
                vital_signs=json.dumps({
                    'temperature': round(random.uniform(36.0, 39.0), 1),
                    'pulse': random.randint(60, 120),
                    'blood_pressure': f"{random.randint(100, 180)}/{random.randint(60, 110)}",
                    'respiratory_rate': random.randint(12, 20)
                }),
                assessment=fake.text(max_nb_chars=200),
                plan=fake.text(max_nb_chars=200),
                provider_id=f"DR{random.randint(1, 10):03d}"
            )
            encounters.append(encounter)
    return encounters

def generate_users():
    """ユーザーデータを生成"""
    users = []
    roles = ['doctor', 'nurse', 'admin', 'patient']
    
    for i, role in enumerate(roles):
        user = User(
            username=f"{role}1",
            password_hash="$pbkdf2-sha256$29000$dummy$dummy_hash",  # ダミーハッシュ
            salt="dummy_salt",
            role=role,
            mfa_enabled=random.choice([True, False]),
            mfa_secret=fake.lexify(text='????????????????????????????????') if random.choice([True, False]) else None,
            mfa_backup_codes=json.dumps([fake.numerify(text='########') for _ in range(8)]) if random.choice([True, False]) else None,
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
            last_login=fake.date_time_between(start_date='-30d', end_date='now') if random.choice([True, False]) else None,
            is_active=True
        )
        users.append(user)
    return users

def generate_audit_logs(count=100):
    """監査ログを生成"""
    logs = []
    actions = ['login', 'logout', 'create_patient', 'update_patient', 'view_record', 'delete_record']
    resource_types = ['patient', 'medical_record', 'user', 'consent']
    
    for i in range(count):
        log = AuditLog(
            user_id=f"user{random.randint(1, 10)}",
            action=random.choice(actions),
            resource_type=random.choice(resource_types),
            resource_id=f"ID{random.randint(1, 1000):04d}",
            details=json.dumps({
                'ip_address': fake.ipv4(),
                'user_agent': fake.user_agent(),
                'additional_info': fake.text(max_nb_chars=100)
            }),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
            created_at=fake.date_time_between(start_date='-30d', end_date='now')
        )
        logs.append(log)
    return logs

def main():
    """メイン処理"""
    print("ダミーデータ生成を開始します...")
    
    # データベース初期化
    init_db()
    
    # セッション作成
    db = SessionLocal()
    
    try:
        # 患者データ生成
        print("患者データを生成中...")
        patients = generate_patients(50)
        db.add_all(patients)
        db.commit()
        
        # 医療記録生成
        print("医療記録を生成中...")
        records = generate_medical_records(patients, 3)
        db.add_all(records)
        db.commit()
        
        # 診療記録生成
        print("診療記録を生成中...")
        encounters = generate_encounters(patients, 2)
        db.add_all(encounters)
        db.commit()
        
        # ユーザーデータ生成
        print("ユーザーデータを生成中...")
        users = generate_users()
        db.add_all(users)
        db.commit()
        
        # 監査ログ生成
        print("監査ログを生成中...")
        logs = generate_audit_logs(100)
        db.add_all(logs)
        db.commit()
        
        print("ダミーデータ生成が完了しました！")
        print(f"患者数: {len(patients)}")
        print(f"医療記録数: {len(records)}")
        print(f"診療記録数: {len(encounters)}")
        print(f"ユーザー数: {len(users)}")
        print(f"監査ログ数: {len(logs)}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
