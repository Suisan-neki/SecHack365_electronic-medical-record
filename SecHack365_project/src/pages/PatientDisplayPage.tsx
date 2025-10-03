import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { api } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const PatientDisplayPage: React.FC = () => {
  const [patientData, setPatientData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { setError } = useAppStore();

  useEffect(() => {
    // 患者表示データを取得
    const fetchPatientData = async () => {
      try {
        // 実際のAPIエンドポイントに合わせて調整
        const response = await fetch('/api/get-patient-display');
        if (response.ok) {
          const data = await response.json();
          setPatientData(data);
        }
      } catch (error) {
        setError('患者データの取得に失敗しました');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPatientData();
  }, [setError]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!patientData) {
    return (
      <div className="container">
        <div className="card">
          <h2>患者表示</h2>
          <p>表示するデータがありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          診療内容のご確認
        </h1>
        
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h2>患者情報</h2>
          <p><strong>お名前:</strong> {patientData.patient_name || '情報なし'}</p>
          <p><strong>診療日:</strong> {new Date().toLocaleDateString('ja-JP')}</p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h2>症状</h2>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#fff3cd', 
            borderRadius: '4px',
            whiteSpace: 'pre-line'
          }}>
            {patientData.chief_complaint || '記載なし'}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h2>診断</h2>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#d1ecf1', 
            borderRadius: '4px',
            whiteSpace: 'pre-line'
          }}>
            {patientData.diagnosis || '記載なし'}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h2>処方薬</h2>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#d4edda', 
            borderRadius: '4px',
            whiteSpace: 'pre-line'
          }}>
            {patientData.treatment || '記載なし'}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h2>医師からの説明</h2>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e2e3e5', 
            borderRadius: '4px',
            whiteSpace: 'pre-line',
            lineHeight: '1.6'
          }}>
            {patientData.notes || '記載なし'}
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button 
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              padding: '12px 30px',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: 'pointer'
            }}
            onClick={() => {
              alert('内容を確認いただき、ありがとうございます。');
            }}
          >
            内容を確認しました
          </button>
        </div>
      </div>
    </div>
  );
};

export default PatientDisplayPage;
