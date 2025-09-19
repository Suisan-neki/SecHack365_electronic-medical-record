import json
import os

class ABACPolicyEnforcer:
    def __init__(self, policy_file="abac_policy.json"):
        self.policy_file = policy_file
        self.policies = self._load_policies()

    def _load_policies(self):
        # 実際にはセキュアなデータベースや設定管理システムを使用すべき
        try:
            with open(self.policy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # デフォルトポリシーを生成
            default_policies = {
                "rules": [
                    {
                        "name": "Doctor can view patient data",
                        "subject": {"role": "doctor"},
                        "action": "view",
                        "resource": {"type": "patient_data"},
                        "effect": "permit"
                    },
                    {
                        "name": "Admin can view and add patient data",
                        "subject": {"role": "admin"},
                        "action": ["view", "add"],
                        "resource": {"type": "patient_data"},
                        "effect": "permit"
                    },
                    {
                        "name": "Patient can view own data",
                        "subject": {"role": "patient", "id": "resource.patient_id"},
                        "action": "view",
                        "resource": {"type": "patient_data"},
                        "effect": "permit"
                    },
                    {
                        "name": "Doctor can add patient data",
                        "subject": {"role": "doctor"},
                        "action": "add",
                        "resource": {"type": "patient_data"},
                        "effect": "permit"
                    }
                ],
                "default_effect": "deny"
            }
            with open(self.policy_file, 'w', encoding='utf-8') as f:
                json.dump(default_policies, f, ensure_ascii=False, indent=4)
            return default_policies

    def _evaluate_rule(self, rule, subject_attributes, action, resource_attributes):
        # Subjectの評価
        for key, value in rule["subject"].items():
            if key == "id" and value == "resource.patient_id": # 患者自身のデータへのアクセス
                if subject_attributes.get("id") != resource_attributes.get("patient_id"):
                    return False
            elif subject_attributes.get(key) != value:
                return False

        # Actionの評価
        if isinstance(rule["action"], list):
            if action not in rule["action"]:
                return False
        elif action != rule["action"]:
            return False

        # Resourceの評価
        for key, value in rule["resource"].items():
            if resource_attributes.get(key) != value:
                return False
        
        return True

    def check_access(self, subject_attributes, action, resource_attributes):
        for rule in self.policies["rules"]:
            if self._evaluate_rule(rule, subject_attributes, action, resource_attributes):
                return rule["effect"] == "permit"
        
        return self.policies["default_effect"] == "permit"

# デモ用
if __name__ == "__main__":
    # 既存のabac_policy.jsonを削除してクリーンな状態にする
    if os.path.exists("abac_policy.json"):
        os.remove("abac_policy.json")

    enforcer = ABACPolicyEnforcer("abac_policy.json")

    # 医師が患者データを閲覧
    subject_doc = {"id": "doctor1", "role": "doctor"}
    resource_pat_data = {"type": "patient_data", "patient_id": "patient001"}
    print(f"医師(doctor1)が患者データ(patient001)を閲覧: {enforcer.check_access(subject_doc, 'view', resource_pat_data)}")

    # 患者が自身のデータを閲覧
    subject_pat = {"id": "patient001", "role": "patient"}
    print(f"患者(patient001)が自身のデータ(patient001)を閲覧: {enforcer.check_access(subject_pat, 'view', resource_pat_data)}")

    # 患者が他人のデータを閲覧
    resource_pat_data_other = {"type": "patient_data", "patient_id": "patient002"}
    print(f"患者(patient001)が患者データ(patient002)を閲覧: {enforcer.check_access(subject_pat, 'view', resource_pat_data_other)}")

    # 管理者が患者データを追加
    subject_admin = {"id": "admin1", "role": "admin"}
    print(f"管理者(admin1)が患者データ(patient001)を追加: {enforcer.check_access(subject_admin, 'add', resource_pat_data)}")

    # 患者が患者データを追加
    print(f"患者(patient001)が患者データ(patient001)を追加: {enforcer.check_access(subject_pat, 'add', resource_pat_data)}")

    # 存在しないアクション
    print(f"医師(doctor1)が患者データ(patient001)を削除: {enforcer.check_access(subject_doc, 'delete', resource_pat_data)}")
