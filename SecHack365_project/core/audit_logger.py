import logging
import json
from datetime import datetime
import os

class AuditLogger:
    def __init__(self, log_file="audit.log", log_level=logging.INFO):
        self.logger = logging.getLogger("audit_logger")
        self.logger.setLevel(log_level)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)

        formatter = AuditJSONFormatter()
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_event(self, event_id, user_id, user_role, ip_address, action, resource, status, message, details=None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_id": event_id,
            "user_id": user_id,
            "user_role": user_role,
            "ip_address": ip_address,
            "action": action,
            "resource": resource,
            "status": status,
            "message": message,
            "details": details if details is not None else {}
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

class AuditJSONFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()

# デモ用
if __name__ == "__main__":
    # 基本的なテスト
    audit_logger = AuditLogger("test_audit.log")
    
    audit_logger.log_event(
        event_id="TEST_EVENT",
        user_id="test_user",
        user_role="admin",
        ip_address="127.0.0.1",
        action="TEST",
        resource="/test",
        status="SUCCESS",
        message="テストイベントです",
        details={"test": True}
    )
    
    print("監査ログテストが完了しました。test_audit.logを確認してください。")
