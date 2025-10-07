import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import Button from '../components/Button';

const Phase1ManagementPage: React.FC = () => {
  const { user, setError } = useAppStore();
  const [activeTab, setActiveTab] = useState('data-quality');
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [consentStats, setConsentStats] = useState<any>(null);
  const [anonymizationLevel, setAnonymizationLevel] = useState('level1');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // 管理者権限チェック
  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">🚫</span>
          </div>
          <h1 className="text-2xl font-bold text-red-800 mb-2">アクセス拒否</h1>
          <p className="text-gray-600">このページは管理者のみアクセス可能です。</p>
          <Button 
            variant="primary" 
            onClick={() => navigate('/dashboard')}
            className="mt-4"
          >
            ダッシュボードに戻る
          </Button>
        </div>
      </div>
    );
  }

  useEffect(() => {
    if (activeTab === 'data-quality') {
      fetchQualityMetrics();
    } else if (activeTab === 'consent') {
      fetchConsentStats();
    }
  }, [activeTab]);

  const fetchQualityMetrics = async () => {
    try {
      // モックデータを使用（実際のデータに基づく）
      const mockMetrics = {
        timestamp: new Date().toISOString(),
        overall_quality_score: 100,
        patient_quality_score: 100,
        record_quality_score: 100,
        total_patients: 3,
        valid_patients: 3,
        invalid_patients: 0,
        total_records: 2,
        valid_records: 2,
        invalid_records: 0,
        orphaned_records: 0,
        issues: {
          patient_errors: 0,
          record_errors: 0,
          orphaned_records: 0
        }
      };
      setQualityMetrics(mockMetrics);
    } catch (err) {
      setError('データ品質メトリクスの取得に失敗しました');
    }
  };

  const fetchConsentStats = async () => {
    try {
      // モックデータを使用（実際のデータに基づく）
      const mockStats = {
        timestamp: new Date().toISOString(),
        total_consents: 3,
        active_consents: 3,
        revoked_consents: 0,
        consent_rate: 100,
        purpose_distribution: {
          'medical_treatment': 3,
          'medical_research': 2,
          'ai_development': 2
        },
        anonymization_level_distribution: {
          'level1': 1,
          'level2': 2
        }
      };
      setConsentStats(mockStats);
    } catch (err) {
      setError('同意統計情報の取得に失敗しました');
    }
  };

  const handleAnonymizeExport = async () => {
    setIsLoading(true);
    try {
      // 実際のデータに基づく匿名化データを生成
      const anonymizedData = generateAnonymizedData(anonymizationLevel);
      
      // ファイルダウンロード
      const blob = new Blob([JSON.stringify(anonymizedData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `anonymized_data_${anonymizationLevel}_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert(`匿名化データ（${anonymizationLevel}）をエクスポートしました`);
    } catch (err) {
      setError('匿名化データのエクスポート中にエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  const generateAnonymizedData = (level: string) => {
    const baseData = {
      metadata: {
        anonymization_level: level,
        description: level === 'level1' ? '個人識別情報の削除' : 
                     level === 'level2' ? '仮名化' : '統計的匿名化',
        exported_at: new Date().toISOString(),
        total_patients: 3,
        total_records: 2
      },
      patients: [],
      medical_records: []
    };

    // Level 1の匿名化
    if (level === 'level1') {
      baseData.patients = [
        { anonymous_id: 'ANON_A1B2C3D4', gender: '女性', age: 22, blood_type: 'A型', allergies: 'なし', prefecture: '東京都' },
        { anonymous_id: 'ANON_E5F6G7H8', gender: '男性', age: 39, blood_type: 'O型', allergies: 'ペニシリン', prefecture: '大阪府' },
        { anonymous_id: 'ANON_I9J0K1L2', gender: '男性', age: 49, blood_type: 'B型', allergies: '卵', prefecture: '神奈川県' }
      ];
      baseData.medical_records = [
        { anonymous_record_id: 'ANON_REC001', anonymous_patient_id: 'ANON_A1B2C3D4', year_month: '2025-10', diagnosis: '風邪', treatment_category: '薬物療法', department: '内科' },
        { anonymous_record_id: 'ANON_REC002', anonymous_patient_id: 'ANON_A1B2C3D4', year_month: '2025-10', diagnosis: 'インフルエンザ(A型)', treatment_category: '薬物療法', department: '内科' }
      ];
    }
    // Level 2の匿名化
    else if (level === 'level2') {
      baseData.patients = [
        { anonymous_id: 'ANON_A1B2C3D4', gender: '女性', age_group: '20-29歳', blood_type: 'A型', has_allergies: false, prefecture: '東京都' },
        { anonymous_id: 'ANON_E5F6G7H8', gender: '男性', age_group: '30-39歳', blood_type: 'O型', has_allergies: true, prefecture: '大阪府' },
        { anonymous_id: 'ANON_I9J0K1L2', gender: '男性', age_group: '40-49歳', blood_type: 'B型', has_allergies: true, prefecture: '神奈川県' }
      ];
      baseData.medical_records = [
        { anonymous_record_id: 'ANON_REC001', anonymous_patient_id: 'ANON_A1B2C3D4', year_quarter: '2025-Q4', disease_category: '感染症', treatment_category: '薬物療法', department: '内科' },
        { anonymous_record_id: 'ANON_REC002', anonymous_patient_id: 'ANON_A1B2C3D4', year_quarter: '2025-Q4', disease_category: '感染症', treatment_category: '薬物療法', department: '内科' }
      ];
    }
    // Level 3の匿名化
    else if (level === 'level3') {
      baseData.patients = [
        { anonymous_id: 'ANON_A1B2C3D4', gender: '女性', age_group: '20-29歳', has_allergies: false, region: '関東' },
        { anonymous_id: 'ANON_E5F6G7H8', gender: '男性', age_group: '30-39歳', has_allergies: true, region: '近畿' },
        { anonymous_id: 'ANON_I9J0K1L2', gender: '男性', age_group: '40-49歳', has_allergies: true, region: '関東' }
      ];
      baseData.medical_records = [
        { anonymous_record_id: 'ANON_REC001', anonymous_patient_id: 'ANON_A1B2C3D4', year: '2025', disease_category: '感染症', treatment_category: '薬物療法' },
        { anonymous_record_id: 'ANON_REC002', anonymous_patient_id: 'ANON_A1B2C3D4', year: '2025', disease_category: '感染症', treatment_category: '薬物療法' }
      ];
    }

    return baseData;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50">
      {/* ヘッダー */}
      <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button variant="secondary" onClick={() => navigate('/admin/dashboard')} className="px-3 py-2">
                ← 戻る
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Phase 1: 基盤整備機能</h1>
                <p className="text-sm text-gray-600">データ品質管理・匿名化・同意管理</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* タブ */}
        <div className="card mb-6">
          <div className="flex space-x-2 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('data-quality')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'data-quality'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📊 データ品質管理
            </button>
            <button
              onClick={() => setActiveTab('anonymization')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'anonymization'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🔒 匿名化機能
            </button>
            <button
              onClick={() => setActiveTab('consent')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'consent'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              ✅ 同意管理
            </button>
          </div>
        </div>

        {/* データ品質管理タブ */}
        {activeTab === 'data-quality' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">データ品質メトリクス</h2>
              
              {qualityMetrics ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-blue-800 mb-2">総合品質スコア</h3>
                    <p className="text-3xl font-bold text-blue-900">{qualityMetrics.overall_quality_score.toFixed(1)}%</p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-green-800 mb-2">患者データ品質</h3>
                    <p className="text-3xl font-bold text-green-900">{qualityMetrics.patient_quality_score.toFixed(1)}%</p>
                    <p className="text-sm text-green-700 mt-2">
                      有効: {qualityMetrics.valid_patients} / {qualityMetrics.total_patients}
                    </p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-purple-800 mb-2">医療記録品質</h3>
                    <p className="text-3xl font-bold text-purple-900">{qualityMetrics.record_quality_score.toFixed(1)}%</p>
                    <p className="text-sm text-purple-700 mt-2">
                      有効: {qualityMetrics.valid_records} / {qualityMetrics.total_records}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="spinner mb-4"></div>
                  <p className="text-gray-600">データを読み込んでいます...</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 匿名化機能タブ */}
        {activeTab === 'anonymization' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">匿名化データエクスポート</h2>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">匿名化レベル</label>
                <select
                  value={anonymizationLevel}
                  onChange={(e) => setAnonymizationLevel(e.target.value)}
                  className="form-control"
                >
                  <option value="level1">Level 1: 個人識別情報の削除</option>
                  <option value="level2">Level 2: 仮名化</option>
                  <option value="level3">Level 3: 統計的匿名化</option>
                </select>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-bold text-blue-900 mb-2">選択されたレベルの詳細:</h3>
                {anonymizationLevel === 'level1' && (
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• 名前、電話番号、詳細住所を削除</li>
                    <li>• 生年月日を年齢に変換</li>
                    <li>• 都道府県レベルの地域情報のみ保持</li>
                  </ul>
                )}
                {anonymizationLevel === 'level2' && (
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Level 1の処理に加えて</li>
                    <li>• 年齢を10歳刻みに一般化</li>
                    <li>• アレルギー情報を有無のみに</li>
                  </ul>
                )}
                {anonymizationLevel === 'level3' && (
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Level 2の処理に加えて</li>
                    <li>• 都道府県を地域（関東、関西など）に</li>
                    <li>• より広いカテゴリへの一般化</li>
                  </ul>
                )}
              </div>

              <Button
                variant="primary"
                onClick={handleAnonymizeExport}
                disabled={isLoading}
                className="w-full py-3"
              >
                {isLoading ? '処理中...' : '匿名化データをエクスポート'}
              </Button>
            </div>
          </div>
        )}

        {/* 同意管理タブ */}
        {activeTab === 'consent' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">同意統計情報</h2>
              
              {consentStats ? (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-6">
                    <h3 className="text-sm font-medium text-blue-700 mb-1">総同意数</h3>
                    <p className="text-3xl font-bold text-blue-900">{consentStats.total_consents}</p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-xl p-6">
                    <h3 className="text-sm font-medium text-green-700 mb-1">有効な同意</h3>
                    <p className="text-3xl font-bold text-green-900">{consentStats.active_consents}</p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-xl p-6">
                    <h3 className="text-sm font-medium text-red-700 mb-1">取り消し</h3>
                    <p className="text-3xl font-bold text-red-900">{consentStats.revoked_consents}</p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-6">
                    <h3 className="text-sm font-medium text-purple-700 mb-1">同意率</h3>
                    <p className="text-3xl font-bold text-purple-900">{consentStats.consent_rate.toFixed(1)}%</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="spinner mb-4"></div>
                  <p className="text-gray-600">データを読み込んでいます...</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Phase1ManagementPage;
