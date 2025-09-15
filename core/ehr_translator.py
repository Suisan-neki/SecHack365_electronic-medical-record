"""
標準型電子カルテ（FHIR風JSON）から患者向け情報への変換機能
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class EHRTranslator:
    """電子カルテデータを患者向けに翻訳するクラス"""
    
    def __init__(self):
        # 医療用語の患者向け説明辞書
        self.medical_terms = {
            "Essential (primary) hypertension": {
                "simple_name": "高血圧",
                "explanation": "血管にかかる圧力が正常より高い状態です。放置すると心臓や血管に負担がかかります。",
                "icon": "🩸",
                "severity": "moderate"
            },
            "Pure hypercholesterolemia": {
                "simple_name": "高コレステロール血症", 
                "explanation": "血液中のコレステロール（脂質）が多すぎる状態です。動脈硬化の原因になります。",
                "icon": "🧈",
                "severity": "moderate"
            }
        }
        
        self.medication_explanations = {
            "アムロジピン": {
                "category": "血圧を下げる薬",
                "how_it_works": "血管を広げて血圧を下げます",
                "common_effects": "めまい、むくみが起こることがあります",
                "icon": "💊",
                "color": "#e74c3c"
            },
            "アトルバスタチン": {
                "category": "コレステロールを下げる薬", 
                "how_it_works": "肝臓でのコレステロール合成を抑えます",
                "common_effects": "筋肉痛、肝機能の変化に注意が必要です",
                "icon": "💊",
                "color": "#3498db"
            }
        }
    
    def translate_ehr_bundle(self, ehr_data: Dict) -> Dict:
        """FHIR Bundle全体を患者向け情報に変換"""
        
        if ehr_data.get("resourceType") != "Bundle":
            raise ValueError("無効なFHIR Bundleデータです")
        
        # リソースを種類別に分類
        resources = self._categorize_resources(ehr_data.get("entry", []))
        
        # 患者向け情報を構築
        patient_info = self._extract_patient_info(resources.get("Patient", []))
        conditions = self._translate_conditions(resources.get("Condition", []))
        medications = self._translate_medications(resources.get("MedicationStatement", []))
        test_results = self._translate_observations(resources.get("Observation", []))
        visit_summary = self._translate_encounters(resources.get("Encounter", []))
        
        return {
            "patient_info": patient_info,
            "current_conditions": conditions,
            "medications": medications,
            "recent_test_results": test_results,
            "visit_summary": visit_summary,
            "translation_metadata": {
                "translated_at": datetime.now().isoformat(),
                "source_data_timestamp": ehr_data.get("timestamp"),
                "translator_version": "1.0.0"
            }
        }
    
    def _categorize_resources(self, entries: List[Dict]) -> Dict[str, List[Dict]]:
        """リソースを種類別に分類"""
        categorized = {}
        
        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")
            
            if resource_type:
                if resource_type not in categorized:
                    categorized[resource_type] = []
                categorized[resource_type].append(resource)
        
        return categorized
    
    def _extract_patient_info(self, patients: List[Dict]) -> Dict:
        """患者基本情報を抽出"""
        if not patients:
            return {}
        
        patient = patients[0]  # 最初の患者情報を使用
        
        # 名前を抽出
        name = ""
        if patient.get("name"):
            name_obj = patient["name"][0]
            family = name_obj.get("family", "")
            given = " ".join(name_obj.get("given", []))
            name = f"{family} {given}".strip()
        
        # 年齢を計算
        age = ""
        if patient.get("birthDate"):
            birth_date = datetime.fromisoformat(patient["birthDate"])
            today = datetime.now()
            age = today.year - birth_date.year
            # 誕生日がまだ来ていない場合は1歳引く
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            
            # デバッグ情報（本番では削除）
            print(f"誕生日: {birth_date.strftime('%Y年%m月%d日')}, 現在: {today.strftime('%Y年%m月%d日')}, 計算年齢: {age}歳")
        
        # 性別を日本語に変換
        gender_map = {"male": "男性", "female": "女性", "other": "その他", "unknown": "不明"}
        gender = gender_map.get(patient.get("gender"), "不明")
        
        return {
            "name": name,
            "age": age,
            "gender": gender,
            "patient_id": patient.get("id", "")
        }
    
    def _translate_conditions(self, conditions: List[Dict]) -> List[Dict]:
        """病気・症状を患者向けに翻訳"""
        translated = []
        
        for condition in conditions:
            if condition.get("clinicalStatus", {}).get("coding", [{}])[0].get("code") != "active":
                continue  # アクティブな状態のみ
            
            code_obj = condition.get("code", {})
            display_name = ""
            
            # ICD-10コードから表示名を取得
            for coding in code_obj.get("coding", []):
                if coding.get("display"):
                    display_name = coding["display"]
                    break
            
            # 患者向け説明を取得
            explanation_data = self.medical_terms.get(display_name, {
                "simple_name": code_obj.get("text", display_name),
                "explanation": "担当医師にご相談ください。",
                "icon": "🏥",
                "severity": "unknown"
            })
            
            onset_date = condition.get("onsetDateTime", "")
            if onset_date:
                onset_date = datetime.fromisoformat(onset_date.replace("Z", "+00:00")).strftime("%Y年%m月%d日")
            
            translated.append({
                "name": explanation_data["simple_name"],
                "explanation": explanation_data["explanation"],
                "icon": explanation_data["icon"],
                "severity": explanation_data["severity"],
                "diagnosed_date": onset_date,
                "status": "治療中"
            })
        
        return translated
    
    def _translate_medications(self, medications: List[Dict]) -> List[Dict]:
        """処方薬を患者向けに翻訳"""
        translated = []
        
        for med in medications:
            if med.get("status") != "active":
                continue  # アクティブな処方のみ
            
            med_concept = med.get("medicationCodeableConcept", {})
            med_name = med_concept.get("text", "")
            
            # 薬剤名から主成分を抽出（簡易版）
            main_ingredient = ""
            for ingredient in self.medication_explanations.keys():
                if ingredient in med_name:
                    main_ingredient = ingredient
                    break
            
            explanation_data = self.medication_explanations.get(main_ingredient, {
                "category": "処方薬",
                "how_it_works": "担当医師にご相談ください",
                "common_effects": "副作用については医師・薬剤師にご相談ください",
                "icon": "💊",
                "color": "#95a5a6"
            })
            
            # 用法用量を抽出
            dosage_text = ""
            if med.get("dosage"):
                dosage_text = med["dosage"][0].get("text", "")
            
            # 医師のメモを抽出
            notes = ""
            if med.get("note"):
                notes = med["note"][0].get("text", "")
            
            translated.append({
                "name": med_name,
                "category": explanation_data["category"],
                "how_it_works": explanation_data["how_it_works"],
                "dosage": dosage_text,
                "notes": notes,
                "common_effects": explanation_data["common_effects"],
                "icon": explanation_data["icon"],
                "color": explanation_data["color"]
            })
        
        return translated
    
    def _translate_observations(self, observations: List[Dict]) -> List[Dict]:
        """検査結果を患者向けに翻訳"""
        translated = []
        
        for obs in observations:
            if obs.get("status") != "final":
                continue  # 確定結果のみ
            
            code_obj = obs.get("code", {})
            test_name = code_obj.get("text", "検査")
            
            test_date = obs.get("effectiveDateTime", "")
            if test_date:
                test_date = datetime.fromisoformat(test_date.replace("Z", "+00:00")).strftime("%Y年%m月%d日")
            
            # コンポーネント（複数の測定値）を処理
            components = obs.get("component", [])
            if components:
                for component in components:
                    comp_code = component.get("code", {})
                    comp_name = comp_code.get("coding", [{}])[0].get("display", "")
                    
                    value_qty = component.get("valueQuantity", {})
                    value = value_qty.get("value", "")
                    unit = value_qty.get("unit", "")
                    
                    # 基準範囲をチェック
                    ref_range = component.get("referenceRange", [])
                    status = "正常"
                    status_icon = "✅"
                    
                    if ref_range:
                        low = ref_range[0].get("low", {}).get("value", 0)
                        high = ref_range[0].get("high", {}).get("value", 999999)
                        
                        if value < low:
                            status = "低値"
                            status_icon = "⬇️"
                        elif value > high:
                            status = "高値"
                            status_icon = "⬆️"
                    
                    # 患者向けの説明
                    explanation = ""
                    if "Systolic" in comp_name:
                        explanation = "上の血圧（心臓が収縮した時の圧力）"
                    elif "Diastolic" in comp_name:
                        explanation = "下の血圧（心臓が拡張した時の圧力）"
                    elif "LDL" in comp_name:
                        explanation = "悪玉コレステロール（動脈硬化の原因となる）"
                    elif "HDL" in comp_name:
                        explanation = "善玉コレステロール（動脈硬化を防ぐ）"
                    
                    translated.append({
                        "test_name": test_name,
                        "item_name": explanation or comp_name,
                        "value": f"{value} {unit}",
                        "status": status,
                        "status_icon": status_icon,
                        "test_date": test_date,
                        "reference_range": f"{ref_range[0].get('low', {}).get('value', '')}-{ref_range[0].get('high', {}).get('value', '')} {unit}" if ref_range else ""
                    })
            
            # 医師のコメント
            notes = ""
            if obs.get("note"):
                notes = obs["note"][0].get("text", "")
            
            if notes and translated:
                translated[-1]["doctor_comment"] = notes
        
        return translated
    
    def _translate_encounters(self, encounters: List[Dict]) -> List[Dict]:
        """受診履歴を患者向けに翻訳"""
        translated = []
        
        for encounter in encounters:
            encounter_type = ""
            if encounter.get("type"):
                encounter_type = encounter["type"][0].get("text", "診察")
            
            period = encounter.get("period", {})
            visit_date = ""
            if period.get("start"):
                visit_date = datetime.fromisoformat(period["start"].replace("Z", "+00:00")).strftime("%Y年%m月%d日")
            
            reason = ""
            if encounter.get("reasonCode"):
                reason = encounter["reasonCode"][0].get("text", "")
            
            translated.append({
                "visit_type": encounter_type,
                "visit_date": visit_date,
                "reason": reason,
                "status": "完了" if encounter.get("status") == "finished" else "進行中"
            })
        
        return translated
