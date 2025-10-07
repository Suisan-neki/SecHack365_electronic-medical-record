import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import Button from '../components/Button';

const DashboardPage: React.FC = () => {
  const { currentPatient, setError, user } = useAppStore();
  const navigate = useNavigate();

  // ログインしていない場合はログインページにリダイレクト
  if (!user) {
    navigate('/login');
    return null;
  }

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
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50">
      {/* ヘッダー */}
      <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-medical">
                  <span className="text-white text-xl">🏥</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">医療ダッシュボード</h1>
                  <p className="text-sm text-gray-600">患者情報共有システム</p>
                </div>
              </div>
            </div>
            
                 <div className="flex items-center space-x-4">
                   <div className="flex items-center space-x-3">
                     <div className="w-10 h-10 bg-gradient-to-br from-medical-500 to-medical-600 rounded-full flex items-center justify-center shadow-sm">
                       <span className="text-sm font-bold text-white">
                         {user?.username?.charAt(0).toUpperCase()}
                       </span>
                     </div>
                     <div className="hidden sm:block">
                       <p className="text-sm font-medium text-gray-900">こんにちは、{user?.name || user?.username}さん</p>
                       <p className="text-xs text-gray-500">
                         {user?.role === 'admin' ? '管理者' : 
                          user?.role === 'doctor' ? '医師' : 
                          user?.role === 'nurse' ? '看護師' : 'ユーザー'}
                       </p>
                     </div>
                   </div>
                   
                   {user?.role === 'admin' && (
                     <Link to="/admin/dashboard">
                       <Button variant="secondary" className="px-4 py-2 text-sm">
                         管理者画面
                       </Button>
                     </Link>
                   )}
                   
                   <Button variant="secondary" onClick={handleLogout} className="px-4 py-2 text-sm">
                     ログアウト
                   </Button>
                 </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 患者情報管理 */}
        <div className="card animate-fade-in">
          <div className="flex items-center space-x-4 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-medical-100 to-medical-200 rounded-xl flex items-center justify-center">
              <span className="text-medical-600 text-xl">👥</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">患者情報管理</h2>
              <p className="text-sm text-gray-600">患者の選択と医療記録の入力を行います</p>
            </div>
          </div>
          
          {currentPatient ? (
            <div className="bg-gradient-to-r from-medical-50 to-medical-100 border border-medical-200 rounded-xl p-6 mb-8 shadow-medical">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-14 h-14 bg-gradient-to-br from-medical-600 to-medical-700 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white text-lg">👤</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-medical-800">現在の患者</h3>
                  <p className="text-sm text-medical-600">医療記録の入力が可能です</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white/70 rounded-lg p-4 border border-medical-200">
                  <p className="text-xs font-medium text-medical-700 mb-1">患者名</p>
                  <p className="text-lg font-bold text-gray-900">{currentPatient.name}</p>
                  <p className="text-sm text-gray-600">({currentPatient.name_kana})</p>
                </div>
                <div className="bg-white/70 rounded-lg p-4 border border-medical-200">
                  <p className="text-xs font-medium text-medical-700 mb-1">生年月日</p>
                  <p className="text-lg font-bold text-gray-900">{currentPatient.birth_date}</p>
                </div>
                <div className="bg-white/70 rounded-lg p-4 border border-medical-200">
                  <p className="text-xs font-medium text-medical-700 mb-1">性別</p>
                  <p className="text-lg font-bold text-gray-900">{currentPatient.gender}</p>
                </div>
                <div className="bg-white/70 rounded-lg p-4 border border-medical-200">
                  <p className="text-xs font-medium text-medical-700 mb-1">患者ID</p>
                  <p className="text-lg font-bold text-gray-900">{currentPatient.patient_id}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-8 mb-8 text-center shadow-soft">
              <div className="flex flex-col items-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full flex items-center justify-center">
                  <span className="text-white text-2xl">⚠️</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-yellow-800 mb-2">患者が選択されていません</h3>
                  <p className="text-sm text-yellow-700">まず患者情報を抽出してください</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Button
              variant="primary"
              onClick={handleExtractPatientData}
              className="w-full py-4 text-base font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
            >
              <span className="mr-3 text-lg">📋</span>
              患者情報を抽出
            </Button>
            
            <Button
              variant="success"
              onClick={handleInputMedicalRecord}
              disabled={!currentPatient}
              className="w-full py-4 text-base font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 disabled:transform-none disabled:shadow-lg"
            >
              <span className="mr-3 text-lg">📝</span>
              医療記録を入力
            </Button>
          </div>
        </div>

      </main>
    </div>
  );
};

export default DashboardPage;
