import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { getDiagnosisExplanation } from '../data/diagnosisExplanations';
import { extractMedicationsFromTreatment } from '../data/medicationInfo';
import Button from '../components/Button';

const PatientDisplayPage: React.FC = () => {
  const [medicalRecord, setMedicalRecord] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMedication, setSelectedMedication] = useState<number | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { setError, currentPatient } = useAppStore();

  useEffect(() => {
    fetchLatestMedicalRecord();
    
    // リアルタイム更新のためのポーリング
    const interval = setInterval(() => fetchLatestMedicalRecord(true), 2000); // 2秒ごとに更新
    
    return () => clearInterval(interval);
  }, [currentPatient]);

  const fetchLatestMedicalRecord = async (isPolling = false) => {
    if (!currentPatient) {
      setIsLoading(false);
      return;
    }

    if (isPolling) {
      setIsUpdating(true);
    }

    try {
      const response = await fetch(`http://localhost:5002/api/medical_records/${currentPatient.patient_id}`);
      if (response.ok) {
        const records = await response.json();
        if (records && records.length > 0) {
          const latestRecord = records[records.length - 1];
          setMedicalRecord(latestRecord);
          setLastUpdated(new Date());
        }
      }
    } catch (err) {
      if (!isPolling) {
        setError('医療記録の取得に失敗しました');
      }
    } finally {
      setIsLoading(false);
      if (isPolling) {
        setIsUpdating(false);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!medicalRecord) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50 flex items-center justify-center">
        <div className="card max-w-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">診療記録がありません</h2>
          <p className="text-gray-600">まだ診療記録が作成されていません。</p>
        </div>
      </div>
    );
  }

  const diagnosisInfo = getDiagnosisExplanation(medicalRecord.diagnosis);
  const medications = extractMedicationsFromTreatment(medicalRecord.treatment || '');

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50">
      {/* ヘッダー */}
      <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-medical-500 to-medical-600 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white text-2xl">👤</span>
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">診療内容のご確認</h1>
            <p className="text-gray-600">{currentPatient?.name} 様</p>
            <p className="text-sm text-gray-500">診療日: {new Date(medicalRecord.date).toLocaleDateString('ja-JP')}</p>
            <div className="flex justify-center items-center mt-2 space-x-2">
              {isUpdating && (
                <div className="flex items-center text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  <span className="text-sm">更新中...</span>
                </div>
              )}
              {lastUpdated && (
                <p className="text-xs text-gray-400">
                  最終更新: {lastUpdated.toLocaleTimeString('ja-JP')}
                </p>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* タブナビゲーション */}
        <div className="card mb-6">
          <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
                activeTab === 'overview'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📋 概要
            </button>
            <button
              onClick={() => setActiveTab('diagnosis')}
              className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
                activeTab === 'diagnosis'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🔍 病気について
            </button>
            <button
              onClick={() => setActiveTab('medication')}
              className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
                activeTab === 'medication'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              💊 お薬について
            </button>
            <button
              onClick={() => setActiveTab('lifestyle')}
              className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
                activeTab === 'lifestyle'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🏠 生活上の注意
            </button>
            <button
              onClick={() => setActiveTab('faq')}
              className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
                activeTab === 'faq'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              ❓ よくある質問
            </button>
          </div>
        </div>

        {/* 概要タブ */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">診療内容</h2>
              
              <div className={`bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 transition-all duration-500 ${
                medicalRecord.diagnosis ? 'animate-pulse' : ''
              }`}>
                <h3 className="text-lg font-bold text-blue-900 mb-2">診断名</h3>
                <p className="text-2xl font-bold text-blue-800">
                  {medicalRecord.diagnosis || (
                    <span className="text-gray-400 italic">診断名を入力中...</span>
                  )}
                </p>
              </div>

              <div className={`bg-green-50 border border-green-200 rounded-lg p-6 mb-6 transition-all duration-500 ${
                medicalRecord.treatment ? 'animate-pulse' : ''
              }`}>
                <h3 className="text-lg font-bold text-green-900 mb-2">処方されたお薬</h3>
                <p className="text-gray-800 whitespace-pre-line">
                  {medicalRecord.treatment || (
                    <span className="text-gray-400 italic">処方薬を入力中...</span>
                  )}
                </p>
              </div>

              <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 transition-all duration-500 ${
                medicalRecord.notes ? 'animate-pulse' : ''
              }`}>
                <h3 className="text-lg font-bold text-gray-900 mb-2">医師からの説明</h3>
                <p className="text-gray-800 whitespace-pre-line leading-relaxed">
                  {medicalRecord.notes || (
                    <span className="text-gray-400 italic">説明を入力中...</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 病気についてタブ */}
        {activeTab === 'diagnosis' && diagnosisInfo && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                {diagnosisInfo.patientFriendlyName} について
              </h2>
              
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-bold text-blue-900 mb-3">📘 分かりやすい説明</h3>
                <p className="text-gray-800 leading-relaxed mb-4">{diagnosisInfo.simpleExplanation}</p>
                <p className="text-gray-700 leading-relaxed">{diagnosisInfo.detailedExplanation}</p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-bold text-yellow-900 mb-3">🤒 よくある症状</h3>
                <ul className="space-y-2">
                  {diagnosisInfo.commonSymptoms.map((symptom, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-yellow-600 mr-2">•</span>
                      <span className="text-gray-800">{symptom}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-bold text-green-900 mb-3">🏥 治療の流れ</h3>
                <ol className="space-y-3">
                  {diagnosisInfo.treatmentFlow.map((step, index) => (
                    <li key={index} className="flex items-start">
                      <span className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center mr-3 text-sm font-bold">
                        {index + 1}
                      </span>
                      <span className="text-gray-800 pt-1">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
                <h3 className="text-lg font-bold text-purple-900 mb-3">📅 予想される経過</h3>
                <p className="text-gray-800 leading-relaxed">{diagnosisInfo.expectedCourse}</p>
              </div>
            </div>
          </div>
        )}

        {/* お薬についてタブ */}
        {activeTab === 'medication' && (
          <div className="space-y-6">
            {medications.length > 0 ? (
              medications.map((med, index) => (
                <div key={index} className="card">
                  <div className="bg-gradient-to-r from-medical-500 to-medical-600 text-white p-6 rounded-t-xl -m-8 mb-6">
                    <h2 className="text-2xl font-bold mb-2">{med.medicationName}</h2>
                    {med.genericName && (
                      <p className="text-medical-100">（一般名: {med.genericName}）</p>
                    )}
                    <p className="text-medical-100 mt-2">{med.category}</p>
                  </div>

                  <div className="space-y-6">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="font-bold text-blue-900 mb-2">💊 この薬の効果</h3>
                      <p className="text-gray-800 mb-2">{med.effect}</p>
                      <p className="text-sm text-gray-700">{med.detailedEffect}</p>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h3 className="font-bold text-green-900 mb-2">📅 飲み方</h3>
                      <p className="text-gray-800 mb-2"><strong>用量:</strong> {med.dosage}</p>
                      <p className="text-gray-800">{med.whenToTake}</p>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h3 className="font-bold text-yellow-900 mb-2">⚠️ 副作用</h3>
                      <ul className="space-y-1">
                        {med.sideEffects.map((effect, i) => (
                          <li key={i} className="text-gray-800">• {effect}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h3 className="font-bold text-red-900 mb-2">🚫 注意事項</h3>
                      <ul className="space-y-1">
                        {med.precautions.map((precaution, i) => (
                          <li key={i} className="text-gray-800">• {precaution}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <h3 className="font-bold text-purple-900 mb-2">❓ 飲み忘れた時は？</h3>
                      <p className="text-gray-800">{med.missedDose}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="card">
                <p className="text-gray-600">処方された薬の詳細情報はありません。</p>
              </div>
            )}
          </div>
        )}

        {/* 生活上の注意タブ */}
        {activeTab === 'lifestyle' && diagnosisInfo && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">生活上の注意</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-green-900 mb-4">🍽️ 食事</h3>
                  <ul className="space-y-2">
                    {diagnosisInfo.lifestyle.food.map((item, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-green-600 mr-2">✓</span>
                        <span className="text-gray-800">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-blue-900 mb-4">🏃 運動</h3>
                  <ul className="space-y-2">
                    {diagnosisInfo.lifestyle.exercise.map((item, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2">✓</span>
                        <span className="text-gray-800">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-red-900 mb-4">🚫 避けるべきこと</h3>
                  <ul className="space-y-2">
                    {diagnosisInfo.lifestyle.avoid.map((item, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-red-600 mr-2">✗</span>
                        <span className="text-gray-800">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-purple-900 mb-4">🏠 日常生活</h3>
                  <ul className="space-y-2">
                    {diagnosisInfo.lifestyle.dailyLife.map((item, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-purple-600 mr-2">•</span>
                        <span className="text-gray-800">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* よくある質問タブ */}
        {activeTab === 'faq' && diagnosisInfo && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">よくある質問</h2>

              <div className="space-y-4">
                {diagnosisInfo.faq.map((qa, index) => (
                  <div key={index} className="bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-6">
                    <div className="flex items-start mb-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-full flex items-center justify-center mr-4">
                        <span className="text-white font-bold">Q</span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 pt-1">{qa.question}</h3>
                    </div>
                    <div className="flex items-start ml-14">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-medical-500 to-medical-600 rounded-full flex items-center justify-center mr-4">
                        <span className="text-white font-bold">A</span>
                      </div>
                      <p className="text-gray-800 leading-relaxed pt-2">{qa.answer}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <div className="flex items-start">
                  <span className="text-3xl mr-4">💡</span>
                  <div>
                    <h3 className="font-bold text-yellow-900 mb-2">その他のご質問がある場合</h3>
                    <p className="text-gray-800">
                      ここに記載されていない質問や心配なことがありましたら、遠慮なく医療機関にお問い合わせください。
                      些細なことでも構いません。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 確認ボタン */}
        <div className="mt-8 text-center">
          <Button
            variant="success"
            onClick={() => {
              alert('内容をご確認いただき、ありがとうございます。\nお大事になさってください。');
              window.close();
            }}
            className="px-8 py-4 text-lg"
          >
            内容を確認しました
          </Button>
        </div>
      </main>
    </div>
  );
};

export default PatientDisplayPage;