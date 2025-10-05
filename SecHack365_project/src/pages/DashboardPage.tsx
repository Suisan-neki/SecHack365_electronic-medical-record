import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">🏥</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">ダッシュボード</h1>
                  <p className="text-sm text-gray-600">患者情報共有システム</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-gray-700 font-medium">こんにちは、{user?.username}さん</span>
              </div>
              
              {user?.role === 'admin' && (
                <Link
                  to="/admin"
                  className="inline-flex items-center px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <span className="mr-2">👨‍💼</span>
                  管理者画面
                </Link>
              )}
              
              <Button variant="secondary" onClick={handleLogout} className="px-4 py-2">
                ログアウト
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* 患者情報管理 */}
        <div className="card mb-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-medical-100 rounded-lg flex items-center justify-center">
              <span className="text-medical-600">👥</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900">患者情報管理</h2>
          </div>
          
          {currentPatient ? (
            <div className="bg-medical-50 border border-medical-200 rounded-lg p-6 mb-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-medical-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">👤</span>
                </div>
                <h3 className="text-lg font-semibold text-medical-800">現在の患者</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">名前:</span> {currentPatient.name} ({currentPatient.name_kana})
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">生年月日:</span> {currentPatient.birth_date}
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">性別:</span> {currentPatient.gender}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">患者ID:</span> {currentPatient.patient_id}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6 text-center">
              <div className="flex items-center justify-center space-x-2 text-yellow-800">
                <span className="text-lg">⚠️</span>
                <p className="font-medium">患者が選択されていません</p>
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-4">
            <Button
              variant="primary"
              onClick={handleExtractPatientData}
              className="flex-1 min-w-48 py-3 text-base font-medium"
            >
              <span className="mr-2">📋</span>
              患者情報を抽出
            </Button>
            
            <Button
              variant="success"
              onClick={handleInputMedicalRecord}
              disabled={!currentPatient}
              className="flex-1 min-w-48 py-3 text-base font-medium"
            >
              <span className="mr-2">📝</span>
              医療記録を入力
            </Button>
          </div>
        </div>

        {/* システム情報 */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <span className="text-primary-600">⚙️</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900">システム情報</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <span className="text-lg">🔒</span>
                <h3 className="text-lg font-semibold text-gray-900">セキュリティ機能</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>RSA 2048bit デジタル署名</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>AES-256-GCM 暗号化</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>WebAuthn (FIDO2) 認証</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>監査ログ</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <span className="text-lg">🔗</span>
                <h3 className="text-lg font-semibold text-gray-900">連携機能</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>FHIR 標準対応</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>CSV インポート/エクスポート</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>模擬電子カルテ連携</span>
                </li>
                <li className="flex items-center space-x-2 text-gray-700">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>リアルタイム患者表示</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
