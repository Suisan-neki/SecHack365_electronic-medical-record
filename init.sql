-- 医療記録システム用データベース初期化スクリプト

-- スキーマ作成
CREATE SCHEMA IF NOT EXISTS ehr_system;
CREATE SCHEMA IF NOT EXISTS info_sharing;

-- 基本テーブル作成
CREATE TABLE IF NOT EXISTS ehr_system.patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_kana VARCHAR(100),
    birth_date DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    allergies TEXT,
    blood_type VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ehr_system.medical_records (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES ehr_system.patients(patient_id),
    record_id VARCHAR(50) UNIQUE NOT NULL,
    diagnosis TEXT,
    symptoms TEXT,
    treatment TEXT,
    medications JSONB,
    test_results JSONB,
    doctor_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ehr_system.encounters (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES ehr_system.patients(patient_id),
    encounter_id VARCHAR(50) UNIQUE NOT NULL,
    encounter_date TIMESTAMP NOT NULL,
    encounter_type VARCHAR(50),
    chief_complaint TEXT,
    vital_signs JSONB,
    assessment TEXT,
    plan TEXT,
    provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 情報共有システム用テーブル
CREATE TABLE IF NOT EXISTS info_sharing.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    mfa_backup_codes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS info_sharing.webauthn_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES info_sharing.users(id),
    credential_id VARCHAR(255) UNIQUE NOT NULL,
    public_key TEXT NOT NULL,
    sign_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS info_sharing.webauthn_challenges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES info_sharing.users(id),
    challenge_type VARCHAR(50) NOT NULL,
    challenge_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS info_sharing.consents (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    granted BOOLEAN NOT NULL,
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP,
    consent_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 監査ログテーブル
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON ehr_system.patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_id ON ehr_system.medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_patient_id ON ehr_system.encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON info_sharing.users(username);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- 権限設定
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ehr_system TO medical_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA info_sharing TO medical_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medical_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ehr_system TO medical_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA info_sharing TO medical_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO medical_user;
