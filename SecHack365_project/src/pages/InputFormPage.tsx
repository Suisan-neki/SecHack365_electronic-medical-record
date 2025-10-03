import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '../store/useAppStore';
import { api } from '../api/client';
import { Tag, SymptomCategory, SymptomPreset } from '../types';
import Button from '../components/Button';
import Input from '../components/Input';
import TagSelector from '../components/TagSelector';
import MedicationCombination from '../components/MedicationCombination';
import LoadingSpinner from '../components/LoadingSpinner';

const InputFormPage: React.FC = () => {
  const navigate = useNavigate();
  const { 
    currentPatient, 
    selectedTags, 
    medicationCombinations,
    formData,
    setSelectedTags,
    addSelectedTag,
    removeSelectedTag,
    setMedicationCombinations,
    addMedicationCombination,
    removeMedicationCombination,
    updateMedicationCombination,
    updateFormField,
    setError,
    setLoading
  } = useAppStore();

  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({
    cold: false,
    pain: true,
    gastro: true,
    general: true,
    cardio: true,
    other: true
  });

  const [medicationCounter, setMedicationCounter] = useState(0);

  // タグデータを取得
  const { data: symptomTags, isLoading: tagsLoading } = useQuery({
    queryKey: ['symptomTags'],
    queryFn: () => api.getSymptomTags(),
  });

  // 症状プリセット
  const symptomPresets: SymptomPreset[] = [
    { id: 'cold', name: '🤧 風邪症状', symptoms: ['発熱', '咳', '鼻水', 'のどの痛み'], icon: '🤧' },
    { id: 'flu', name: '🤒 インフル症状', symptoms: ['高熱', '頭痛', '筋肉痛', '倦怠感'], icon: '🤒' },
    { id: 'gastro', name: '🤢 胃腸炎症状', symptoms: ['腹痛', '下痢', '吐き気', '嘔吐'], icon: '🤢' }
  ];

  // カテゴリー別にタグを分類
  const categorizedTags = symptomTags?.data?.reduce((acc, tag) => {
    const category = tag.category as SymptomCategory;
    if (!acc[category]) acc[category] = [];
    acc[category].push(tag);
    return acc;
  }, {} as Record<SymptomCategory, Tag[]>) || {} as Record<SymptomCategory, Tag[]>;

  const toggleCategory = (category: string) => {
    setCollapsedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleTagToggle = (tag: Tag) => {
    const isSelected = selectedTags.some(t => t.tag_id === tag.tag_id);
    if (isSelected) {
      removeSelectedTag(tag.tag_id);
    } else {
      addSelectedTag(tag);
    }
  };

  const applySymptomPreset = (preset: SymptomPreset) => {
    const presetTags = symptomTags?.data?.filter(tag => 
      preset.symptoms.includes(tag.tag_name)
    ) || [];
    setSelectedTags(presetTags);
  };

  const addNewMedicationCombination = () => {
    const newCombination = {
      id: `medication-${medicationCounter}`,
      drug_name: '',
      dosage: '',
      frequency: '',
      days: '',
      timing: '',
      instructions: ''
    };
    addMedicationCombination(newCombination);
    setMedicationCounter(prev => prev + 1);
  };

  const updateMedicationField = () => {
    const medicationText = medicationCombinations
      .map(combo => `${combo.drug_name} ${combo.dosage} ${combo.frequency} ${combo.days} ${combo.timing}`)
      .join('\n');
    updateFormField('medication', medicationText);
  };

  useEffect(() => {
    updateMedicationField();
  }, [medicationCombinations]);

  const confirmSymptoms = () => {
    const symptomTags = selectedTags.filter(t => t.category?.startsWith('症状'));
    const symptomNames = symptomTags.map(t => t.tag_name);
    const explanation = `「${symptomNames.join('」「')}」といった症状で受診していただきました。`;
    updateFormField('patient_explanation', explanation);
  };

  const confirmDiagnosis = () => {
    const diagnosis = formData.diagnosis;
    if (diagnosis) {
      const explanation = formData.patient_explanation + 
        `\n\n診断は「${diagnosis}」です。`;
      updateFormField('patient_explanation', explanation);
    }
  };

  const confirmMedication = () => {
    const medicationCount = medicationCombinations.length;
    if (medicationCount > 0) {
      const explanation = formData.patient_explanation + 
        `\n\n処方薬は${medicationCount}種類を${medicationCombinations[0]?.days || '数日'}分お出しします。`;
      updateFormField('patient_explanation', explanation);
    }
  };

  const handleSubmit = async () => {
    if (!currentPatient) {
      setError('患者が選択されていません');
      return;
    }

    setLoading(true);
    try {
      const now = new Date();
      const jstTime = new Date(now.getTime() + (9 * 60 * 60 * 1000));
      const jstISOString = jstTime.toISOString();

      const recordData = {
        patient_id: currentPatient.patient_id,
        date: jstISOString,
        chief_complaint: formData.symptoms,
        diagnosis: formData.diagnosis,
        treatment: formData.medication,
        notes: formData.patient_explanation,
        doctor_notes: formData.doctor_notes
      };

      const response = await api.submitMedicalRecord(recordData);
      if (response.success) {
        // 患者表示を開始
        await api.setPatientDisplay(recordData);
        
        // 3秒後にダッシュボードに戻る
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } else {
        setError(response.message || '診療記録の送信に失敗しました');
      }
    } catch (error) {
      setError('診療記録の送信に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  if (tagsLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>医療記録入力フォーム</h1>
        <Button variant="secondary" onClick={() => navigate('/dashboard')}>
          ダッシュボードに戻る
        </Button>
      </div>

      {currentPatient && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3>現在の患者: {currentPatient.name} ({currentPatient.name_kana})</h3>
        </div>
      )}

      <div className="three-column-layout">
        {/* 症状セクション */}
        <div className="form-section">
          <h2>症状</h2>
          
          {/* 症状プリセット */}
          <div className="form-group">
            <label>よく使う症状セット:</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
              {symptomPresets.map(preset => (
                <Button
                  key={preset.id}
                  variant="secondary"
                  onClick={() => applySymptomPreset(preset)}
                  style={{ fontSize: '12px' }}
                >
                  {preset.name}
                </Button>
              ))}
            </div>
          </div>

          {/* 症状タグ選択 */}
          <div className="form-group">
            <label>症状タグ選択:</label>
            {Object.entries(categorizedTags).map(([category, tags]) => (
              <TagSelector
                key={category}
                category={category as SymptomCategory}
                tags={tags}
                selectedTags={selectedTags}
                onTagToggle={handleTagToggle}
                isCollapsed={collapsedCategories[category]}
                onToggleCollapse={() => toggleCategory(category)}
              />
            ))}
          </div>

          {/* 選択中の症状タグ */}
          <div className="form-group">
            <label>選択中の症状:</label>
            <div className="tag-buttons">
              {selectedTags.filter(t => t.category?.startsWith('症状')).map(tag => (
                <button
                  key={tag.tag_id}
                  className="tag selected"
                  onClick={() => removeSelectedTag(tag.tag_id)}
                >
                  {tag.tag_name} ×
                </button>
              ))}
            </div>
            <Button
              variant="secondary"
              onClick={confirmSymptoms}
              style={{ marginTop: '10px' }}
            >
              ✓ 症状を確定して説明文に追加
            </Button>
          </div>

          {/* 症状の詳細入力 */}
          <div className="form-group">
            <label>症状の詳細</label>
            <small style={{ color: '#000', display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              💡 選択したタグをもとに、症状の詳細（いつから、程度、経過など）を記入してください。
            </small>
            <Input
              type="textarea"
              value={formData.symptoms}
              onChange={(value) => updateFormField('symptoms', value)}
              placeholder="例: 発熱（選択したタグ）→ 3日前から38.5度の発熱が続いている。解熱剤で一時的に下がるが再び上昇。"
            />
          </div>
        </div>

        {/* 診断・治療計画セクション */}
        <div className="form-section">
          <h2>診断・治療計画</h2>
          
          <div className="form-group">
            <label>診断名</label>
            <Input
              value={formData.diagnosis}
              onChange={(value) => updateFormField('diagnosis', value)}
              placeholder="例: 急性上気道感染症"
            />
            <Button
              variant="secondary"
              onClick={confirmDiagnosis}
              style={{ marginTop: '10px' }}
            >
              ✓ 診断を確定して説明文に追加
            </Button>
          </div>

          <div className="form-group">
            <label>診断の詳細</label>
            <Input
              type="textarea"
              value={formData.diagnosis_details}
              onChange={(value) => updateFormField('diagnosis_details', value)}
              placeholder="診断の根拠や詳細を記入してください"
            />
          </div>

          <div className="form-group">
            <label>治療計画</label>
            <Input
              type="textarea"
              value={formData.treatment_plan}
              onChange={(value) => updateFormField('treatment_plan', value)}
              placeholder="治療方針や今後の予定を記入してください"
            />
          </div>

          <div className="form-group">
            <label>フォローアップ</label>
            <Input
              type="textarea"
              value={formData.follow_up}
              onChange={(value) => updateFormField('follow_up', value)}
              placeholder="次回受診予定や注意事項を記入してください"
            />
          </div>
        </div>

        {/* 処方薬セクション */}
        <div className="form-section">
          <h2>処方薬</h2>
          
          <div className="form-group">
            <label>薬剤組み合わせ</label>
            <Button
              variant="primary"
              onClick={addNewMedicationCombination}
              style={{ marginBottom: '15px' }}
            >
              + 薬剤を追加
            </Button>
            
            <div id="medication-combination-area">
              {medicationCombinations.map(combination => (
                <MedicationCombination
                  key={combination.id}
                  combination={combination}
                  onRemove={removeMedicationCombination}
                  onUpdate={updateMedicationCombination}
                />
              ))}
            </div>
            
            <Button
              variant="secondary"
              onClick={confirmMedication}
              style={{ marginTop: '10px' }}
            >
              ✓ 処方薬を確定して説明文に追加
            </Button>
          </div>

          <div className="form-group">
            <label>処方薬・治療</label>
            <Input
              type="textarea"
              value={formData.medication}
              onChange={(value) => updateFormField('medication', value)}
              placeholder="処方薬の詳細を記入してください"
            />
          </div>

          <div className="form-group">
            <label>服薬指導・注意事項</label>
            <Input
              type="textarea"
              value={formData.medication_instructions}
              onChange={(value) => updateFormField('medication_instructions', value)}
              placeholder="服薬方法や注意事項を記入してください"
            />
          </div>
        </div>
      </div>

      {/* 患者向け説明文 */}
      <div className="card">
        <h2>患者向け説明文</h2>
        <div className="form-group">
          <label>説明文（患者に表示される内容）</label>
          <Input
            type="textarea"
            value={formData.patient_explanation}
            onChange={(value) => updateFormField('patient_explanation', value)}
            placeholder="患者さんに分かりやすく説明する内容を記入してください"
          />
        </div>

        <div className="form-group">
          <label>医師メモ（患者には表示されません）</label>
          <Input
            type="textarea"
            value={formData.doctor_notes}
            onChange={(value) => updateFormField('doctor_notes', value)}
            placeholder="内部記録用のメモを記入してください"
          />
        </div>
      </div>

      {/* 送信ボタン */}
      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <Button
          variant="success"
          onClick={handleSubmit}
          style={{ fontSize: '16px', padding: '12px 30px' }}
        >
          電子カルテに入力する
        </Button>
      </div>
    </div>
  );
};

export default InputFormPage;
