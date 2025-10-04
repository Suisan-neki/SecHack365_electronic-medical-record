"""
模擬電子カルテシステム (Dummy EHR System)

既存の電子カルテシステムを模擬し、
メインシステムとのデータ連携をデモするためのシステム
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import sys
import base64
import secrets
try:
    from webauthn import generate_registration_options, verify_registration_response
    from webauthn import generate_authentication_options, verify_authentication_response
    from webauthn.helpers.structs import AttestationConveyancePreference, AuthenticatorSelectionCriteria, UserVerificationRequirement
    WEBAUTHN_AVAILABLE = True
    print("[INFO] WebAuthnライブラリのインポートに成功しました")
except ImportError as e:
    print(f"[ERROR] WebAuthnライブラリのインポートに失敗しました: {e}")
    WEBAUTHN_AVAILABLE = False

# パスを追加（core モジュールを使うため）
sys.path.append(os.path.join(os.path.dirname(__file__), '../../SecHack365_project'))

app = Flask(__name__)

# CORS設定
CORS(app, 
     origins=['http://localhost:5001'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# データディレクトリ
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
os.makedirs(DATA_DIR, exist_ok=True)

PATIENTS_FILE = os.path.join(DATA_DIR, 'patients.json')
RECORDS_FILE = os.path.join(DATA_DIR, 'medical_records.json')
WEBAUTHN_CREDENTIALS_FILE = os.path.join(DATA_DIR, 'webauthn_credentials.json')

# WebAuthn設定
RP_ID = "localhost"
RP_NAME = "患者情報共有システム"
ORIGIN = "http://localhost:5001"
RP_ICON = "https://localhost:5001/favicon.ico"


# ==================== データ管理 ====================

def load_patients():
    """患者データを読み込み"""
    if os.path.exists(PATIENTS_FILE):
        with open(PATIENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_patients(patients):
    """患者データを保存"""
    with open(PATIENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(patients, f, ensure_ascii=False, indent=2)

def load_records():
    """診療記録を読み込み"""
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_records(records):
    """診療記録を保存"""
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_webauthn_credentials():
    """WebAuthn認証情報を読み込み"""
    if os.path.exists(WEBAUTHN_CREDENTIALS_FILE):
        with open(WEBAUTHN_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_webauthn_credentials(credentials):
    """WebAuthn認証情報を保存"""
    with open(WEBAUTHN_CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(credentials, f, ensure_ascii=False, indent=2)

def migrate_webauthn_credentials():
    """元のシステムからWebAuthn認証情報を移行"""
    try:
        # 元のシステムのWebAuthn認証情報ファイル
        old_user_db_path = os.path.join(os.path.dirname(__file__), '../../../SecHack365_project/info_sharing_system/app/user_db.json')
        
        if os.path.exists(old_user_db_path):
            with open(old_user_db_path, 'r', encoding='utf-8') as f:
                old_user_db = json.load(f)
            
            # 新しいシステムのWebAuthn認証情報
            credentials = load_webauthn_credentials()
            
            # doctor1のWebAuthn認証情報を移行
            if 'doctor1' in old_user_db and 'webauthn_credentials' in old_user_db['doctor1']:
                old_creds = old_user_db['doctor1']['webauthn_credentials']
                if old_creds:
                    old_cred = old_creds[0]  # 最初の認証情報を使用
                    credentials['doctor1'] = {
                        'id': old_cred['credential_id'],
                        'public_key': old_cred['public_key'],
                        'counter': old_cred['sign_count'],
                        'device_type': 'platform',
                        'backed_up': False,
                        'transports': ['internal']
                    }
                    
                    save_webauthn_credentials(credentials)
                    print(f"[INFO] WebAuthn認証情報を移行しました: doctor1")
            
    except Exception as e:
        print(f"[WARNING] WebAuthn認証情報の移行に失敗しました: {e}")

def initialize_sample_data():
    """サンプルデータを初期化"""
    
    # WebAuthn認証情報を移行
    migrate_webauthn_credentials()
    
    if not os.path.exists(PATIENTS_FILE):
        sample_patients = [
            {
                "patient_id": "P001",
                "name": "山下真凜",
                "name_kana": "ヤマシタマリン",
                "birth_date": "2002-03-15",
                "gender": "女性",
                "phone": "090-1234-5678",
                "address": "東京都渋谷区恵比寿1-2-3",
                "allergies": "なし",
                "blood_type": "A型",
                "created_at": "2020-01-01T00:00:00"
            },
            {
                "patient_id": "P002",
                "name": "佐藤花子",
                "name_kana": "サトウハナコ",
                "birth_date": "1992-08-20",
                "gender": "女性",
                "phone": "090-9876-5432",
                "address": "東京都新宿区...",
                "allergies": "なし",
                "blood_type": "O型",
                "created_at": "2020-02-01T00:00:00"
            },
            {
                "patient_id": "P003",
                "name": "鈴木一郎",
                "name_kana": "スズキイチロウ",
                "birth_date": "1975-12-03",
                "gender": "男性",
                "phone": "090-5555-6666",
                "address": "神奈川県横浜市...",
                "allergies": "卵",
                "blood_type": "B型",
                "created_at": "2020-03-01T00:00:00"
            }
        ]
        save_patients(sample_patients)
    
    if not os.path.exists(RECORDS_FILE):
        sample_records = [
            {
                "record_id": "REC001",
                "patient_id": "P001",
                "date": "2025-09-15T10:30:00",
                "doctor": "田中医師",
                "department": "内科",
                "chief_complaint": "発熱、咳、鼻水",
                "diagnosis": "急性上気道炎",
                "treatment": "カロナール 500mg 1日3回 3日分 食後、ムコダイン 500mg 1日3回 5日分 食後",
                "notes": "3日前から38.5度の発熱が続いている。解熱剤で一時的に下がるが再び上昇。安静と水分補給を指示。",
                "status": "完了"
            },
            {
                "record_id": "REC002",
                "patient_id": "P002",
                "date": "2025-09-20T14:00:00",
                "doctor": "田中医師",
                "department": "内科",
                "chief_complaint": "腹痛、下痢",
                "diagnosis": "急性胃腸炎",
                "treatment": "ナウゼリン 10mg 1日3回 3日分 食前",
                "notes": "脱水に注意",
                "status": "完了"
            },
            {
                "record_id": "REC003",
                "patient_id": "P001",
                "date": "2025-10-01T09:00:00",
                "doctor": "田中医師",
                "department": "内科",
                "chief_complaint": "頭痛、倦怠感",
                "diagnosis": "片頭痛",
                "treatment": "ロキソニン 60mg 1日3回 3日分 食後",
                "notes": "月経周期と関連する可能性。ストレス要因の確認。",
                "status": "完了"
            }
        ]
        save_records(sample_records)


# ==================== ルート ====================

@app.route('/')
def index():
    """ダッシュボード"""
    patients = load_patients()
    records = load_records()
    
    stats = {
        "total_patients": len(patients),
        "total_records": len(records),
        "today_records": len([r for r in records if r['date'].startswith(datetime.now().strftime('%Y-%m-%d'))])
    }
    
    return render_template('index.html', stats=stats)

@app.route('/patients')
def patient_list():
    """患者一覧"""
    patients = load_patients()
    return render_template('patient_list.html', patients=patients)

@app.route('/patient/<patient_id>')
def patient_detail(patient_id):
    """患者詳細"""
    patients = load_patients()
    records = load_records()
    
    patient = next((p for p in patients if p['patient_id'] == patient_id), None)
    if not patient:
        return "Patient not found", 404
    
    patient_records = [r for r in records if r['patient_id'] == patient_id]
    patient_records.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('patient_detail.html', patient=patient, records=patient_records)

@app.route('/records')
def records_list():
    """診療記録一覧"""
    records = load_records()
    patients = load_patients()
    
    # 患者情報を診療記録に追加
    for record in records:
        patient = next((p for p in patients if p['patient_id'] == record['patient_id']), None)
        if patient:
            record['patient_name'] = patient['name']
            record['patient_name_kana'] = patient['name_kana']
        else:
            record['patient_name'] = '不明'
            record['patient_name_kana'] = 'フメイ'
    
    records.sort(key=lambda x: x['date'], reverse=True)
    return render_template('records.html', records=records)

@app.route('/export')
def export_page():
    """データ抽出ページ"""
    patients = load_patients()
    return render_template('export.html', patients=patients)

@app.route('/import')
def import_page():
    """データ受信ページ"""
    return render_template('import.html')


# ==================== API ====================

@app.route('/api/patients', methods=['GET'])
def api_get_patients():
    """患者一覧取得API"""
    patients = load_patients()
    return jsonify(patients)

@app.route('/api/patient/<patient_id>', methods=['GET'])
def api_get_patient(patient_id):
    """患者情報取得API"""
    patients = load_patients()
    patient = next((p for p in patients if p['patient_id'] == patient_id), None)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    return jsonify(patient)

@app.route('/api/patient/<patient_id>/records', methods=['GET'])
def api_get_patient_records(patient_id):
    """患者の診療記録取得API"""
    records = load_records()
    patient_records = [r for r in records if r['patient_id'] == patient_id]
    return jsonify(patient_records)


# ==================== データ抽出（Export） ====================

@app.route('/api/export/csv/<patient_id>', methods=['GET'])
def export_patient_csv(patient_id):
    """患者データをCSVでエクスポート"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../SecHack365_project'))
        from core.csv_handler import CSVHandler
        
        patients = load_patients()
        records = load_records()
        
        patient = next((p for p in patients if p['patient_id'] == patient_id), None)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        patient_records = [r for r in records if r['patient_id'] == patient_id]
        
        # CSV形式に変換
        handler = CSVHandler()
        csv_records = []
        
        for record in patient_records:
            csv_records.append({
                "patient_id": patient_id,
                "timestamp": record.get('date', ''),
                "symptoms": record.get('chief_complaint', ''),
                "diagnosis": record.get('diagnosis', ''),
                "diagnosis_details": record.get('notes', ''),
                "medication": record.get('treatment', ''),
                "medication_instructions": "",
                "treatment_plan": "",
                "follow_up": "",
                "patient_explanation": ""
            })
        
        csv_content = handler.export_to_csv(csv_records) if csv_records else handler.create_template_csv()
        
        # ファイルとして返す
        from io import BytesIO
        output = BytesIO()
        output.write(csv_content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'patient_{patient_id}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        print(f"CSV Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/fhir/<patient_id>', methods=['GET'])
def export_patient_fhir(patient_id):
    """患者データをFHIR形式でエクスポート"""
    try:
        from core.fhir_adapter import FHIRAdapter
        
        patients = load_patients()
        records = load_records()
        
        patient = next((p for p in patients if p['patient_id'] == patient_id), None)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        patient_records = [r for r in records if r['patient_id'] == patient_id]
        
        # 最新の記録を使用
        if patient_records:
            latest_record = max(patient_records, key=lambda x: x['date'])
            
            adapter = FHIRAdapter()
            medical_record = {
                "patient_id": patient_id,
                "symptoms": latest_record.get('chief_complaint', ''),
                "diagnosis": latest_record.get('diagnosis', ''),
                "diagnosis_details": latest_record.get('notes', ''),
                "medication": latest_record.get('treatment', ''),
                "medication_instructions": "",
                "treatment_plan": "",
                "follow_up": "",
                "patient_explanation": ""
            }
            
            fhir_bundle = adapter.export_to_fhir_bundle(medical_record, patient_id)
            return jsonify(json.loads(fhir_bundle))
        else:
            return jsonify({"error": "No records found"}), 404
            
    except Exception as e:
        print(f"FHIR Export Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== データ受信（Import） ====================

@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """CSVデータをインポート"""
    try:
        from core.csv_handler import CSVHandler
        
        if 'file' in request.files:
            file = request.files['file']
            csv_content = file.read().decode('utf-8')
        elif request.is_json:
            csv_content = request.get_json().get('csv_content')
        else:
            return jsonify({"error": "CSV data required"}), 400
        
        handler = CSVHandler()
        imported_records = handler.import_from_csv(csv_content)
        
        # 既存レコードに追加
        records = load_records()
        
        for imported in imported_records:
            new_record = {
                "record_id": f"REC{len(records) + 1:03d}",
                "patient_id": imported.get('patient_id', 'UNKNOWN'),
                "date": imported.get('timestamp', datetime.now().isoformat()),
                "doctor": "インポート",
                "department": "内科",
                "chief_complaint": imported.get('symptoms', ''),
                "diagnosis": imported.get('diagnosis', ''),
                "treatment": imported.get('medication', ''),
                "notes": imported.get('diagnosis_details', ''),
                "status": "完了"
            }
            records.append(new_record)
        
        save_records(records)
        
        return jsonify({
            "success": True,
            "imported_count": len(imported_records),
            "message": f"{len(imported_records)}件の記録をインポートしました"
        })
        
    except Exception as e:
        print(f"CSV Import Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/import/fhir', methods=['POST'])
def import_fhir():
    """FHIRデータをインポート"""
    try:
        from core.fhir_adapter import FHIRAdapter
        
        fhir_bundle = request.get_json()
        
        adapter = FHIRAdapter()
        medical_record = adapter.import_from_fhir_bundle(json.dumps(fhir_bundle))
        
        # 既存レコードに追加
        records = load_records()
        
        new_record = {
            "record_id": f"REC{len(records) + 1:03d}",
            "patient_id": medical_record.get('patient_id', 'UNKNOWN'),
            "date": datetime.now().isoformat(),
            "doctor": "インポート（FHIR）",
            "department": "内科",
            "chief_complaint": medical_record.get('symptoms', ''),
            "diagnosis": medical_record.get('diagnosis', ''),
            "treatment": medical_record.get('medication', ''),
            "notes": medical_record.get('diagnosis_details', ''),
            "status": "完了"
        }
        records.append(new_record)
        
        save_records(records)
        
        return jsonify({
            "success": True,
            "message": "FHIRデータをインポートしました"
        })
        
    except Exception as e:
        print(f"FHIR Import Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/import/record', methods=['POST'])
def import_record():
    """診療記録をインポート"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'データが提供されていません'}), 400
        
        # 必要なフィールドをチェック
        required_fields = ['patient_id', 'date', 'doctor', 'diagnosis']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field}が必要です'}), 400
        
        # 新しいレコードIDを生成
        records = load_records()
        new_record_id = f"REC{len(records) + 1:03d}"
        
        # 診療記録を作成
        # 受信した日時がUTCの場合は日本時間に変換
        received_date = data['date']
        if received_date.endswith('Z'):
            # UTC時刻を日本時間に変換
            from datetime import datetime, timezone, timedelta
            utc_time = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
            jst_time = utc_time.astimezone(timezone(timedelta(hours=9)))
            display_date = jst_time.isoformat()
        else:
            display_date = received_date
        
        new_record = {
            'record_id': new_record_id,
            'patient_id': data['patient_id'],
            'date': display_date,
            'doctor': data['doctor'],
            'department': data.get('department', '内科'),
            'chief_complaint': data.get('chief_complaint', ''),
            'diagnosis': data['diagnosis'],
            'treatment': data.get('treatment', ''),
            'notes': data.get('notes', ''),
            'status': data.get('status', '完了'),
            'doctor_notes': data.get('doctor_notes', '')
        }
        
        # レコードを追加
        records.append(new_record)
        save_records(records)
        
        print(f"[INFO] 診療記録をインポートしました: {new_record_id} - 患者{data['patient_id']}")
        
        return jsonify({
            'success': True, 
            'message': '診療記録をインポートしました',
            'record_id': new_record_id
        })
        
    except Exception as e:
        print(f"[ERROR] 診療記録インポートエラー: {e}")
        return jsonify({'success': False, 'error': f'診療記録のインポート中にエラーが発生しました: {str(e)}'}), 500


# ==================== WebAuthn認証 ====================

@app.route('/api/webauthn/register/begin', methods=['POST'])
def webauthn_register_begin():
    """WebAuthn登録開始（簡易版）"""
    print(f"[DEBUG] 登録開始エンドポイントにアクセスされました")
    print(f"[DEBUG] リクエストヘッダー: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"[DEBUG] 登録開始リクエスト: {data}")
        
        if not data:
            print(f"[ERROR] リクエストデータが空です")
            return jsonify({'error': 'リクエストデータが必要です'}), 400
            
        username = data.get('username', '')
        
        if not username:
            print(f"[ERROR] ユーザー名が空です")
            return jsonify({'error': 'ユーザー名が必要です'}), 400
        
        # 簡易的なモックレスポンス
        mock_options = {
            'challenge': base64.b64encode(b'mock_challenge').decode('utf-8'),
            'rp': {
                'id': 'localhost',
                'name': '患者情報共有システム'
            },
            'user': {
                'id': base64.b64encode(username.encode('utf-8')).decode('utf-8'),
                'name': username,
                'displayName': username
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},
                {'type': 'public-key', 'alg': -257}
            ],
            'timeout': 120000,
            'attestation': 'direct'
        }
        
        print(f"[DEBUG] モック登録オプション生成成功")
        
        return jsonify(mock_options)
        
    except Exception as e:
        print(f"[ERROR] WebAuthn登録開始エラー: {e}")
        import traceback
        print(f"[ERROR] スタックトレース: {traceback.format_exc()}")
        return jsonify({'error': f'登録の開始に失敗しました: {str(e)}'}), 500

@app.route('/api/webauthn/register/complete', methods=['POST'])
def webauthn_register_complete():
    """WebAuthn登録完了"""
    print(f"[DEBUG] 登録完了エンドポイントにアクセスされました")
    print(f"[DEBUG] リクエストヘッダー: {dict(request.headers)}")
    
    if not WEBAUTHN_AVAILABLE:
        print(f"[ERROR] WebAuthnライブラリが利用できません")
        return jsonify({'error': 'WebAuthnライブラリが利用できません'}), 500
    
    try:
        data = request.get_json()
        print(f"[DEBUG] 登録完了リクエスト: {data}")
        
        if not data:
            print(f"[ERROR] リクエストデータが空です")
            return jsonify({'error': 'リクエストデータが必要です'}), 400
            
        username = data.get('username', '')
        credential = data.get('credential', {})
        
        if not username:
            print(f"[ERROR] ユーザー名が空です")
            return jsonify({'error': 'ユーザー名が必要です'}), 400
            
        if not credential:
            print(f"[ERROR] 認証情報が空です")
            return jsonify({'error': '認証情報が必要です'}), 400
        
        # チャレンジを読み込み
        challenge_file = os.path.join(DATA_DIR, 'webauthn_challenge.json')
        if not os.path.exists(challenge_file):
            return jsonify({'error': 'チャレンジが見つかりません'}), 400
        
        with open(challenge_file, 'r') as f:
            challenge_data = json.load(f)
        
        if challenge_data['username'] != username:
            return jsonify({'error': 'ユーザー名が一致しません'}), 400
        
        # 簡易的な認証情報保存（検証をスキップ）
        try:
            print(f"[DEBUG] 認証情報を保存中: {credential}")
            
            # 認証情報を保存
            credentials = load_webauthn_credentials()
            credentials[username] = {
                'id': credential.get('id', 'mock_credential_id'),
                'public_key': 'mock_public_key',
                'counter': 0,
                'device_type': 'platform',
                'backed_up': False,
                'transports': ['internal']
            }
            save_webauthn_credentials(credentials)
            
            # チャレンジファイルを削除
            if os.path.exists(challenge_file):
                os.remove(challenge_file)
            
            print(f"[INFO] WebAuthn認証情報が登録されました: ユーザー={username}")
            return jsonify({
                'success': True,
                'message': 'WebAuthn認証情報が登録されました'
            })
            
        except Exception as e:
            print(f"[ERROR] WebAuthn認証情報保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': '認証情報の保存に失敗しました'}), 400
        
    except Exception as e:
        print(f"[ERROR] WebAuthn登録完了エラー: {e}")
        return jsonify({'error': '登録の完了に失敗しました'}), 500

@app.route('/api/webauthn/authenticate/begin', methods=['POST'])
def webauthn_authenticate_begin():
    """WebAuthn認証開始"""
    print(f"[DEBUG] 認証開始エンドポイントにアクセスされました")
    print(f"[DEBUG] リクエストヘッダー: {dict(request.headers)}")
    
    if not WEBAUTHN_AVAILABLE:
        print(f"[ERROR] WebAuthnライブラリが利用できません")
        return jsonify({'error': 'WebAuthnライブラリが利用できません'}), 500
    
    try:
        data = request.get_json()
        print(f"[DEBUG] 認証開始リクエスト: {data}")
        username = data.get('username', '')
        
        if not username:
            print(f"[ERROR] ユーザー名が空です")
            return jsonify({'error': 'ユーザー名が必要です'}), 400
        
        # 保存された認証情報を取得
        credentials = load_webauthn_credentials()
        print(f"[DEBUG] 読み込まれた認証情報: {credentials}")
        
        if username not in credentials:
            print(f"[ERROR] 登録されていないユーザーです: {username}")
            return jsonify({'error': '登録されていないユーザーです'}), 400
        
        user_credential = credentials[username]
        print(f"[DEBUG] ユーザー認証情報: {user_credential}")
        
        # 簡易的な認証オプション（モック）
        options = {
            'challenge': base64.b64encode(b'mock_auth_challenge').decode('utf-8'),
            'allowCredentials': [{
                'id': user_credential['id'],
                'type': 'public-key',
                'transports': user_credential['transports']
            }],
            'userVerification': 'preferred',
            'timeout': 120000
        }
        
        print(f"[DEBUG] 生成された認証オプション: {options}")
        
        # チャレンジを保存
        challenge_data = {
            'challenge': options['challenge'],
            'username': username,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(os.path.join(DATA_DIR, 'webauthn_challenge.json'), 'w') as f:
            json.dump(challenge_data, f)
        
        # WebAuthnオブジェクトを辞書形式に変換
        options_dict = {
            'challenge': options['challenge'],
            'rp': {
                'id': RP_ID,
                'name': 'Medical Record System'
            },
            'user': {
                'id': base64.b64encode(username.encode('utf-8')).decode('utf-8'),
                'name': username,
                'displayName': username
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},
                {'type': 'public-key', 'alg': -257}
            ],
            'timeout': 120000,
            'attestation': 'direct'
        }
        
        return jsonify(options_dict)
        
    except Exception as e:
        print(f"[ERROR] WebAuthn認証開始エラー: {e}")
        return jsonify({'error': '認証の開始に失敗しました'}), 500

@app.route('/api/webauthn/authenticate/complete', methods=['POST'])
def webauthn_authenticate_complete():
    """WebAuthn認証完了"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        credential = data.get('credential', {})
        
        # チャレンジを読み込み
        challenge_file = os.path.join(DATA_DIR, 'webauthn_challenge.json')
        if not os.path.exists(challenge_file):
            return jsonify({'error': 'チャレンジが見つかりません'}), 400
        
        with open(challenge_file, 'r') as f:
            challenge_data = json.load(f)
        
        if challenge_data['username'] != username:
            return jsonify({'error': 'ユーザー名が一致しません'}), 400
        
        # 保存された認証情報を取得
        credentials = load_webauthn_credentials()
        if username not in credentials:
            return jsonify({'error': '登録されていないユーザーです'}), 400
        
        user_credential = credentials[username]
        
        # 簡易的な認証成功（検証をスキップ）
        try:
            print(f"[DEBUG] 認証成功: {username}")
            
            # カウンターを更新
            credentials[username]['counter'] += 1
            save_webauthn_credentials(credentials)
            
            # チャレンジファイルを削除
            if os.path.exists(challenge_file):
                os.remove(challenge_file)
            
            print(f"[INFO] WebAuthn認証成功: ユーザー={username}")
            return jsonify({
                'success': True,
                'user': {
                    'username': username,
                    'role': 'doctor' if username.startswith('doctor') else 'admin' if username.startswith('admin') else 'patient'
                }
            })
            
        except Exception as e:
            print(f"[ERROR] WebAuthn認証保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': '認証の保存に失敗しました'}), 400
        
    except Exception as e:
        print(f"[ERROR] WebAuthn認証完了エラー: {e}")
        return jsonify({'error': '認証の完了に失敗しました'}), 500


# ==================== 起動 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("模擬電子カルテシステム (Dummy EHR System)")
    print("=" * 60)
    print("初期化中...")
    initialize_sample_data()
    print("サンプルデータを作成しました")
    print()
    print("起動設定:")
    print(f"  host=127.0.0.1")
    print(f"  port=5002")
    print("=" * 60)
    print("ブラウザで http://127.0.0.1:5002 にアクセスしてください")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5002, debug=True)

