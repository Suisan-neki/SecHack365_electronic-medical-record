import os
import json
import gzip
from datetime import datetime, timedelta
import shutil

class AuditLogManager:
    """
    監査ログの管理とローテーション機能
    """
    
    def __init__(self, log_file="audit.log", max_file_size_mb=10, retention_days=90):
        self.log_file = log_file
        self.max_file_size = max_file_size_mb * 1024 * 1024  # MB to bytes
        self.retention_days = retention_days
        self.log_dir = os.path.dirname(log_file) or "."
        
    def check_rotation_needed(self):
        """ログローテーションが必要かチェック"""
        if not os.path.exists(self.log_file):
            return False
            
        file_size = os.path.getsize(self.log_file)
        return file_size > self.max_file_size
    
    def rotate_log(self):
        """ログファイルをローテーション"""
        if not os.path.exists(self.log_file):
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_file = f"{self.log_file}.{timestamp}"
        
        # 現在のログファイルをリネーム
        shutil.move(self.log_file, archived_file)
        
        # gzip圧縮
        with open(archived_file, 'rb') as f_in:
            with gzip.open(f"{archived_file}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 元のファイルを削除
        os.remove(archived_file)
        
        print(f"[AUDIT] ログローテーション完了: {archived_file}.gz")
    
    def cleanup_old_logs(self):
        """古いログファイルを削除"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.log_dir):
            if filename.startswith(os.path.basename(self.log_file)) and filename.endswith('.gz'):
                file_path = os.path.join(self.log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"[AUDIT] 古いログファイルを削除: {filename}")
    
    def get_log_statistics(self):
        """ログファイルの統計情報を取得"""
        stats = {
            'current_file_size_mb': 0,
            'total_entries': 0,
            'oldest_entry': None,
            'newest_entry': None,
            'archived_files': 0
        }
        
        # 現在のログファイル
        if os.path.exists(self.log_file):
            stats['current_file_size_mb'] = round(os.path.getsize(self.log_file) / (1024 * 1024), 2)
            
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    stats['total_entries'] = len([l for l in lines if l.strip()])
                    
                    if lines:
                        # 最初と最後のエントリの時刻
                        first_entry = json.loads(lines[0].strip())
                        last_entry = json.loads(lines[-1].strip())
                        stats['oldest_entry'] = first_entry.get('timestamp')
                        stats['newest_entry'] = last_entry.get('timestamp')
            except:
                pass
        
        # アーカイブファイル数
        for filename in os.listdir(self.log_dir):
            if filename.startswith(os.path.basename(self.log_file)) and filename.endswith('.gz'):
                stats['archived_files'] += 1
        
        return stats

# デモ用
if __name__ == "__main__":
    manager = AuditLogManager("audit.log", max_file_size_mb=1, retention_days=30)
    
    print("=== 監査ログ管理システム ===")
    stats = manager.get_log_statistics()
    
    print(f"現在のファイルサイズ: {stats['current_file_size_mb']} MB")
    print(f"総エントリ数: {stats['total_entries']}")
    print(f"アーカイブファイル数: {stats['archived_files']}")
    
    if manager.check_rotation_needed():
        print("ログローテーションが必要です")
        manager.rotate_log()
    
    manager.cleanup_old_logs()
