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

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24) # セッション管理のための秘密鍵

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# current_userをテンプレートで利用可能にする
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# UserAuthenticatorの初期化
authenticator = UserAuthenticator(os.path.join(app.root_path, "user_db.json"))

# ABACPolicyEnforcerの初期化
abac_enforcer = ABACPolicyEnforcer(os.path.join(app.root_path, "..", "..", "abac_policy.json")) # パスを調整

# Flask-LoginのためのUserクラス
class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

    def get_id(self):
        return str(self.id)

    def get_role(self):
        return self.role

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

karte_data = load_karte_data()

# デモ用ユーザーの初期化
def initialize_demo_users():
    """デモ用ユーザーを初期化"""
    demo_users = [
        ("doctor1", "secure_pass_doc", "doctor", True),
        ("nurse1", "secure_pass_nurse", "nurse", False),
        ("patient1", "secure_pass_pat", "patient", False),
        ("admin1", "secure_pass_admin", "admin", False)
    ]
    
    for username, password, role, enable_mfa in demo_users:
        # 既に存在しない場合のみ作成
        if username not in authenticator.users:
            success, message, mfa_secret = authenticator.register_user(
                username, password, role, enable_mfa
            )
            if success:
                print(f"[DEMO] ユーザー作成: {username} ({role}) - MFA: {enable_mfa}")
                if mfa_secret:
                    print(f"[DEMO] {username} のMFAシークレット: {mfa_secret}")

# アプリケーション起動時にデモユーザーを初期化
initialize_demo_users()

@app.route('/')
def index():
    # 認証済みの場合はユーザー情報を渡し、未認証の場合はログインリンクを表示
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.id, role=current_user.role)
    else:
        return render_template('index.html')

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
                return redirect(url_for('mfa_verify'))
            else:
                user = User(username, authenticator.get_user_role(username))
                login_user(user)
                return redirect(url_for('index'))
        else:
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
            user = User(username, authenticator.get_user_role(username))
            login_user(user)
            session.pop('mfa_username', None)
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
@login_required
def get_patient_data(patient_id):
    subject_attributes = {"id": current_user.id, "role": current_user.role}
    action = "view"
    resource_attributes = {"type": "patient_data", "patient_id": patient_id}

    if not abac_enforcer.check_access(subject_attributes, action, resource_attributes):
        return jsonify({'error': 'Permission denied'}), 403

    patient = karte_data.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # 最新のカルテ情報を取得
    latest_record = patient['medical_records'][-1] if patient['medical_records'] else None

    # 署名検証（デモ用）
    is_valid_signature = False
    if latest_record and 'signature' in latest_record and 'data' in latest_record:
        try:
            # 署名対象のデータは文字列として結合されていると仮定
            signed_data_str = json.dumps(latest_record['data'], ensure_ascii=False, sort_keys=True)
            signature_bytes = bytes.fromhex(latest_record['signature'])
            is_valid_signature = verify_signature(public_key, signed_data_str, signature_bytes)
        except Exception as e:
            print(f"Signature verification failed: {e}")
            is_valid_signature = False

    # ハッシュチェーン検証（デモ用）
    is_valid_hash_chain = hash_chain.is_valid()

    response_data = {
        'patient_info': patient['patient_info'],
        'latest_record': latest_record['data'] if latest_record else None,
        'signature_status': 'Valid' if is_valid_signature else 'Invalid',
        'hash_chain_status': 'Valid' if is_valid_hash_chain else 'Invalid'
    }
    return jsonify(response_data)

@app.route('/api/patient/<patient_id>/add_record', methods=['POST'])
@login_required
def add_medical_record(patient_id):
    subject_attributes = {"id": current_user.id, "role": current_user.role}
    action = "add"
    resource_attributes = {"type": "patient_data", "patient_id": patient_id}

    if not abac_enforcer.check_access(subject_attributes, action, resource_attributes):
        return jsonify({'error': 'Permission denied'}), 403

    patient = karte_data.get(patient_id)
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

    save_karte_data(karte_data)
    return jsonify({'message': 'Medical record added successfully', 'record': record_entry}), 201

# WebAuthn関連のエンドポイント
@app.route('/webauthn_register')
@login_required
def webauthn_register():
    """WebAuthn認証器登録ページを表示"""
    return render_template('webauthn_register.html', username=current_user.id)

@app.route('/webauthn/register/begin', methods=['POST'])
@login_required
def webauthn_register_begin():
    """WebAuthn認証器登録を開始"""
    try:
        registration_options = authenticator.generate_webauthn_registration_options(current_user.id)
        if registration_options:
            return jsonify(registration_options)
        else:
            return jsonify({'error': '登録オプションの生成に失敗しました'}), 500
    except Exception as e:
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
        
        authentication_options = authenticator.generate_webauthn_authentication_options(username)
        if authentication_options:
            return jsonify(authentication_options)
        else:
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
            # ユーザーをログイン状態にする
            user = User(username, authenticator.get_user_role(username))
            login_user(user)
            return jsonify({'success': True, 'message': message, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'認証完了エラー: {str(e)}'}), 500

if __name__ == '__main__':
    # certsディレクトリが存在しない場合は作成
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
    app.run(debug=True, ssl_context=(os.path.join(CERT_DIR, 'cert.pem'), os.path.join(CERT_DIR, 'key.pem')))