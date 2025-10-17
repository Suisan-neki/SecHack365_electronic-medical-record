"""
セキュリティ強化された医療記録システム
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db, init_db
from models.patient import Patient, MedicalRecord, Encounter
from models.user import User, WebAuthnCredential, WebAuthnChallenge, Consent
from models.audit import AuditLog
from config import config
import json

def create_app(config_name=None):
    """アプリケーションファクトリー"""
    app = Flask(__name__)
    
    # 設定読み込み
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # ログ設定
    setup_logging(app)
    
    # データベース初期化
    init_db()
    
    # ログイン管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        db = next(get_db())
        return db.query(User).filter(User.id == user_id).first()
    
    # セキュリティヘッダー設定
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # 監査ログ記録
    @app.before_request
    def log_request():
        if current_user.is_authenticated:
            db = next(get_db())
            audit_log = AuditLog(
                user_id=str(current_user.id),
                action=request.method,
                resource_type=request.endpoint,
                resource_id=request.path,
                details=json.dumps({
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'timestamp': datetime.now().isoformat()
                }),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.add(audit_log)
            db.commit()
    
    # ルート定義
    @app.route('/')
    def index():
        return jsonify({
            'message': '医療記録システム API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/api/patients', methods=['GET'])
    def get_patients():
        """患者一覧取得"""
        if not current_user.is_authenticated:
            return jsonify({'error': '認証が必要です'}), 401
        
        db = next(get_db())
        patients = db.query(Patient).limit(50).all()
        
        return jsonify([{
            'id': p.id,
            'patient_id': p.patient_id,
            'name': p.name,
            'birth_date': p.birth_date.isoformat() if p.birth_date else None,
            'gender': p.gender,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in patients])
    
    @app.route('/api/patients/<patient_id>', methods=['GET'])
    def get_patient(patient_id):
        """患者詳細取得"""
        if not current_user.is_authenticated:
            return jsonify({'error': '認証が必要です'}), 401
        
        db = next(get_db())
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        
        if not patient:
            return jsonify({'error': '患者が見つかりません'}), 404
        
        return jsonify({
            'id': patient.id,
            'patient_id': patient.patient_id,
            'name': patient.name,
            'name_kana': patient.name_kana,
            'birth_date': patient.birth_date.isoformat() if patient.birth_date else None,
            'gender': patient.gender,
            'phone': patient.phone,
            'address': patient.address,
            'allergies': patient.allergies,
            'blood_type': patient.blood_type,
            'created_at': patient.created_at.isoformat() if patient.created_at else None
        })
    
    @app.route('/api/patients/<patient_id>/records', methods=['GET'])
    def get_patient_records(patient_id):
        """患者の医療記録取得"""
        if not current_user.is_authenticated:
            return jsonify({'error': '認証が必要です'}), 401
        
        db = next(get_db())
        records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
        
        return jsonify([{
            'id': r.id,
            'record_id': r.record_id,
            'diagnosis': r.diagnosis,
            'symptoms': r.symptoms,
            'treatment': r.treatment,
            'medications': json.loads(r.medications) if r.medications else None,
            'test_results': json.loads(r.test_results) if r.test_results else None,
            'doctor_notes': r.doctor_notes,
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in records])
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """ヘルスチェック"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    # エラーハンドラー
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'リソースが見つかりません'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '内部サーバーエラー'}), 500
    
    return app

def setup_logging(app):
    """ログ設定"""
    if not app.debug:
        # ログディレクトリ作成
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # ファイルハンドラー設定
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # フォーマッター設定
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
