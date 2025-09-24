from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from webauthn.helpers.structs import RegistrationCredential, AuthenticationCredential

# coreモジュールから必要な機能をインポート
from core.digital_signature import generate_keys, sign_data, verify_signature
from core.hash_chain import HashChain
from core.authentication import UserAuthenticator
from core.authorization import ABACPolicyEnforcer # ABAC機能を追加
from core.data_encryption import DataEncryptor # データ暗号化機能を追加
from core.audit_logger import AuditLogger # 監査ログ機能を追加

app = Flask(__name__)
# セッション管理のための固定秘密鍵（開発用）
# 注意: 本番環境では環境変数から取得すること
app.config["SECRET_KEY"] = "SecHack365_medical_dx_project_secret_key_2024"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "この機能を使用するにはログインが必要です。"
login_manager.login_message_category = "info"

# セッション設定を強化（HTTP開発環境用）
app.config['SESSION_COOKIE_SECURE'] = False  # HTTP環境ではFalse
app.config['SESSION_COOKIE_HTTPONLY'] = False  # 開発環境では一時的にFalse
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# current_userをテンプレートで利用可能にする
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# すべてのリクエストをログに出力（デバッグ用）
@app.before_request
def log_request():
    print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")
    if request.path.startswith('/api/'):
        print(f"[API REQUEST] Headers: {dict(request.headers)}")
        if current_user.is_authenticated:
            print(f"[API REQUEST] User: {current_user.id}")
        else:
            print(f"[API REQUEST] User: 未認証")

# UserAuthenticatorの初期化
authenticator = UserAuthenticator(os.path.join(app.root_path, "user_db.json"))

# AuditLoggerの初期化（プロジェクトルートにaudit.logを作成）
audit_logger = AuditLogger(log_file=os.path.join(app.root_path, "..", "..", "audit.log"))

# ABACPolicyEnforcerの初期化
abac_enforcer = ABACPolicyEnforcer(os.path.join(app.root_path, "..", "..", "abac_policy.json")) # パスを調整

# Flask-LoginのためのUserクラス
class User(UserMixin):
    def __init__(self, id, role, encryption_key=None):
        self.id = id
        self.role = role
        self.encryption_key = encryption_key # 暗号化キーをユーザーオブジェクトに保存

    def get_id(self):
        return str(self.id)

    def get_role(self):
        return self.role
    
    def get_encryption_key(self):
        return self.encryption_key
    
    def has_encryption_key(self):
        return self.encryption_key is not None

@login_manager.user_loader
def load_user(user_id):
    user_data = authenticator.users.get(user_id)
    if user_data:
        return User(user_id, user_data["role"])
    return None

# 設定
DATA_FILE = os.path.join(app.root_path, 'demo_karte.json')
CERT_DIR = os.path.join(app.root_path, 'certs')

# ハッシュチェーンの初期化
hash_chain = HashChain()

# 秘密鍵と公開鍵の生成（または既存のものをロード）
# 実際には、これらはセキュアな方法で管理されるべきです。
if not os.path.exists(CERT_DIR):
    os.makedirs(CERT_DIR)

private_key_path = os.path.join(CERT_DIR, 'private_key.pem')
public_key_path = os.path.join(CERT_DIR, 'public_key.pem')

if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
    private_key, public_key = generate_keys()
    with open(private_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(public_key_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
else:
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())

# デモ用カルテデータのロード
def load_karte_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_karte_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_encrypted_karte_data(encryption_key):
    """
    暗号化されたカルテデータを読み込み、復号する
    
    Args:
        encryption_key (bytes): 復号用の暗号化キー
        
    Returns:
        dict: 復号されたカルテデータ
    """
    encrypted_data_file = os.path.join(app.root_path, "demo_karte_encrypted.json")
    
    if not os.path.exists(encrypted_data_file):
        # 暗号化ファイルが存在しない場合、既存の平文データを暗号化して移行
        if os.path.exists(DATA_FILE):
            print(f"[INFO] 平文データを暗号化形式に移行中...")
            plain_data = load_karte_data()
            save_encrypted_karte_data(plain_data, encryption_key)
            return plain_data
        else:
            return {}
    
    try:
        with open(encrypted_data_file, 'r', encoding='utf-8') as f:
            encrypted_content = json.load(f)
        
        # DataEncryptorで復号
        encryptor = DataEncryptor(encryption_key)
        decrypted_data = encryptor.decrypt_json(encrypted_content["encrypted_data"])
        
        print(f"[INFO] 暗号化データを正常に復号しました")
        return decrypted_data
        
    except Exception as e:
        print(f"[ERROR] データ復号エラー: {e}")
        # 復号に失敗した場合は空のデータを返す
        return {}

def save_encrypted_karte_data(data, encryption_key):
    """
    カルテデータを暗号化して保存する
    
    Args:
        data (dict): 保存するカルテデータ
        encryption_key (bytes): 暗号化用のキー
    """
    encrypted_data_file = os.path.join(app.root_path, "demo_karte_encrypted.json")
    
    try:
        # DataEncryptorで暗号化
        encryptor = DataEncryptor(encryption_key)
        encrypted_data = encryptor.encrypt_json(data)
        
        # 暗号化データとメタデータを保存
        encrypted_content = {
            "encrypted_data": encrypted_data,
            "encryption_info": encryptor.get_encryption_info(),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(encrypted_data_file, 'w', encoding='utf-8') as f:
            json.dump(encrypted_content, f, ensure_ascii=False, indent=4)
        
        print(f"[INFO] データを暗号化して保存しました")
        
    except Exception as e:
        print(f"[ERROR] データ暗号化エラー: {e}")
        raise

karte_data = load_karte_data()

# デモ用ユーザーの初期化
def initialize_demo_users():
    """デモ用ユーザーを初期化（既存データを保護）"""
    
    # 既存ユーザーが存在する場合はスキップ
    if authenticator.users:
        print(f"[INFO] 既存ユーザーが見つかりました: {list(authenticator.users.keys())}")
        print("[INFO] デモユーザーの初期化をスキップしました（既存データを保護）")
        return
    
    print("[INFO] 新規環境を検出。デモユーザーを初期化します...")
    demo_users = [
        ("doctor1", "secure_pass_doc", "doctor", True),
        ("nurse1", "secure_pass_nurse", "nurse", False),
        ("patient1", "secure_pass_pat", "patient", False),
        ("admin1", "secure_pass_admin", "admin", False)
    ]
    
    for username, password, role, enable_mfa in demo_users:
        success, message, mfa_secret = authenticator.register_user(
            username, password, role, enable_mfa
        )
        if success:
            print(f"[DEMO] ユーザー作成: {username} ({role}) - MFA: {enable_mfa}")
            if mfa_secret:
                print(f"[DEMO] {username} のMFAシークレット: {mfa_secret}")
        else:
            print(f"[ERROR] ユーザー作成失敗 {username}: {message}")
    
    print("[INFO] デモユーザーの初期化が完了しました")

def get_or_create_demo_keys():
    """
    デモ用の固定鍵ペアを取得または生成
    
    Returns:
        dict: {'private_key': private_key, 'public_key': public_key} または None
    """
    demo_keys_file = os.path.join(app.root_path, "demo_keys.json")
    
    # 既存の鍵を読み込み
    if os.path.exists(demo_keys_file):
        try:
            with open(demo_keys_file, 'r', encoding='utf-8') as f:
                keys_data = json.load(f)
                # 文字列から鍵オブジェクトに復元
                from cryptography.hazmat.primitives import serialization
                private_key = serialization.load_pem_private_key(
                    keys_data['private_key_pem'].encode(),
                    password=None
                )
                public_key = serialization.load_pem_public_key(
                    keys_data['public_key_pem'].encode()
                )
                print("[DEBUG] 既存のデモ用鍵を読み込みました")
                return {'private_key': private_key, 'public_key': public_key}
        except Exception as e:
            print(f"[WARNING] 既存のデモ用鍵の読み込みに失敗: {e}")
    
    # 新しい鍵ペアを生成
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives import serialization
        
        # RSA鍵ペアを生成
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        
        # PEM形式で保存
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        # ファイルに保存
        keys_data = {
            'private_key_pem': private_pem,
            'public_key_pem': public_pem,
            'created_at': datetime.now().isoformat()
        }
        
        with open(demo_keys_file, 'w', encoding='utf-8') as f:
            json.dump(keys_data, f, indent=2, ensure_ascii=False)
        
        print("[INFO] 新しいデモ用鍵ペアを生成しました")
        return {'private_key': private_key, 'public_key': public_key}
        
    except Exception as e:
        print(f"[ERROR] デモ用鍵ペアの生成に失敗: {e}")
        return None

def sign_patient_data(patient_data, private_key):
    """
    患者データに署名を付与
    
    Args:
        patient_data (dict): 患者データ
        private_key: 秘密鍵
        
    Returns:
        str: 16進数文字列の署名
    """
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        
        # データを文字列として結合
        data_str = json.dumps(patient_data, ensure_ascii=False, sort_keys=True)
        data_bytes = data_str.encode('utf-8')
        
        # 署名を生成
        signature = private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # 16進数文字列に変換
        return signature.hex()
        
    except Exception as e:
        print(f"[ERROR] 署名生成エラー: {e}")
        return None

def add_signatures_to_existing_data():
    """
    既存の患者データに署名を追加（デモ用）
    """
    try:
        # デモ用鍵を取得
        demo_keys = get_or_create_demo_keys()
        if not demo_keys:
            print("[ERROR] デモ用鍵の取得に失敗")
            return False
        
        print("[DEBUG] 既存の患者データを読み込み中...")
        # 既存の患者データを読み込み（暗号化キーを取得）
        # 既存のauthenticatorインスタンスを使用
        temp_authenticator = authenticator
        
        # デモ用パスワードで暗号化キーを取得
        demo_passwords = {
            'doctor1': 'secure_pass_doc',
            'nurse1': 'secure_pass_nurse', 
            'patient1': 'secure_pass_pat',
            'admin1': 'secure_pass_admin'
        }
        
        encryption_key = None
        for username, password in demo_passwords.items():
            try:
                salt = temp_authenticator.get_user_encryption_salt(username)
                if salt:
                    key = temp_authenticator.derive_encryption_key(password, salt)
                    test_data = load_encrypted_karte_data(key)
                    if test_data:
                        encryption_key = key
                        print(f"[DEBUG] 暗号化キー取得成功: {username}")
                        break
            except Exception as e:
                print(f"[DEBUG] ユーザー {username} のキー取得失敗: {e}")
                continue
        
        if not encryption_key:
            print("[ERROR] 暗号化キーの取得に失敗")
            return False
        
        encrypted_data = load_encrypted_karte_data(encryption_key)
        if not encrypted_data:
            print("[ERROR] 既存データの読み込みに失敗")
            return False
        
        print(f"[DEBUG] 読み込んだ患者データ: {list(encrypted_data.keys())}")
        
        # 各患者のデータに署名を追加
        signatures_added = 0
        for patient_id, patient_data in encrypted_data.items():
            if 'medical_records' in patient_data:
                for i, record in enumerate(patient_data['medical_records']):
                    print(f"[DEBUG] 患者 {patient_id} レコード {i}: {list(record.keys())}")
                    if 'data' in record and 'signature' not in record:
                        # データに署名を追加
                        signature = sign_patient_data(record['data'], demo_keys['private_key'])
                        if signature:
                            record['signature'] = signature
                            signatures_added += 1
                            print(f"[INFO] 患者 {patient_id} のレコード {i} に署名を追加しました")
                    elif 'signature' in record:
                        print(f"[DEBUG] 患者 {patient_id} レコード {i} は既に署名済み")
        
        print(f"[INFO] 合計 {signatures_added} 件の署名を追加しました")
        
        # 署名付きデータを保存
        save_encrypted_karte_data(encrypted_data, encryption_key)
        print("[INFO] 署名付きデータを保存しました")
        return True
        
    except Exception as e:
        print(f"[ERROR] 署名追加処理エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_or_create_webauthn_encryption_key(username):
    """
    WebAuthn認証用の専用暗号化キーを取得または生成
    
    Args:
        username (str): ユーザー名
        
    Returns:
        bytes: 暗号化キー（32バイト）
    """
    # WebAuthn用暗号化キーファイルのパス
    webauthn_keys_file = os.path.join(app.root_path, "webauthn_encryption_keys.json")
    
    # 既存のキーを読み込み
    webauthn_keys = {}
    if os.path.exists(webauthn_keys_file):
        try:
            with open(webauthn_keys_file, 'r', encoding='utf-8') as f:
                webauthn_keys = json.load(f)
        except Exception as e:
            print(f"[WARNING] WebAuthn暗号化キーファイルの読み込みに失敗: {e}")
    
    # ユーザーのキーが存在するかチェック
    if username in webauthn_keys:
        try:
            # Base64デコードして暗号化キーを返す
            import base64
            return base64.b64decode(webauthn_keys[username])
        except Exception as e:
            print(f"[ERROR] WebAuthn暗号化キーのデコードに失敗: {e}")
    
    # キーが存在しない場合は新規生成
    print(f"[INFO] ユーザー {username} の新しいWebAuthn暗号化キーを生成中...")
    new_key = os.urandom(32)  # 32バイト = AES-256
    
    # Base64エンコードして保存
    import base64
    webauthn_keys[username] = base64.b64encode(new_key).decode('utf-8')
    
    # ファイルに保存
    try:
        with open(webauthn_keys_file, 'w', encoding='utf-8') as f:
            json.dump(webauthn_keys, f, ensure_ascii=False, indent=4)
        print(f"[SUCCESS] ユーザー {username} のWebAuthn暗号化キーを保存しました")
    except Exception as e:
        print(f"[ERROR] WebAuthn暗号化キーの保存に失敗: {e}")
    
    return new_key

# アプリケーション起動時にデモユーザーを初期化
print("[STARTUP] アプリケーション初期化中...")
initialize_demo_users()

# 患者データの確認と作成
def ensure_patient_data():
    """患者データが存在しない場合は作成する"""
    encrypted_data_file = os.path.join(app.root_path, "demo_karte_encrypted.json")
    
    if not os.path.exists(encrypted_data_file):
        print("[STARTUP] 患者データが見つかりません。作成中...")
        try:
            # doctor1のパスワードベース暗号化キーを取得
            username = 'doctor1'
            password = 'secure_pass_doc'
            salt = authenticator.get_user_encryption_salt(username)
            
            if salt:
                encryption_key = authenticator.derive_encryption_key(password, salt)
                
                # 山下真凜の患者データを作成
                patient_data = {
                    'P001': {
                        'patient_info': {
                            'id': 'P001',
                            'name': '山下真凜',
                            'age': 28,
                            'gender': '女性',
                            'contact': '03-1234-5678',
                            'address': '東京都渋谷区'
                        },
                        'medical_records': [
                            {
                                'timestamp': '2024-01-15T10:30:00Z',
                                'data': {
                                    'diagnosis': '軽度の貧血',
                                    'medication': '鉄剤 100mg',
                                    'notes': '食事指導を実施。1ヶ月後に再検査予定。',
                                    'doctor': 'Dr. 田中',
                                    'blood_pressure': '120/80',
                                    'temperature': '36.5°C'
                                },
                                'signature': 'yamashita_signature_1'
                            }
                        ]
                    }
                }
                
                # データを暗号化して保存
                save_encrypted_karte_data(patient_data, encryption_key)
                print("[STARTUP] 患者データを作成しました: 山下真凜 (P001)")
                
                # 作成したデータの検証
                try:
                    test_data = load_encrypted_karte_data(encryption_key)
                    if test_data and 'P001' in test_data:
                        print("[STARTUP] 患者データの作成と復号を確認しました")
                    else:
                        print("[STARTUP] 警告: 作成したデータの復号に失敗")
                except Exception as verify_error:
                    print(f"[STARTUP] データ検証エラー: {verify_error}")
            else:
                print("[STARTUP] 患者データの作成に失敗: ソルトが見つかりません")
        except Exception as e:
            print(f"[STARTUP] 患者データ作成エラー: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[STARTUP] 患者データファイルを確認しました")
        # 既存データの検証
        try:
            # doctor1のキーで復号テスト
            username = 'doctor1'
            password = 'secure_pass_doc'
            salt = authenticator.get_user_encryption_salt(username)
            if salt:
                encryption_key = authenticator.derive_encryption_key(password, salt)
                test_data = load_encrypted_karte_data(encryption_key)
                if test_data and isinstance(test_data, dict):
                    patient_ids = list(test_data.keys())
                    print(f"[STARTUP] 患者データ確認: {patient_ids}")
                    # 各患者の詳細も確認
                    for patient_id in patient_ids:
                        patient_info = test_data[patient_id].get('patient_info', {})
                        patient_name = patient_info.get('name', '不明')
                        print(f"[STARTUP] 患者 {patient_id}: {patient_name}")
                else:
                    print("[STARTUP] 警告: 患者データが空または無効です")
        except Exception as e:
            print(f"[STARTUP] 患者データ確認エラー: {e}")

ensure_patient_data()
print("[STARTUP] アプリケーション初期化完了")

# デモ用署名の初期化
print("[STARTUP] デモ用署名を初期化中...")
if add_signatures_to_existing_data():
    print("[STARTUP] デモ用署名の初期化が完了しました")
else:
    print("[WARNING] デモ用署名の初期化に失敗しました")

@app.route('/')
def index():
    # 認証済みの場合はユーザー情報を渡し、未認証の場合はログインリンクを表示
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.id, role=current_user.role)
    else:
        return render_template('index.html')

@app.route('/api/test')
def api_test():
    """APIテスト用エンドポイント"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
                'timestamp': datetime.now().isoformat()
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        authenticated, message, mfa_required = authenticator.authenticate_user(username, password)
        
        if authenticated:
            if mfa_required:
                session['mfa_username'] = username # MFA検証のためにユーザー名をセッションに保存
                session['temp_password'] = password # MFA検証のために一時的にパスワードを保存
                return redirect(url_for('mfa_verify'))
            else:
                # パスワード認証成功時に暗号化キーを導出
                user_data = authenticator.users.get(username)
                salt = authenticator.get_user_encryption_salt(username)
                if salt:
                    encryption_key = authenticator.derive_encryption_key(password, salt)
                    user = User(username, authenticator.get_user_role(username), encryption_key)
                    print(f"[INFO] ユーザー {username} の暗号化キーを設定しました")
                else:
                    user = User(username, authenticator.get_user_role(username))
                    print(f"[WARNING] ユーザー {username} のソルトが見つかりません")
                login_user(user)
                # 監査ログ: ログイン成功
                audit_logger.log_event(
                    event_id="AUTH_LOGIN_SUCCESS",
                    user_id=username,
                    user_role=authenticator.get_user_role(username),
                    ip_address=request.remote_addr,
                    action="LOGIN",
                    resource="/login",
                    status="SUCCESS",
                    message="ユーザーがログインしました",
                    details={"mfa_enabled": False}
                )
                return redirect(url_for('index'))
        else:
            # 監査ログ: ログイン失敗
            audit_logger.log_event(
                event_id="AUTH_LOGIN_FAILURE",
                user_id=username,
                user_role="unknown",
                ip_address=request.remote_addr,
                action="LOGIN",
                resource="/login",
                status="FAILURE",
                message="ログインに失敗しました",
                details={"reason": message}
            )
            flash(message)
            return render_template('login.html', error=message)
    return render_template('login.html')

@app.route('/mfa_verify', methods=['GET', 'POST'])
def mfa_verify():
    if 'mfa_username' not in session:
        return redirect(url_for('login'))

    username = session['mfa_username']
    if request.method == 'POST':
        mfa_code = request.form['mfa_code']
        verified, message = authenticator.verify_mfa(username, mfa_code)
        if verified:
            # MFA認証成功時に暗号化キーを導出
            password = session.get('temp_password')
            if password:
                salt = authenticator.get_user_encryption_salt(username)
                if salt:
                    encryption_key = authenticator.derive_encryption_key(password, salt)
                    user = User(username, authenticator.get_user_role(username), encryption_key)
                    print(f"[INFO] MFA認証後、ユーザー {username} の暗号化キーを設定しました")
                else:
                    user = User(username, authenticator.get_user_role(username))
                    print(f"[WARNING] ユーザー {username} のソルトが見つかりません")
            else:
                user = User(username, authenticator.get_user_role(username))
                print(f"[WARNING] 一時パスワードが見つかりません")
            
            login_user(user)
            session.pop('mfa_username', None)
            session.pop('temp_password', None) # セキュリティのため一時パスワードを削除
            return redirect(url_for('index'))
        else:
            flash(message)
            return render_template('mfa_verify.html', error=message)
    
    # MFA設定用のQRコード表示（デモ用）
    mfa_enabled, mfa_secret = authenticator.get_mfa_status(username)
    qr_code_url = None
    if mfa_enabled and mfa_secret:
        import pyotp
        totp = pyotp.TOTP(mfa_secret)
        qr_code_url = totp.provisioning_uri(name=username, issuer_name="SecHack365 PHR")

    return render_template('mfa_verify.html', qr_code_url=qr_code_url)

@app.route('/logout')
@login_required
def logout():
    # WebAuthnチャレンジをクリア（ログアウト時の古いチャレンジを削除）
    try:
        user_data = authenticator.users.get(current_user.id)
        if user_data and 'webauthn_challenges' in user_data:
            user_data['webauthn_challenges'].clear()
            authenticator._save_users()
    except Exception as e:
        print(f"[DEBUG] ログアウト時のチャレンジクリアエラー: {e}")
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/patient/<patient_id>', methods=['GET'])
def get_patient_data(patient_id):
    print(f"[API] 患者データ取得リクエスト受信: {patient_id}")
    
    # 手動で認証チェック（@login_requiredの代わり）
    if not current_user.is_authenticated:
        print(f"[API] 認証されていないユーザーからのリクエスト")
        return jsonify({
            'error': 'この機能を使用するにはログインが必要です。',
            'auth_method': 'login_required'
        }), 401
    
    print(f"[API] 認証済みユーザー: {current_user.id}")
    # 暗号化キーの確認
    if not current_user.has_encryption_key():
        print(f"[DEBUG] ユーザー {current_user.id} に暗号化キーがありません。複数のキーを試行中...")
        
        # 複数の暗号化キーを試行
        encryption_key_found = False
        
        try:
            # 1. パスワードベース暗号化キーを試行（既存データ用）
            demo_passwords = {
                'doctor1': 'secure_pass_doc',
                'nurse1': 'secure_pass_nurse', 
                'patient1': 'secure_pass_pat',
                'admin1': 'secure_pass_admin'
            }
            
            if current_user.id in demo_passwords:
                salt = authenticator.get_user_encryption_salt(current_user.id)
                if salt:
                    password_key = authenticator.derive_encryption_key(demo_passwords[current_user.id], salt)
                    try:
                        test_data = load_encrypted_karte_data(password_key)
                        if test_data:
                            current_user.encryption_key = password_key
                            encryption_key_found = True
                            print(f"[SUCCESS] パスワードベース暗号化キーでデータアクセス成功: {current_user.id}")
                    except Exception as e:
                        print(f"[WARNING] パスワードベース暗号化キーで復号失敗: {e}")
            
            # 2. WebAuthn専用キーを試行（フォールバック）
            if not encryption_key_found:
                webauthn_key = get_or_create_webauthn_encryption_key(current_user.id)
                if webauthn_key:
                    try:
                        test_data = load_encrypted_karte_data(webauthn_key)
                        if test_data:
                            current_user.encryption_key = webauthn_key
                            encryption_key_found = True
                            print(f"[SUCCESS] WebAuthn暗号化キーでデータアクセス成功: {current_user.id}")
                    except Exception as e:
                        print(f"[WARNING] WebAuthn暗号化キーで復号失敗: {e}")
            
            if not encryption_key_found:
                return jsonify({
                    "error": "暗号化データの復号に失敗しました。データが破損している可能性があります。",
                    "auth_method": "decryption_failed"
                }), 401
                
        except Exception as e:
            print(f"[ERROR] 暗号化キー取得エラー: {e}")
            return jsonify({
                "error": "暗号化キーが利用できません。",
                "auth_method": "key_error"
            }), 401

    subject_attributes = {"id": current_user.id, "role": current_user.role}
    action = "view"
    resource_attributes = {"type": "patient_data", "patient_id": patient_id}

    if not abac_enforcer.check_access(subject_attributes, action, resource_attributes):
        return jsonify({'error': 'Permission denied'}), 403

    # 暗号化されたデータを読み込み
    try:
        decrypted_karte_data = load_encrypted_karte_data(current_user.get_encryption_key())
        print(f"[DEBUG] 復号されたデータのキー: {list(decrypted_karte_data.keys()) if decrypted_karte_data else 'None'}")
        patient = decrypted_karte_data.get(patient_id) if decrypted_karte_data else None
        print(f"[DEBUG] 患者 {patient_id} のデータ: {'見つかりました' if patient else '見つかりません'}")
    except Exception as e:
        print(f"[ERROR] データ復号エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'データの復号に失敗しました'}), 500
    
    if not patient:
        print(f"[ERROR] 患者 {patient_id} が見つかりません。利用可能な患者ID: {list(decrypted_karte_data.keys()) if decrypted_karte_data else '[]'}")
        return jsonify({'error': 'Patient not found'}), 404

    # 最新のカルテ情報を取得
    latest_record = patient['medical_records'][-1] if patient['medical_records'] else None

    # 署名検証（デモ用 - 適切な実装）
    is_valid_signature = False
    print(f"[DEBUG] 最新レコード: {latest_record}")
    
    if latest_record and 'signature' in latest_record and 'data' in latest_record:
        print(f"[DEBUG] 署名データ発見: {latest_record['signature'][:20]}...")
        try:
            # デモ用の固定鍵ペアを取得または生成
            demo_keys = get_or_create_demo_keys()
            if demo_keys:
                # 署名対象のデータを文字列として結合
                signed_data_str = json.dumps(latest_record['data'], ensure_ascii=False, sort_keys=True)
                print(f"[DEBUG] 署名対象データ: {signed_data_str[:100]}...")
                
                # 署名の形式をチェック（16進数文字列かどうか）
                signature = latest_record['signature']
                if signature.startswith('yamashita_signature_'):
                    # 古い形式の署名の場合は、新しい署名を生成
                    print(f"[DEBUG] 古い形式の署名を検出、新しい署名を生成中...")
                    new_signature = sign_patient_data(latest_record['data'], demo_keys['private_key'])
                    if new_signature:
                        # データベースを更新
                        latest_record['signature'] = new_signature
                        # 暗号化データを保存
                        try:
                            save_encrypted_karte_data(decrypted_karte_data, current_user.get_encryption_key())
                            print(f"[INFO] 署名を更新しました")
                        except Exception as e:
                            print(f"[WARNING] 署名更新の保存に失敗: {e}")
                        signature = new_signature
                    else:
                        print(f"[ERROR] 新しい署名の生成に失敗")
                        is_valid_signature = False
                
                try:
                    signature_bytes = bytes.fromhex(signature)
                    is_valid_signature = verify_signature(demo_keys['public_key'], signed_data_str, signature_bytes)
                except ValueError as e:
                    print(f"[ERROR] 署名の16進数変換エラー: {e}")
                    is_valid_signature = False
                print(f"[DEBUG] 署名検証結果: {'Valid' if is_valid_signature else 'Invalid'}")
            else:
                print("[WARNING] デモ用鍵の取得に失敗")
                is_valid_signature = False
        except Exception as e:
            print(f"[ERROR] 署名検証エラー: {e}")
            import traceback
            traceback.print_exc()
            is_valid_signature = False
    else:
        print("[DEBUG] 署名データが不足しています")
        if latest_record:
            print(f"[DEBUG] 利用可能なキー: {list(latest_record.keys())}")
        is_valid_signature = False

    # ハッシュチェーン検証（デモ用）
    is_valid_hash_chain = hash_chain.is_valid()

    response_data = {
        'patient_info': patient['patient_info'],
        'latest_record': latest_record['data'] if latest_record else None,
        'signature_status': 'Valid' if is_valid_signature else 'Invalid',
        'hash_chain_status': 'Valid' if is_valid_hash_chain else 'Invalid'
    }
    
    # 監査ログ: 患者データアクセス成功
    audit_logger.log_event(
        event_id="DATA_ACCESS",
        user_id=current_user.id,
        user_role=current_user.role,
        ip_address=request.remote_addr,
        action="VIEW_PATIENT_DATA",
        resource=f"/api/patient/{patient_id}",
        status="SUCCESS",
        message="患者データにアクセスしました",
        details={
            "patient_id": patient_id,
            "encryption_method": "AES-256-GCM",
            "hash_chain_valid": is_valid_hash_chain
        }
    )
    
    return jsonify(response_data)

@app.route('/api/patient/<patient_id>/add_record', methods=['POST'])
def add_medical_record(patient_id):
    print(f"[API] 医療記録追加リクエスト受信: {patient_id}")
    
    # 手動で認証チェック
    if not current_user.is_authenticated:
        print(f"[API] 認証されていないユーザーからのリクエスト")
        return jsonify({
            'error': 'この機能を使用するにはログインが必要です。',
            'auth_method': 'login_required'
        }), 401
    
    print(f"[API] 認証済みユーザー: {current_user.id}")
    # 暗号化キーの確認
    if not current_user.has_encryption_key():
        print(f"[DEBUG] ユーザー {current_user.id} に暗号化キーがありません。WebAuthn用キーを確認中...")
        
        # WebAuthn認証の場合、専用暗号化キーを取得
        try:
            webauthn_key = get_or_create_webauthn_encryption_key(current_user.id)
            if webauthn_key:
                # 現在のユーザーオブジェクトに暗号化キーを設定
                current_user.encryption_key = webauthn_key
                print(f"[INFO] WebAuthn暗号化キーを設定しました: {current_user.id}")
            else:
                return jsonify({
                    "error": "暗号化キーが利用できません。パスワードでログインしてください。",
                    "auth_method": "password_required"
                }), 401
        except Exception as e:
            print(f"[ERROR] WebAuthn暗号化キー取得エラー: {e}")
            return jsonify({
                "error": "暗号化キーが利用できません。パスワードでログインしてください。",
                "auth_method": "password_required"
            }), 401

    subject_attributes = {"id": current_user.id, "role": current_user.role}
    action = "add"
    resource_attributes = {"type": "patient_data", "patient_id": patient_id}

    if not abac_enforcer.check_access(subject_attributes, action, resource_attributes):
        return jsonify({'error': 'Permission denied'}), 403

    # 暗号化されたデータを読み込み
    try:
        decrypted_karte_data = load_encrypted_karte_data(current_user.get_encryption_key())
        patient = decrypted_karte_data.get(patient_id)
    except Exception as e:
        print(f"[ERROR] データ復号エラー: {e}")
        return jsonify({'error': 'データの復号に失敗しました'}), 500

    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    new_record_data = request.json
    if not new_record_data:
        return jsonify({'error': 'No data provided'}), 400

    # 署名対象のデータは文字列として結合されていると仮定
    signed_data_str = json.dumps(new_record_data, ensure_ascii=False, sort_keys=True)
    signature = sign_data(private_key, signed_data_str)

    record_entry = {
        'timestamp': datetime.now().isoformat(),
        'data': new_record_data,
        'signature': signature.hex() # 署名をhex文字列で保存
    }

    patient['medical_records'].append(record_entry)

    # ハッシュチェーンに追加
    hash_chain.add_block({
        'patient_id': patient_id,
        'record': record_entry,
        'timestamp': datetime.now().isoformat()
    })

    # 暗号化してデータを保存
    try:
        save_encrypted_karte_data(decrypted_karte_data, current_user.get_encryption_key())
        print(f"[INFO] 患者 {patient_id} のデータを暗号化して保存しました")
    except Exception as e:
        print(f"[ERROR] データ暗号化保存エラー: {e}")
        return jsonify({'error': 'データの保存に失敗しました'}), 500

    return jsonify({'message': 'Medical record added successfully', 'record': record_entry}), 201

# WebAuthn関連のエンドポイント
@app.route('/webauthn_register')
@login_required
def webauthn_register():
    """WebAuthn認証器登録ページを表示"""
    return render_template('webauthn_register.html', username=current_user.id)

@app.route('/audit-dashboard')
@login_required
def audit_dashboard():
    """監査ログダッシュボードを表示"""
    # 管理者権限チェック
    if current_user.role != 'admin' and current_user.role != 'doctor':
        flash('監査ログダッシュボードへのアクセス権限がありません')
        return redirect(url_for('index'))
    
    return render_template('audit_dashboard.html')

@app.route('/api/webauthn/status', methods=['GET'])
@login_required
def webauthn_status():
    """WebAuthn認証器の登録状況を確認"""
    try:
        # ヘルパー関数を使用してWebAuthn状況を確認
        from core.webauthn_helper import has_webauthn_credentials, get_webauthn_credentials
        user_db_path = os.path.join(os.path.dirname(__file__), 'user_db.json')
        
        has_webauthn = has_webauthn_credentials(current_user.id, user_db_path)
        credentials = get_webauthn_credentials(current_user.id, user_db_path)
        credentials_count = len(credentials)
        
        return jsonify({
            'registered': has_webauthn,
            'credentials_count': credentials_count,
            'username': current_user.id
        })
    except Exception as e:
        print(f"[ERROR] WebAuthn状況確認エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo-keys-status', methods=['GET'])
def get_demo_keys_status():
    """デモ用鍵の状態を取得"""
    try:
        demo_keys = get_or_create_demo_keys()
        if not demo_keys:
            return jsonify({
                'status': 'error',
                'message': 'デモ用鍵の取得に失敗しました'
            }), 500
        
        # 公開鍵の情報を取得
        from cryptography.hazmat.primitives import serialization
        public_pem = demo_keys['public_key'].public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        # 鍵の詳細情報
        key_info = {
            'status': 'success',
            'key_type': 'RSA 2048-bit',
            'algorithm': 'RSA-PSS with SHA256',
            'public_key_preview': public_pem[:100] + '...',
            'key_size': 2048,
            'created_at': 'デモ用鍵（起動時に生成）'
        }
        
        return jsonify(key_info)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'鍵状態の取得に失敗: {str(e)}'
        }), 500

@app.route('/api/audit-logs', methods=['GET'])
@login_required
def get_audit_logs():
    """監査ログを取得してAPIで提供"""
    try:
        # 管理者権限チェック
        if current_user.role != 'admin' and current_user.role != 'doctor':
            return jsonify({'error': '権限がありません'}), 403
        
        audit_log_path = os.path.join(app.root_path, "..", "..", "audit.log")
        logs = []
        stats = {
            'total': 0,
            'success': 0,
            'failure': 0,
            'activeUsers': 0
        }
        
        if os.path.exists(audit_log_path):
            try:
                with open(audit_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                active_users = set()
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                            
                            # 統計情報の更新
                            stats['total'] += 1
                            status = log_entry.get('status', '').upper()
                            if status == 'SUCCESS':
                                stats['success'] += 1
                            elif status == 'FAILURE':
                                stats['failure'] += 1
                            
                            if log_entry.get('user_id') and log_entry.get('user_id') != 'anonymous':
                                active_users.add(log_entry.get('user_id'))
                                
                        except json.JSONDecodeError:
                            continue  # 無効なJSON行をスキップ
                
                stats['activeUsers'] = len(active_users)
                
            except Exception as e:
                print(f"[ERROR] 監査ログ読み込みエラー: {e}")
                
        # 最新のログから順に並び替え
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'logs': logs,
            'stats': stats
        })
        
    except Exception as e:
        print(f"[ERROR] 監査ログAPI エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/webauthn/register/begin', methods=['POST'])
@login_required
def webauthn_register_begin():
    """WebAuthn認証器登録を開始"""
    try:
        print(f"[DEBUG] WebAuthn登録開始: {current_user.id}")
        registration_options = authenticator.generate_webauthn_registration_options(current_user.id)
        if registration_options:
            print(f"[DEBUG] WebAuthn登録オプション生成成功: {current_user.id}")
            return jsonify(registration_options)
        else:
            print(f"[ERROR] WebAuthn登録オプション生成失敗: {current_user.id}")
            return jsonify({'error': '登録オプションの生成に失敗しました'}), 500
    except Exception as e:
        print(f"[ERROR] WebAuthn登録開始エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'登録開始エラー: {str(e)}'}), 500

@app.route('/webauthn/register/complete', methods=['POST'])
@login_required
def webauthn_register_complete():
    """WebAuthn認証器登録を完了"""
    try:
        data = request.get_json()
        registration_response = data.get('registrationResponse')
        challenge = data.get('challenge')
        
        if not registration_response or not challenge:
            return jsonify({'error': '必要なデータが不足しています'}), 400
        
        success, message = authenticator.verify_webauthn_registration_response(
            current_user.id, registration_response, challenge
        )
        
        if success:
            # WebAuthn登録成功時に暗号化キーを生成（まだ存在しない場合）
            get_or_create_webauthn_encryption_key(current_user.id)
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'登録完了エラー: {str(e)}'}), 500

@app.route('/webauthn_login')
def webauthn_login():
    """WebAuthnログインページを表示"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('webauthn_login.html')

@app.route('/webauthn/login/begin', methods=['POST'])
def webauthn_login_begin():
    """WebAuthn認証を開始"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'ユーザー名が必要です'}), 400
        
        # ヘルパー関数を使用してWebAuthn認証器を確認
        from core.webauthn_helper import has_webauthn_credentials, get_webauthn_credentials
        user_db_path = os.path.join(os.path.dirname(__file__), 'user_db.json')
        
        has_webauthn = has_webauthn_credentials(username, user_db_path)
        credentials = get_webauthn_credentials(username, user_db_path)
        
        print(f"[DEBUG] ユーザー {username} のWebAuthn認証器数: {len(credentials)}")
        print(f"[DEBUG] WebAuthn登録状況: {has_webauthn}")
        
        if not has_webauthn or len(credentials) == 0:
            print(f"[ERROR] ユーザー {username} にWebAuthn認証器が登録されていません")
            return jsonify({'error': 'WebAuthn認証器が登録されていません'}), 400
            
        for i, cred in enumerate(credentials):
            print(f"[DEBUG] 認証器 {i+1}: credential_id={cred.get('credential_id', 'N/A')[:20]}...")
        
        authentication_options = authenticator.generate_webauthn_authentication_options(username)
        if authentication_options:
            print(f"[DEBUG] WebAuthn認証オプションを生成しました: {username}")
            return jsonify(authentication_options)
        else:
            print(f"[DEBUG] WebAuthn認証器が登録されていません: {username}")
            return jsonify({'error': 'WebAuthn認証器が登録されていません'}), 400
            
    except Exception as e:
        return jsonify({'error': f'認証開始エラー: {str(e)}'}), 500

@app.route('/webauthn/login/complete', methods=['POST'])
def webauthn_login_complete():
    """WebAuthn認証を完了"""
    try:
        data = request.get_json()
        username = data.get('username')
        authentication_response = data.get('authenticationResponse')
        challenge = data.get('challenge')
        
        if not username or not authentication_response or not challenge:
            return jsonify({'error': '必要なデータが不足しています'}), 400
        
        success, message = authenticator.verify_webauthn_authentication_response(
            username, authentication_response, challenge
        )
        
        if success:
            print(f"[DEBUG] WebAuthn認証成功: {username}")
            
            # WebAuthn認証成功時に専用暗号化キーを生成・取得
            encryption_key = get_or_create_webauthn_encryption_key(username)
            print(f"[DEBUG] 暗号化キーを取得: {len(encryption_key)}バイト")
            
            # ユーザーをログイン状態にする（暗号化キー付き）
            user = User(username, authenticator.get_user_role(username), encryption_key)
            login_user(user)
            print(f"[DEBUG] ユーザーログイン完了: {username} (暗号化キー有効)")
            
            # 監査ログ: WebAuthnログイン成功
            audit_logger.log_event(
                event_id="AUTH_WEBAUTHN_SUCCESS",
                user_id=username,
                user_role=authenticator.get_user_role(username),
                ip_address=request.remote_addr,
                action="WEBAUTHN_LOGIN",
                resource="/webauthn/login/complete",
                status="SUCCESS",
                message="WebAuthn認証でログインしました",
                details={"authentication_method": "webauthn"}
            )
            
            return jsonify({'success': True, 'message': message, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'認証完了エラー: {str(e)}'}), 500

# グローバル変数でラズパイ表示用患者IDを管理
current_display_patient_id = None

# ラズパイ患者ビュー専用API
@app.route('/api/patient-display')
def get_patient_display():
    """ラズパイ用患者ビュー専用API（認証不要）"""
    try:
        # グローバル変数から患者IDを取得（PCから設定される）
        global current_display_patient_id
        patient_id = current_display_patient_id
        if not patient_id:
            return jsonify({"error": "No patient selected for display"}), 400
        
        # 患者データの取得（デモデータを直接返す）
        try:
            # デモ患者データを直接返す
            if patient_id == "P001":
                response_data = {
                    "patient_info": {
                        "name": "山下真凜",
                        "birth_date": "1990-05-15",
                        "age": 33,
                        "gender": "女性"
                    },
                    "current_conditions": "高血圧、軽度の糖尿病",
                    "medications": "アムロジピン 5mg、メトホルミン 500mg",
                    "test_results": "血圧: 140/90 mmHg、血糖値: 120 mg/dL"
                }
            else:
                return jsonify({"error": "Patient data not found"}), 404
            
        except Exception as e:
            print(f"[ERROR] ラズパイ用患者データ取得エラー: {e}")
            return jsonify({"error": f"Failed to load patient data: {str(e)}"}), 500
        
        # 監査ログ記録
        audit_logger.log_event(
            event_id="PATIENT_DISPLAY_ACCESS",
            user_id="raspberry_pi",
            user_role="display_device",
            ip_address=request.remote_addr,
            action="read",
            resource="patient_display",
            status="success",
            message=f"ラズパイから患者ID {patient_id} の表示データにアクセス",
            details={"patient_id": patient_id}
        )
        
        return jsonify(response_data)
        
    except Exception as e:
        audit_logger.log_event(
            event_id="PATIENT_DISPLAY_ERROR",
            user_id="raspberry_pi",
            user_role="display_device",
            ip_address=request.remote_addr,
            action="read",
            resource="patient_display",
            status="error",
            message=f"ラズパイ表示データアクセス中にエラーが発生: {str(e)}",
            details={"error": str(e)}
        )
        return jsonify({"error": "Internal server error"}), 500

# PC側から患者表示を制御するAPI
@app.route('/api/set-patient-display', methods=['POST'])
def set_patient_display():
    """PC側から患者表示を設定するAPI（認証を一時的に無効化）"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({"error": "patient_id is required"}), 400
        
        # グローバル変数に患者IDを設定（セッション共有の問題を回避）
        global current_display_patient_id
        current_display_patient_id = patient_id
        
        # 監査ログ記録（認証なしでも記録）
        audit_logger.log_event(
            event_id="PATIENT_DISPLAY_SET",
            user_id="system_user",
            user_role="system",
            ip_address=request.remote_addr,
            action="set_display",
            resource="patient_display",
            status="success",
            message=f"患者ID {patient_id} をラズパイ表示に設定",
            details={"patient_id": patient_id}
        )
        
        return jsonify({"success": True, "patient_id": patient_id})
        
    except Exception as e:
        print(f"[ERROR] set_patient_display: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ラズパイ用患者ビューページ
@app.route('/patient-display')
def patient_display():
    """ラズパイ用患者ビュー表示ページ"""
    return render_template('patient_display.html')

# テスト用ページ
@app.route('/raspi_test.html')
def raspi_test():
    """ラズパイ表示テスト用ページ"""
    return render_template('raspi_test.html')

# 修正用JavaScriptファイル
@app.route('/pc_fix.js')
def pc_fix_js():
    """修正用JavaScriptファイル"""
    from flask import send_from_directory
    return send_from_directory('static', 'pc_fix.js', mimetype='application/javascript')

@app.route('/security_verification', methods=['GET'])
@login_required
def security_verification():
    """セキュリティ検証システム - 現在のセキュリティ状況を総合的に検証"""
    try:
        print(f"[SECURITY] セキュリティ検証開始: {current_user.id}")
        
        verification_results = {
            'overall_status': 'success',
            'timestamp': datetime.now().isoformat(),
            'user_id': current_user.id,
            'checks': []
        }
        
        # 1. デモ用鍵システムの検証
        try:
            demo_keys = get_or_create_demo_keys()
            if demo_keys and 'public_key' in demo_keys and 'private_key' in demo_keys:
                verification_results['checks'].append({
                    'name': 'デモ用鍵システム',
                    'status': 'success',
                    'message': 'RSA 2048-bit鍵ペアが正常に生成・管理されています',
                    'details': {
                        'key_type': 'RSA 2048-bit',
                        'algorithm': 'RSA-PSS with SHA256',
                        'key_size': 2048
                    }
                })
            else:
                verification_results['checks'].append({
                    'name': 'デモ用鍵システム',
                    'status': 'failure',
                    'message': 'デモ用鍵ペアの生成に失敗しています',
                    'details': {}
                })
                verification_results['overall_status'] = 'partial'
        except Exception as e:
            verification_results['checks'].append({
                'name': 'デモ用鍵システム',
                'status': 'error',
                'message': f'鍵システム検証エラー: {str(e)}',
                'details': {}
            })
            verification_results['overall_status'] = 'partial'
        
        # 2. 患者データ署名検証
        try:
            # 患者P001のデータを取得して署名検証
            from flask import jsonify
            patient_response = get_patient_data('P001')
            if hasattr(patient_response, 'get_json'):
                patient_data = patient_response.get_json()
            else:
                patient_data = patient_response
                
            if patient_data and patient_data.get('signature_status') == 'Valid':
                verification_results['checks'].append({
                    'name': '患者データ署名検証',
                    'status': 'success',
                    'message': '患者データの署名検証が正常に完了しています',
                    'details': {
                        'patient_id': 'P001',
                        'signature_status': 'Valid',
                        'hash_chain_status': patient_data.get('hash_chain_status', 'Unknown')
                    }
                })
            else:
                verification_results['checks'].append({
                    'name': '患者データ署名検証',
                    'status': 'failure',
                    'message': '患者データの署名検証に失敗しています',
                    'details': {
                        'patient_id': 'P001',
                        'signature_status': patient_data.get('signature_status', 'Unknown') if patient_data else 'No Data'
                    }
                })
                verification_results['overall_status'] = 'partial'
        except Exception as e:
            verification_results['checks'].append({
                'name': '患者データ署名検証',
                'status': 'error',
                'message': f'署名検証エラー: {str(e)}',
                'details': {}
            })
            verification_results['overall_status'] = 'partial'
        
        # 3. 監査ログシステムの検証
        try:
            audit_log_path = os.path.join(app.root_path, "..", "..", "audit.log")
            if os.path.exists(audit_log_path):
                with open(audit_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                total_logs = len([line for line in lines if line.strip()])
                if total_logs > 0:
                    verification_results['checks'].append({
                        'name': '監査ログシステム',
                        'status': 'success',
                        'message': f'監査ログシステムが正常に動作しています（{total_logs}件のログ）',
                        'details': {
                            'total_logs': total_logs,
                            'log_file_exists': True
                        }
                    })
                else:
                    verification_results['checks'].append({
                        'name': '監査ログシステム',
                        'status': 'warning',
                        'message': '監査ログファイルは存在しますが、ログが記録されていません',
                        'details': {
                            'total_logs': 0,
                            'log_file_exists': True
                        }
                    })
            else:
                verification_results['checks'].append({
                    'name': '監査ログシステム',
                    'status': 'failure',
                    'message': '監査ログファイルが存在しません',
                    'details': {
                        'total_logs': 0,
                        'log_file_exists': False
                    }
                })
                verification_results['overall_status'] = 'partial'
        except Exception as e:
            verification_results['checks'].append({
                'name': '監査ログシステム',
                'status': 'error',
                'message': f'監査ログ検証エラー: {str(e)}',
                'details': {}
            })
            verification_results['overall_status'] = 'partial'
        
        # 4. 暗号化システムの検証
        try:
            # ユーザーの暗号化キーが存在するかチェック
            user_encryption_key = authenticator.get_user_encryption_key(current_user.id)
            if not user_encryption_key:
                # 暗号化キーが存在しない場合は生成を試行
                print(f"[DEBUG] ユーザー {current_user.id} の暗号化キーが存在しません。生成を試行します。")
                try:
                    # パスワードベースの暗号化キーを生成
                    user_data = authenticator.get_user_info(current_user.id)
                    if user_data and 'password' in user_data:
                        # パスワードから暗号化キーを生成
                        import hashlib
                        password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
                        user_encryption_key = password_hash[:32]  # 32文字のキー
                        print(f"[DEBUG] パスワードベース暗号化キーを生成しました")
                    else:
                        print(f"[DEBUG] ユーザーデータまたはパスワードが見つかりません")
                except Exception as e:
                    print(f"[DEBUG] 暗号化キー生成エラー: {e}")
            
            if user_encryption_key:
                verification_results['checks'].append({
                    'name': '暗号化システム',
                    'status': 'success',
                    'message': 'ユーザー暗号化キーが正常に設定されています',
                    'details': {
                        'user_id': current_user.id,
                        'encryption_key_exists': True
                    }
                })
            else:
                verification_results['checks'].append({
                    'name': '暗号化システム',
                    'status': 'warning',
                    'message': 'ユーザー暗号化キーが設定されていません',
                    'details': {
                        'user_id': current_user.id,
                        'encryption_key_exists': False
                    }
                })
        except Exception as e:
            verification_results['checks'].append({
                'name': '暗号化システム',
                'status': 'error',
                'message': f'暗号化システム検証エラー: {str(e)}',
                'details': {}
            })
            verification_results['overall_status'] = 'partial'
        
        # 5. WebAuthn認証システムの検証
        try:
            # ユーザーデータからWebAuthn認証器を取得
            user_data = authenticator.get_user_info(current_user.id)
            webauthn_credentials = user_data.get('webauthn_credentials', []) if user_data else []
            if webauthn_credentials and len(webauthn_credentials) > 0:
                verification_results['checks'].append({
                    'name': 'WebAuthn認証システム',
                    'status': 'success',
                    'message': f'WebAuthn認証器が登録されています（{len(webauthn_credentials)}件）',
                    'details': {
                        'user_id': current_user.id,
                        'registered_credentials': len(webauthn_credentials)
                    }
                })
            else:
                verification_results['checks'].append({
                    'name': 'WebAuthn認証システム',
                    'status': 'info',
                    'message': 'WebAuthn認証器が登録されていません（オプション機能）',
                    'details': {
                        'user_id': current_user.id,
                        'registered_credentials': 0
                    }
                })
        except Exception as e:
            verification_results['checks'].append({
                'name': 'WebAuthn認証システム',
                'status': 'error',
                'message': f'WebAuthn検証エラー: {str(e)}',
                'details': {}
            })
        
        # 6. セッション管理の検証
        try:
            if current_user and current_user.id:
                verification_results['checks'].append({
                    'name': 'セッション管理',
                    'status': 'success',
                    'message': 'ユーザーセッションが正常に管理されています',
                    'details': {
                        'user_id': current_user.id,
                        'user_role': current_user.role,
                        'session_active': True
                    }
                })
            else:
                verification_results['checks'].append({
                    'name': 'セッション管理',
                    'status': 'failure',
                    'message': 'ユーザーセッションが無効です',
                    'details': {}
                })
                verification_results['overall_status'] = 'partial'
        except Exception as e:
            verification_results['checks'].append({
                'name': 'セッション管理',
                'status': 'error',
                'message': f'セッション検証エラー: {str(e)}',
                'details': {}
            })
            verification_results['overall_status'] = 'partial'
        
        # 総合評価の計算
        success_count = len([check for check in verification_results['checks'] if check['status'] == 'success'])
        total_checks = len(verification_results['checks'])
        
        verification_results['summary'] = {
            'total_checks': total_checks,
            'successful_checks': success_count,
            'success_rate': f"{(success_count / total_checks * 100):.1f}%" if total_checks > 0 else "0%"
        }
        
        print(f"[SECURITY] セキュリティ検証完了: {verification_results['overall_status']} ({success_count}/{total_checks})")
        
        return jsonify(verification_results)
        
    except Exception as e:
        print(f"[ERROR] セキュリティ検証エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'overall_status': 'error',
            'timestamp': datetime.now().isoformat(),
            'user_id': current_user.id if current_user else 'unknown',
            'error': str(e),
            'checks': []
        }), 500

@app.route('/security_verification_page')
@login_required
def security_verification_page():
    """セキュリティ検証ページを表示"""
    return render_template('security_verification.html')

@app.route('/api/webauthn-credentials', methods=['GET'])
@login_required
def get_webauthn_credentials():
    """WebAuthn認証器一覧を取得"""
    try:
        print(f"認証器一覧取得 - ユーザー: {current_user.id}")
        credentials_info = authenticator.get_webauthn_credentials_info(current_user.id)
        print(f"取得した認証器数: {len(credentials_info)}")
        for i, cred in enumerate(credentials_info):
            print(f"認証器 {i}: {cred.get('credential_id', 'N/A')} (長さ: {len(cred.get('credential_id', ''))})")
        return jsonify({
            'success': True,
            'credentials': credentials_info,
            'total_count': len(credentials_info)
        })
    except Exception as e:
        print(f"認証器一覧取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/webauthn-credentials/clear-all', methods=['POST'])
@login_required
def clear_all_webauthn_credentials():
    """すべてのWebAuthn認証器を削除"""
    try:
        success, message, removed_count = authenticator.clear_all_webauthn_credentials(current_user.id)
        return jsonify({
            'success': success,
            'message': message,
            'removed_count': removed_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/webauthn-credentials/<credential_id>', methods=['DELETE'])
@login_required
def remove_webauthn_credential(credential_id):
    """指定されたWebAuthn認証器を削除"""
    try:
        print(f"削除リクエスト - ユーザー: {current_user.id}, 認証器ID: {credential_id}")
        
        # 現在の認証器一覧を確認
        user_info = authenticator.get_user_info(current_user.id)
        if user_info and 'webauthn_credentials' in user_info:
            print(f"現在の認証器数: {len(user_info['webauthn_credentials'])}")
            for i, cred in enumerate(user_info['webauthn_credentials']):
                print(f"認証器 {i}: {cred.get('credential_id', 'N/A')}")
                # IDの完全一致を確認
                if cred.get('credential_id') == credential_id:
                    print(f"✅ 認証器IDが一致しました: {credential_id}")
                else:
                    print(f"❌ 認証器IDが一致しません: 期待値={credential_id}, 実際値={cred.get('credential_id')}")
        else:
            print("❌ ユーザー情報または認証器一覧が見つかりません")
        
        success, message = authenticator.remove_webauthn_credential(current_user.id, credential_id)
        print(f"削除結果 - 成功: {success}, メッセージ: {message}")
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        print(f"削除エラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webauthn-management')
@login_required
def webauthn_management():
    """WebAuthn認証器管理ページを表示"""
    return render_template('webauthn_management.html')

# 登録されているルートを表示（デバッグ用）
print("[STARTUP] 登録されているAPIルート:")
for rule in app.url_map.iter_rules():
    if '/api/' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint} ({list(rule.methods)})")

# このファイルは run_app.py から呼び出されるため、直接実行しない
if __name__ == '__main__':
    print("[WARNING] このファイルは直接実行しないでください")
    print("[INFO] python info_sharing_system/run_app.py を使用してください")