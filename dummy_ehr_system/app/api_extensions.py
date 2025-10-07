"""
API拡張機能

追加のAPIエンドポイントとヘルパー関数を提供
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import sys
from pathlib import Path

# システム管理モジュールをインポート
sys.path.append(str(Path(__file__).parent.parent))
from utils.system_manager import SystemManager

# ログ設定
logger = logging.getLogger(__name__)

# システム管理インスタンスを作成
system_manager = SystemManager(os.path.dirname(os.path.dirname(__file__)))

# Blueprintを作成
api_extensions = Blueprint('api_extensions', __name__)

def require_api_key(f):
    """APIキー認証デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('API_KEY', 'default-api-key')
        
        if not api_key or api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def handle_errors(f):
    """エラーハンドリングデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return jsonify({'error': 'Required file not found'}), 404
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return jsonify({'error': 'Invalid JSON data'}), 400
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

@api_extensions.route('/api/health', methods=['GET'])
@handle_errors
def health_check():
    """システムの健全性チェック"""
    # システム管理クラスを使用してヘルスチェックを実行
    health_status = system_manager.check_system_health()
    
    # ログ記録
    logger.info(f"システムヘルスチェック実行: {health_status['overall_status']}")
    
    status_code = 200 if health_status['overall_status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@api_extensions.route('/api/statistics', methods=['GET'])
@handle_errors
def get_statistics():
    """システム統計情報を取得"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'patients': get_patient_statistics(),
        'medical_records': get_medical_record_statistics(),
        'system': get_system_statistics()
    }
    
    return jsonify(stats)

@api_extensions.route('/api/patients/search', methods=['GET'])
@handle_errors
def search_patients():
    """患者検索"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    patients = load_patients_from_file()
    matching_patients = []
    
    for patient in patients:
        # 名前、カナ、IDで検索
        searchable_text = f"{patient.get('name', '')} {patient.get('name_kana', '')} {patient.get('patient_id', '')}"
        
        if query.lower() in searchable_text.lower():
            matching_patients.append(patient)
            
            if len(matching_patients) >= limit:
                break
    
    return jsonify({
        'query': query,
        'results': matching_patients,
        'total': len(matching_patients)
    })

@api_extensions.route('/api/medical-records/recent', methods=['GET'])
@handle_errors
def get_recent_records():
    """最近の医療記録を取得"""
    days = int(request.args.get('days', 7))
    limit = int(request.args.get('limit', 20))
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    records = load_medical_records_from_file()
    recent_records = []
    
    for record in records:
        try:
            record_date = datetime.strptime(record.get('date', ''), '%Y-%m-%d')
            if record_date >= cutoff_date:
                recent_records.append(record)
                
                if len(recent_records) >= limit:
                    break
        except ValueError:
            continue
    
    # 日付でソート（新しい順）
    recent_records.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return jsonify({
        'days': days,
        'records': recent_records,
        'total': len(recent_records)
    })

@api_extensions.route('/api/patients/<patient_id>/summary', methods=['GET'])
@handle_errors
def get_patient_summary(patient_id: str):
    """患者のサマリー情報を取得"""
    patients = load_patients_from_file()
    patient = next((p for p in patients if p.get('patient_id') == patient_id), None)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    records = load_medical_records_from_file()
    patient_records = [r for r in records if r.get('patient_id') == patient_id]
    
    # 統計を計算
    total_visits = len(patient_records)
    
    # 診断の頻度
    diagnoses = [r.get('diagnosis', '') for r in patient_records if r.get('diagnosis')]
    diagnosis_counts = {}
    for diagnosis in diagnoses:
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
    
    # 最後の受診日
    last_visit = None
    if patient_records:
        dates = [r.get('date', '') for r in patient_records if r.get('date')]
        if dates:
            last_visit = max(dates)
    
    # 年齢計算
    age = None
    if patient.get('birth_date'):
        try:
            birth_date = datetime.strptime(patient['birth_date'], '%Y-%m-%d')
            age = (datetime.now() - birth_date).days // 365
        except ValueError:
            pass
    
    summary = {
        'patient_id': patient_id,
        'name': patient.get('name'),
        'age': age,
        'total_visits': total_visits,
        'last_visit': last_visit,
        'common_diagnoses': dict(sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
        'patient_info': patient
    }
    
    return jsonify(summary)

@api_extensions.route('/api/export/patients', methods=['GET'])
@require_api_key
@handle_errors
def export_patients():
    """患者データのエクスポート"""
    format_type = request.args.get('format', 'json')
    
    patients = load_patients_from_file()
    
    if format_type == 'csv':
        # CSV形式でエクスポート
        import csv
        import io
        
        output = io.StringIO()
        if patients:
            fieldnames = patients[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(patients)
        
        csv_data = output.getvalue()
        output.close()
        
        return jsonify({
            'format': 'csv',
            'data': csv_data,
            'filename': f'patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
    
    else:  # JSON形式
        return jsonify({
            'format': 'json',
            'data': patients,
            'filename': f'patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        })

@api_extensions.route('/api/import/patients', methods=['POST'])
@require_api_key
@handle_errors
def import_patients():
    """患者データのインポート"""
    if not request.is_json:
        return jsonify({'error': 'JSON data is required'}), 400
    
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({'error': 'Data must be an array of patients'}), 400
    
    # データの検証
    validation_errors = validate_patient_data(data)
    if validation_errors:
        return jsonify({'error': 'Data validation failed', 'details': validation_errors}), 400
    
    # 既存の患者データを読み込み
    existing_patients = load_patients_from_file()
    existing_ids = {p.get('patient_id') for p in existing_patients}
    
    # 重複チェック
    new_patients = []
    duplicates = []
    
    for patient in data:
        if patient.get('patient_id') in existing_ids:
            duplicates.append(patient.get('patient_id'))
        else:
            new_patients.append(patient)
            existing_patients.append(patient)
    
    # データを保存
    if new_patients:
        save_patients_to_file(existing_patients)
    
    return jsonify({
        'imported': len(new_patients),
        'duplicates': len(duplicates),
        'duplicate_ids': duplicates,
        'total_patients': len(existing_patients)
    })

@api_extensions.route('/api/system/backup', methods=['POST'])
@require_api_key
@handle_errors
def create_system_backup():
    """システムバックアップの作成"""
    backup_name = request.json.get('name') if request.is_json else None
    
    # システム管理クラスを使用してバックアップを作成
    result = system_manager.create_backup(backup_name)
    
    # ログ記録
    if result['status'] == 'success':
        logger.info(f"バックアップ作成成功: {result['backup_name']}")
    else:
        logger.error(f"バックアップ作成失敗: {result.get('message', 'Unknown error')}")
    
    return jsonify(result)

@api_extensions.route('/api/system/logs', methods=['GET'])
@require_api_key
@handle_errors
def get_system_logs():
    """システムログの取得"""
    lines = int(request.args.get('lines', 100))
    
    try:
        # システム管理クラスからログファイルを読み取り
        log_file = system_manager.log_file
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                all_logs = f.readlines()
            
            # 指定された行数を取得（最新のもの）
            recent_logs = all_logs[-lines:] if len(all_logs) > lines else all_logs
            
            return jsonify({
                'logs': [log.strip() for log in recent_logs],
                'total_lines': len(all_logs),
                'requested_lines': lines,
                'log_file': str(log_file)
            })
        else:
            return jsonify({
                'logs': [],
                'total_lines': 0,
                'requested_lines': lines,
                'message': 'ログファイルが見つかりません'
            })
    except Exception as e:
        logger.error(f"ログ取得エラー: {e}")
        return jsonify({'error': 'ログの取得に失敗しました'}), 500

# ヘルパー関数

def get_system_uptime() -> str:
    """システムの稼働時間を取得"""
    # 簡略化された実装
    return "24 hours"

def check_database_health() -> Dict[str, Any]:
    """データベースの健全性をチェック"""
    try:
        # データファイルの存在確認
        data_files = ['patients.json', 'medical_records.json']
        for file_name in data_files:
            if not os.path.exists(f'data/{file_name}'):
                return {'status': 'unhealthy', 'message': f'Missing file: {file_name}'}
        
        return {'status': 'healthy', 'message': 'All data files accessible'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def check_filesystem_health() -> Dict[str, Any]:
    """ファイルシステムの健全性をチェック"""
    try:
        # ディスク容量の簡易チェック
        import shutil
        total, used, free = shutil.disk_usage('.')
        usage_percent = (used / total) * 100
        
        if usage_percent > 90:
            return {'status': 'warning', 'message': f'Disk usage: {usage_percent:.1f}%'}
        else:
            return {'status': 'healthy', 'message': f'Disk usage: {usage_percent:.1f}%'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def check_memory_health() -> Dict[str, Any]:
    """メモリの健全性をチェック"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            return {'status': 'warning', 'message': f'Memory usage: {memory.percent:.1f}%'}
        else:
            return {'status': 'healthy', 'message': f'Memory usage: {memory.percent:.1f}%'}
    except ImportError:
        return {'status': 'info', 'message': 'Memory monitoring not available'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def get_patient_statistics() -> Dict[str, Any]:
    """患者統計を取得"""
    patients = load_patients_from_file()
    
    if not patients:
        return {'total': 0}
    
    # 性別統計
    gender_counts = {}
    age_groups = {'0-18': 0, '19-30': 0, '31-50': 0, '51-65': 0, '66+': 0}
    
    for patient in patients:
        # 性別統計
        gender = patient.get('gender', '不明')
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        # 年齢グループ統計
        try:
            birth_date = datetime.strptime(patient.get('birth_date', ''), '%Y-%m-%d')
            age = (datetime.now() - birth_date).days // 365
            
            if age <= 18:
                age_groups['0-18'] += 1
            elif age <= 30:
                age_groups['19-30'] += 1
            elif age <= 50:
                age_groups['31-50'] += 1
            elif age <= 65:
                age_groups['51-65'] += 1
            else:
                age_groups['66+'] += 1
        except ValueError:
            continue
    
    return {
        'total': len(patients),
        'by_gender': gender_counts,
        'by_age_group': age_groups
    }

def get_medical_record_statistics() -> Dict[str, Any]:
    """医療記録統計を取得"""
    records = load_medical_records_from_file()
    
    if not records:
        return {'total': 0}
    
    # 診断統計
    diagnoses = [r.get('diagnosis', '') for r in records if r.get('diagnosis')]
    diagnosis_counts = {}
    for diagnosis in diagnoses:
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
    
    # 月別統計
    monthly_counts = {}
    for record in records:
        try:
            date = datetime.strptime(record.get('date', ''), '%Y-%m-%d')
            month_key = date.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        except ValueError:
            continue
    
    return {
        'total': len(records),
        'top_diagnoses': dict(sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        'monthly_counts': monthly_counts
    }

def get_system_statistics() -> Dict[str, Any]:
    """システム統計を取得"""
    return {
        'api_endpoints': 15,
        'uptime': get_system_uptime(),
        'version': '1.0.0'
    }

def load_patients_from_file() -> List[Dict[str, Any]]:
    """患者データをファイルから読み込み"""
    try:
        with open('data/patients.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_medical_records_from_file() -> List[Dict[str, Any]]:
    """医療記録をファイルから読み込み"""
    try:
        with open('data/medical_records.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_patients_to_file(patients: List[Dict[str, Any]]) -> bool:
    """患者データをファイルに保存"""
    try:
        with open('data/patients.json', 'w', encoding='utf-8') as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save patients: {e}")
        return False

def validate_patient_data(patients: List[Dict[str, Any]]) -> List[str]:
    """患者データの検証"""
    errors = []
    required_fields = ['patient_id', 'name', 'birth_date', 'gender']
    
    for i, patient in enumerate(patients):
        for field in required_fields:
            if field not in patient or not patient[field]:
                errors.append(f"Patient {i}: Missing required field '{field}'")
    
    return errors
