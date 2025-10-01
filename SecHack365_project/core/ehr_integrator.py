"""
電子カルテ連携モジュール
複数の電子カルテシステムとの連携を管理
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class EHRSystemType(Enum):
    """サポートする電子カルテシステムの種類"""
    EPIC = "epic"
    CERNER = "cerner"
    ALLSCRIPTS = "allscripts"
    GENERIC_FHIR = "generic_fhir"

class EHRIntegrator:
    """電子カルテシステム連携クラス"""
    
    def __init__(self):
        """EHR連携システムを初期化"""
        self.supported_systems = {
            EHRSystemType.EPIC: {
                "name": "Epic MyChart",
                "api_base_url": "https://api.epic.com/fhir/r4",
                "auth_type": "oauth2",
                "fhir_version": "R4"
            },
            EHRSystemType.CERNER: {
                "name": "Cerner PowerChart",
                "api_base_url": "https://fhir.cerner.com/r4",
                "auth_type": "oauth2",
                "fhir_version": "R4"
            },
            EHRSystemType.ALLSCRIPTS: {
                "name": "Allscripts Sunrise",
                "api_base_url": "https://api.allscripts.com/fhir/r4",
                "auth_type": "oauth2",
                "fhir_version": "R4"
            },
            EHRSystemType.GENERIC_FHIR: {
                "name": "Generic FHIR Server",
                "api_base_url": "http://localhost:8080/fhir",
                "auth_type": "none",
                "fhir_version": "R4"
            }
        }
        
        # デモ用の設定（実際の環境では環境変数から取得）
        self.demo_config = {
            "epic": {
                "client_id": "demo_client_id",
                "client_secret": "demo_client_secret",
                "redirect_uri": "http://localhost:5001/callback/epic"
            },
            "cerner": {
                "client_id": "demo_client_id",
                "client_secret": "demo_client_secret",
                "redirect_uri": "http://localhost:5001/callback/cerner"
            },
            "allscripts": {
                "client_id": "demo_client_id",
                "client_secret": "demo_client_secret",
                "redirect_uri": "http://localhost:5001/callback/allscripts"
            }
        }
    
    def validate_medical_data(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        医療データの妥当性を検証
        
        Args:
            medical_data (Dict[str, Any]): 検証する医療データ
            
        Returns:
            Dict[str, Any]: 検証結果
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 必須フィールドのチェック
        required_fields = ["diagnosis", "medication", "treatment_plan"]
        for field in required_fields:
            if not medical_data.get(field):
                validation_result["errors"].append(f"必須フィールドが不足しています: {field}")
                validation_result["is_valid"] = False
        
        # 診断名の長さチェック
        diagnosis = medical_data.get("diagnosis", "")
        if len(diagnosis) > 200:
            validation_result["warnings"].append("診断名が長すぎます（200文字以内を推奨）")
        
        # 処方薬の形式チェック
        medication = medical_data.get("medication", "")
        if medication and not any(char.isdigit() for char in medication):
            validation_result["warnings"].append("処方薬に用量が含まれていない可能性があります")
        
        # 患者説明文の存在チェック
        if not medical_data.get("patient_explanation"):
            validation_result["warnings"].append("患者向け説明文が不足しています")
        
        return validation_result
    
    def format_for_ehr_system(self, medical_data: Dict[str, Any], 
                            ehr_system_type: EHRSystemType) -> Dict[str, Any]:
        """
        医療データを電子カルテシステム用の形式に変換
        
        Args:
            medical_data (Dict[str, Any]): 元の医療データ
            ehr_system_type (EHRSystemType): 対象の電子カルテシステム
            
        Returns:
            Dict[str, Any]: 変換されたデータ
        """
        if ehr_system_type == EHRSystemType.GENERIC_FHIR:
            return self._format_for_fhir(medical_data)
        elif ehr_system_type == EHRSystemType.EPIC:
            return self._format_for_epic(medical_data)
        elif ehr_system_type == EHRSystemType.CERNER:
            return self._format_for_cerner(medical_data)
        elif ehr_system_type == EHRSystemType.ALLSCRIPTS:
            return self._format_for_allscripts(medical_data)
        else:
            return self._format_for_fhir(medical_data)  # デフォルトはFHIR
    
    def _format_for_fhir(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """FHIR形式に変換"""
        fhir_data = {
            "resourceType": "Bundle",
            "type": "document",
            "timestamp": datetime.now().isoformat(),
            "entry": []
        }
        
        # 診断情報（Condition）
        if medical_data.get("diagnosis"):
            condition = {
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "coding": [{
                            "system": "http://hl7.org/fhir/sid/icd-10-cm",
                            "code": "Z00.00",  # デモ用コード
                            "display": medical_data["diagnosis"]
                        }]
                    },
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }]
                    }
                }
            }
            fhir_data["entry"].append(condition)
        
        # 処方情報（MedicationRequest）
        if medical_data.get("medication"):
            medication_request = {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "medicationCodeableConcept": {
                        "text": medical_data["medication"]
                    },
                    "status": "active",
                    "intent": "order"
                }
            }
            fhir_data["entry"].append(medication_request)
        
        return fhir_data
    
    def _format_for_epic(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Epic形式に変換"""
        epic_data = {
            "patientId": medical_data.get("patient_id"),
            "encounterId": medical_data.get("session_id"),
            "diagnosis": {
                "primary": medical_data.get("diagnosis"),
                "details": medical_data.get("diagnosis_details")
            },
            "medications": [{
                "name": medical_data.get("medication"),
                "instructions": medical_data.get("medication_instructions")
            }],
            "treatmentPlan": medical_data.get("treatment_plan"),
            "followUp": medical_data.get("follow_up"),
            "timestamp": datetime.now().isoformat()
        }
        return epic_data
    
    def _format_for_cerner(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cerner形式に変換"""
        cerner_data = {
            "patient_identifier": medical_data.get("patient_id"),
            "encounter_identifier": medical_data.get("session_id"),
            "diagnosis_list": [{
                "diagnosis_name": medical_data.get("diagnosis"),
                "diagnosis_description": medical_data.get("diagnosis_details")
            }],
            "medication_orders": [{
                "medication_name": medical_data.get("medication"),
                "dosing_instructions": medical_data.get("medication_instructions")
            }],
            "care_plan": medical_data.get("treatment_plan"),
            "follow_up_instructions": medical_data.get("follow_up"),
            "created_datetime": datetime.now().isoformat()
        }
        return cerner_data
    
    def _format_for_allscripts(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Allscripts形式に変換"""
        allscripts_data = {
            "PatientID": medical_data.get("patient_id"),
            "EncounterID": medical_data.get("session_id"),
            "Diagnosis": {
                "Primary": medical_data.get("diagnosis"),
                "Description": medical_data.get("diagnosis_details")
            },
            "Medications": [{
                "DrugName": medical_data.get("medication"),
                "Instructions": medical_data.get("medication_instructions")
            }],
            "TreatmentPlan": medical_data.get("treatment_plan"),
            "FollowUp": medical_data.get("follow_up"),
            "DateTime": datetime.now().isoformat()
        }
        return allscripts_data
    
    def transfer_to_ehr_system(self, medical_data: Dict[str, Any], 
                             ehr_system_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        電子カルテシステムにデータを転送
        
        Args:
            medical_data (Dict[str, Any]): 転送する医療データ
            ehr_system_id (str): 電子カルテシステムID
            dry_run (bool): テスト実行かどうか
            
        Returns:
            Dict[str, Any]: 転送結果
        """
        try:
            # システムタイプを取得
            ehr_system_type = EHRSystemType(ehr_system_id)
            system_config = self.supported_systems[ehr_system_type]
            
            # データ検証
            validation_result = self.validate_medical_data(medical_data)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": "データ検証に失敗しました",
                    "validation_errors": validation_result["errors"]
                }
            
            # データ形式変換
            formatted_data = self.format_for_ehr_system(medical_data, ehr_system_type)
            
            if dry_run:
                # テスト実行の場合は実際の転送は行わない
                return {
                    "success": True,
                    "message": f"テスト実行完了: {system_config['name']}",
                    "formatted_data": formatted_data,
                    "validation_warnings": validation_result["warnings"]
                }
            
            # 実際の転送処理（デモ用）
            transfer_result = self._perform_transfer(formatted_data, ehr_system_type, system_config)
            
            return transfer_result
            
        except ValueError:
            return {
                "success": False,
                "error": f"サポートされていない電子カルテシステム: {ehr_system_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"転送処理中にエラーが発生しました: {str(e)}"
            }
    
    def _perform_transfer(self, formatted_data: Dict[str, Any], 
                         ehr_system_type: EHRSystemType, 
                         system_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        実際の転送処理を実行
        
        Args:
            formatted_data (Dict[str, Any]): フォーマット済みデータ
            ehr_system_type (EHRSystemType): 電子カルテシステムタイプ
            system_config (Dict[str, Any]): システム設定
            
        Returns:
            Dict[str, Any]: 転送結果
        """
        try:
            # デモ用の転送処理
            # 実際の実装では、各システムのAPIにHTTPリクエストを送信
            
            if system_config["auth_type"] == "oauth2":
                # OAuth2認証が必要な場合
                access_token = self._get_access_token(ehr_system_type)
                if not access_token:
                    return {
                        "success": False,
                        "error": "認証トークンの取得に失敗しました"
                    }
            
            # 転送先URLの構築
            api_url = f"{system_config['api_base_url']}/Bundle"
            
            # デモ用のレスポンス
            demo_response = {
                "success": True,
                "message": f"{system_config['name']}への転送が完了しました",
                "transfer_id": f"demo_transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "ehr_system": system_config['name']
            }
            
            print(f"[EHR] 転送完了: {system_config['name']} - {demo_response['transfer_id']}")
            return demo_response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"転送処理エラー: {str(e)}"
            }
    
    def _get_access_token(self, ehr_system_type: EHRSystemType) -> Optional[str]:
        """
        OAuth2アクセストークンを取得
        
        Args:
            ehr_system_type (EHRSystemType): 電子カルテシステムタイプ
            
        Returns:
            Optional[str]: アクセストークン
        """
        # デモ用の実装
        # 実際の実装では、OAuth2フローを実行してトークンを取得
        system_name = ehr_system_type.value
        if system_name in self.demo_config:
            return f"demo_access_token_{system_name}_{datetime.now().strftime('%Y%m%d')}"
        return None
    
    def test_connection(self, ehr_system_id: str) -> Dict[str, Any]:
        """
        電子カルテシステムとの接続をテスト
        
        Args:
            ehr_system_id (str): 電子カルテシステムID
            
        Returns:
            Dict[str, Any]: 接続テスト結果
        """
        try:
            ehr_system_type = EHRSystemType(ehr_system_id)
            system_config = self.supported_systems[ehr_system_type]
            
            # デモ用の接続テスト
            test_result = {
                "success": True,
                "message": f"{system_config['name']}との接続テストが成功しました",
                "system_name": system_config['name'],
                "api_base_url": system_config['api_base_url'],
                "fhir_version": system_config['fhir_version'],
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[EHR] 接続テスト成功: {system_config['name']}")
            return test_result
            
        except ValueError:
            return {
                "success": False,
                "error": f"サポートされていない電子カルテシステム: {ehr_system_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"接続テストエラー: {str(e)}"
            }
    
    def get_supported_systems(self) -> List[Dict[str, Any]]:
        """
        サポートされている電子カルテシステムの一覧を取得
        
        Returns:
            List[Dict[str, Any]]: システム一覧
        """
        systems = []
        for system_type, config in self.supported_systems.items():
            systems.append({
                "id": system_type.value,
                "name": config["name"],
                "api_base_url": config["api_base_url"],
                "auth_type": config["auth_type"],
                "fhir_version": config["fhir_version"]
            })
        return systems

# グローバルEHR連携インスタンス
ehr_integrator = EHRIntegrator()
