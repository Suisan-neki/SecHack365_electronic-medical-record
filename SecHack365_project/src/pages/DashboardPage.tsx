import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import Button from '../components/Button';

const DashboardPage: React.FC = () => {
  const { user, currentPatient, setError } = useAppStore();
  const navigate = useNavigate();

  const handleExtractPatientData = () => {
    // グローバル関数を呼び出して患者選択モーダルを表示
    if ((window as any).showPatientSelectionModal) {
      (window as any).showPatientSelectionModal();
    } else {
      setError('患者選択機能が利用できません');
    }
  };

  const handleInputMedicalRecord = () => {
    if (!currentPatient) {
      setError('まず患者を選択してください');
      return;
    }
    navigate('/input-form');
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>ダッシュボード</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span>こんにちは、{user?.username}さん</span>
          <Button variant="secondary" onClick={handleLogout}>
            ログアウト
          </Button>
        </div>
      </div>

      <div className="card">
        <h2>患者情報管理</h2>
        {currentPatient ? (
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e8f5e9', 
            borderRadius: '4px', 
            marginBottom: '20px' 
          }}>
            <h3>現在の患者</h3>
            <p><strong>名前:</strong> {currentPatient.name} ({currentPatient.name_kana})</p>
            <p><strong>生年月日:</strong> {currentPatient.birth_date}</p>
            <p><strong>性別:</strong> {currentPatient.gender}</p>
            <p><strong>患者ID:</strong> {currentPatient.patient_id}</p>
          </div>
        ) : (
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#fff3cd', 
            borderRadius: '4px', 
            marginBottom: '20px' 
          }}>
            <p>患者が選択されていません</p>
          </div>
        )}

        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          <Button
            variant="primary"
            onClick={handleExtractPatientData}
            style={{ minWidth: '200px' }}
          >
            📋 患者情報を抽出
          </Button>
          
          <Button
            variant="success"
            onClick={handleInputMedicalRecord}
            disabled={!currentPatient}
            style={{ minWidth: '200px' }}
          >
            📝 医療記録を入力
          </Button>
        </div>
      </div>

      <div className="card">
        <h2>システム情報</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <h3>セキュリティ機能</h3>
            <ul>
              <li>RSA 2048bit デジタル署名</li>
              <li>AES-256-GCM 暗号化</li>
              <li>WebAuthn (FIDO2) 認証</li>
              <li>監査ログ</li>
            </ul>
          </div>
          
          <div>
            <h3>連携機能</h3>
            <ul>
              <li>FHIR 標準対応</li>
              <li>CSV インポート/エクスポート</li>
              <li>模擬電子カルテ連携</li>
              <li>リアルタイム患者表示</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
