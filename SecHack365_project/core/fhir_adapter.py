"""
FHIR アダプター
既存の電子カルテシステムとFHIR形式でデータ連携するためのモジュール
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import json

try:
    from fhir.resources.bundle import Bundle
    from fhir.resources.patient import Patient
    from fhir.resources.encounter import Encounter
    from fhir.resources.observation import Observation
    from fhir.resources.condition import Condition
    from fhir.resources.medicationrequest import MedicationRequest
    from fhir.resources.medication import Medication
    FHIR_AVAILABLE = True
except ImportError:
    FHIR_AVAILABLE = False
    print("[WARNING] fhir.resources not installed. FHIR functionality will be limited.")


class FHIRAdapter:
    """FHIR形式のデータと内部形式の変換を行うアダプター"""
    
    def __init__(self):
        if not FHIR_AVAILABLE:
            raise ImportError("fhir.resources package is required. Install with: pip install fhir.resources")
    
    def import_from_fhir_bundle(self, fhir_bundle_json: str) -> Dict[str, Any]:
        """
        FHIR Bundle形式のJSONを受け取り、内部形式に変換
        
        Args:
            fhir_bundle_json: FHIR Bundle形式のJSON文字列
            
        Returns:
            内部形式の医療記録辞書
        """
        try:
            bundle_dict = json.loads(fhir_bundle_json) if isinstance(fhir_bundle_json, str) else fhir_bundle_json
            bundle = Bundle(**bundle_dict)
            
            # 各リソースを抽出
            symptoms = []
            diagnosis = ""
            diagnosis_details = ""
            medication = ""
            medication_instructions = ""
            
            if bundle.entry:
                for entry in bundle.entry:
                    resource = entry.resource
                    
                    # Observation（症状・所見）
                    if resource.resource_type == "Observation":
                        obs = Observation(**resource.dict())
                        if obs.code and obs.code.text:
                            symptom_text = obs.code.text
                            if obs.valueString:
                                symptom_text += f": {obs.valueString}"
                            symptoms.append(symptom_text)
                    
                    # Condition（診断）
                    elif resource.resource_type == "Condition":
                        cond = Condition(**resource.dict())
                        if cond.code and cond.code.text:
                            diagnosis = cond.code.text
                        if cond.note:
                            diagnosis_details = "\n".join([note.text for note in cond.note if note.text])
                    
                    # MedicationRequest（処方）
                    elif resource.resource_type == "MedicationRequest":
                        med_req = MedicationRequest(**resource.dict())
                        med_text = ""
                        
                        # 薬剤名
                        if med_req.medicationCodeableConcept and med_req.medicationCodeableConcept.text:
                            med_text = med_req.medicationCodeableConcept.text
                        
                        # 用量
                        if med_req.dosageInstruction:
                            for dosage in med_req.dosageInstruction:
                                if dosage.doseAndRate:
                                    for dose in dosage.doseAndRate:
                                        if dose.doseQuantity:
                                            med_text += f" {dose.doseQuantity.value}{dose.doseQuantity.unit}"
                                
                                if dosage.timing and dosage.timing.code and dosage.timing.code.text:
                                    med_text += f" {dosage.timing.code.text}"
                                
                                if dosage.patientInstruction:
                                    medication_instructions += f"{dosage.patientInstruction}\n"
                        
                        # 日数
                        if med_req.dispenseRequest and med_req.dispenseRequest.expectedSupplyDuration:
                            duration = med_req.dispenseRequest.expectedSupplyDuration
                            med_text += f" {duration.value}{duration.unit}"
                        
                        if med_text:
                            medication += med_text + "、"
            
            # 症状を文字列に結合
            symptoms_text = "、".join(symptoms) if symptoms else ""
            medication = medication.rstrip("、")
            
            return {
                "symptoms": symptoms_text,
                "diagnosis": diagnosis,
                "diagnosis_details": diagnosis_details,
                "medication": medication,
                "medication_instructions": medication_instructions.strip(),
                "treatment_plan": "",  # FHIRから自動抽出は難しいため空欄
                "follow_up": "",
                "patient_explanation": ""
            }
            
        except Exception as e:
            raise ValueError(f"FHIR Bundle parsing failed: {str(e)}")
    
    def export_to_fhir_bundle(self, medical_record: Dict[str, Any], patient_id: str = "unknown") -> str:
        """
        内部形式の医療記録をFHIR Bundle形式のJSONに変換
        
        Args:
            medical_record: 内部形式の医療記録辞書
            patient_id: 患者ID
            
        Returns:
            FHIR Bundle形式のJSON文字列
        """
        try:
            bundle = Bundle(
                type="transaction",
                entry=[]
            )
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Observation（症状）
            if medical_record.get("symptoms"):
                symptoms_list = medical_record["symptoms"].split("、")
                for idx, symptom in enumerate(symptoms_list):
                    if symptom.strip():
                        obs = Observation(
                            id=f"obs-{idx}",
                            status="final",
                            code={
                                "text": symptom.strip()
                            },
                            subject={
                                "reference": f"Patient/{patient_id}"
                            },
                            effectiveDateTime=timestamp
                        )
                        bundle.entry.append({
                            "resource": obs,
                            "request": {
                                "method": "POST",
                                "url": "Observation"
                            }
                        })
            
            # Condition（診断）
            if medical_record.get("diagnosis"):
                cond = Condition(
                    id="condition-1",
                    clinicalStatus={
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }]
                    },
                    code={
                        "text": medical_record["diagnosis"]
                    },
                    subject={
                        "reference": f"Patient/{patient_id}"
                    },
                    recordedDate=timestamp
                )
                
                if medical_record.get("diagnosis_details"):
                    cond.note = [{
                        "text": medical_record["diagnosis_details"]
                    }]
                
                bundle.entry.append({
                    "resource": cond,
                    "request": {
                        "method": "POST",
                        "url": "Condition"
                    }
                })
            
            # MedicationRequest（処方）
            if medical_record.get("medication"):
                medications_list = medical_record["medication"].split("、")
                for idx, med in enumerate(medications_list):
                    if med.strip():
                        med_req = MedicationRequest(
                            id=f"medreq-{idx}",
                            status="active",
                            intent="order",
                            medicationCodeableConcept={
                                "text": med.strip()
                            },
                            subject={
                                "reference": f"Patient/{patient_id}"
                            },
                            authoredOn=timestamp
                        )
                        
                        if medical_record.get("medication_instructions"):
                            med_req.dosageInstruction = [{
                                "patientInstruction": medical_record["medication_instructions"]
                            }]
                        
                        bundle.entry.append({
                            "resource": med_req,
                            "request": {
                                "method": "POST",
                                "url": "MedicationRequest"
                            }
                        })
            
            return bundle.json(indent=2)
            
        except Exception as e:
            raise ValueError(f"FHIR Bundle creation failed: {str(e)}")


def create_sample_fhir_bundle() -> str:
    """テスト用のサンプルFHIR Bundleを作成"""
    if not FHIR_AVAILABLE:
        return json.dumps({"error": "FHIR library not available"})
    
    sample_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-1",
                    "status": "final",
                    "code": {
                        "text": "発熱"
                    },
                    "valueString": "38.5度",
                    "effectiveDateTime": datetime.utcnow().isoformat() + "Z"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "cond-1",
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }]
                    },
                    "code": {
                        "text": "急性上気道炎"
                    },
                    "recordedDate": datetime.utcnow().isoformat() + "Z"
                }
            }
        ]
    }
    
    return json.dumps(sample_data, indent=2, ensure_ascii=False)

