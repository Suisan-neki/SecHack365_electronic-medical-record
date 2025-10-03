import React from 'react';
import { MedicationCombination as MedicationCombinationType } from '../types';
import { useAppStore } from '../store/useAppStore';
import Button from './Button';
import Input from './Input';

interface MedicationCombinationProps {
  combination: MedicationCombinationType;
  onRemove: (id: string) => void;
  onUpdate: (id: string, updates: Partial<MedicationCombinationType>) => void;
}

const MedicationCombination: React.FC<MedicationCombinationProps> = ({
  combination,
  onRemove,
  onUpdate
}) => {
  const handleFieldChange = (field: keyof MedicationCombinationType, value: string) => {
    onUpdate(combination.id, { [field]: value });
  };

  return (
    <div className="medication-combination" style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      marginBottom: '15px',
      backgroundColor: '#f9f9f9'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h4 style={{ margin: 0, color: '#333' }}>薬剤 {combination.id.split('-')[1]}</h4>
        <Button 
          variant="danger" 
          size="small"
          onClick={() => onRemove(combination.id)}
        >
          削除
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
        <div className="form-group">
          <label>薬剤名</label>
          <Input
            value={combination.drug_name}
            onChange={(value) => handleFieldChange('drug_name', value)}
            placeholder="例: カロナール"
          />
        </div>

        <div className="form-group">
          <label>用量</label>
          <Input
            value={combination.dosage}
            onChange={(value) => handleFieldChange('dosage', value)}
            placeholder="例: 500mg"
          />
        </div>

        <div className="form-group">
          <label>頻度</label>
          <Input
            value={combination.frequency}
            onChange={(value) => handleFieldChange('frequency', value)}
            placeholder="例: 1日3回"
          />
        </div>

        <div className="form-group">
          <label>日数</label>
          <Input
            value={combination.days}
            onChange={(value) => handleFieldChange('days', value)}
            placeholder="例: 5日分"
          />
        </div>

        <div className="form-group">
          <label>タイミング</label>
          <Input
            value={combination.timing}
            onChange={(value) => handleFieldChange('timing', value)}
            placeholder="例: 食後"
          />
        </div>

        <div className="form-group">
          <label>服薬指導</label>
          <Input
            value={combination.instructions}
            onChange={(value) => handleFieldChange('instructions', value)}
            placeholder="例: 食後に水で服用"
          />
        </div>
      </div>

      <div className="form-group">
        <label>プレビュー</label>
        <div style={{
          padding: '10px',
          backgroundColor: '#e8f5e9',
          borderRadius: '4px',
          fontSize: '14px',
          color: '#2c3e50'
        }}>
          {combination.drug_name} {combination.dosage} {combination.frequency} {combination.days} {combination.timing}
          {combination.instructions && ` (${combination.instructions})`}
        </div>
      </div>
    </div>
  );
};

export default MedicationCombination;
