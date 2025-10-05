import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';

interface SecurityLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  status: 'success' | 'failed';
  ipAddress: string;
}

interface WebAuthnCredential {
  username: string;
  id: string;
  counter: number;
  deviceType: string;
  lastUsed: string;
}

const AdminSecurityPage: React.FC = () => {
  const { user } = useAppStore();
  const [securityLogs, setSecurityLogs] = useState<SecurityLog[]>([]);
  const [webauthnCredentials, setWebauthnCredentials] = useState<WebAuthnCredential[]>([]);
  const [selectedTab, setSelectedTab] = useState<'logs' | 'credentials' | 'settings'>('logs');

  // 管理者権限チェック
  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">アクセス拒否</h2>
            <p className="text-gray-600">このページは管理者のみアクセス可能です。</p>
          </div>
        </div>
      </div>
    );
  }

  useEffect(() => {
    // セキュリティログの取得
    const fetchSecurityLogs = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/admin/security-logs');
        if (response.ok) {
          const logs = await response.json();
          setSecurityLogs(logs);
        }
      } catch (error) {
        console.error('セキュリティログの取得に失敗:', error);
        // モックデータ
        setSecurityLogs([
          {
            id: '1',
            timestamp: '2024-10-04T14:04:38Z',
            user: 'doctor1',
            action: 'WebAuthn認証成功',
            status: 'success',
            ipAddress: '127.0.0.1'
          },
          {
            id: '2',
            timestamp: '2024-10-04T14:03:27Z',
            user: 'doctor1',
            action: 'WebAuthn登録完了',
            status: 'success',
            ipAddress: '127.0.0.1'
          }
        ]);
      }
    };

    // WebAuthn認証情報の取得
    const fetchWebAuthnCredentials = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/admin/webauthn-credentials');
        if (response.ok) {
          const credentials = await response.json();
          setWebauthnCredentials(credentials);
        }
      } catch (error) {
        console.error('WebAuthn認証情報の取得に失敗:', error);
        // モックデータ
        setWebauthnCredentials([
          {
            username: 'doctor1',
            id: 'aD_JYodFJ8-i40rDlSZVch1dfM9em5j80H3WIGfZlso',
            counter: 1,
            deviceType: 'platform',
            lastUsed: '2024-10-04T14:04:38Z'
          }
        ]);
      }
    };

    fetchSecurityLogs();
    fetchWebAuthnCredentials();
  }, []);

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ja-JP');
  };

  const getStatusColor = (status: string) => {
    return status === 'success' ? 'text-green-600' : 'text-red-600';
  };

  const getStatusBadge = (status: string) => {
    return status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* ヘッダー */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">セキュリティ管理</h1>
              <p className="mt-1 text-sm text-gray-500">
                WebAuthn認証・アクセス監査・セキュリティ設定
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.history.back()}
                className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm hover:bg-gray-700"
              >
                戻る
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* タブナビゲーション */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setSelectedTab('logs')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'logs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              セキュリティログ
            </button>
            <button
              onClick={() => setSelectedTab('credentials')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'credentials'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              WebAuthn認証情報
            </button>
            <button
              onClick={() => setSelectedTab('settings')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === 'settings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              セキュリティ設定
            </button>
          </nav>
        </div>

        {/* タブコンテンツ */}
        {selectedTab === 'logs' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                セキュリティログ
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        時刻
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ユーザー
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        アクション
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ステータス
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IPアドレス
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {securityLogs.map((log) => (
                      <tr key={log.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatTimestamp(log.timestamp)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.user}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.action}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(log.status)}`}>
                            {log.status === 'success' ? '成功' : '失敗'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.ipAddress}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'credentials' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                WebAuthn認証情報
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ユーザー名
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        認証情報ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        デバイスタイプ
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        カウンター
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        最終使用
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {webauthnCredentials.map((cred, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {cred.username}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 font-mono">
                          {cred.id.substring(0, 20)}...
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {cred.deviceType}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {cred.counter}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatTimestamp(cred.lastUsed)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'settings' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                セキュリティ設定
              </h3>
              <div className="space-y-6">
                <div className="border-b border-gray-200 pb-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">WebAuthn設定</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">
                          WebAuthn認証の有効化
                        </label>
                        <p className="text-sm text-gray-500">
                          生体認証によるログインを有効にします
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">
                          認証タイムアウト（秒）
                        </label>
                        <p className="text-sm text-gray-500">
                          認証処理のタイムアウト時間
                        </p>
                      </div>
                      <input
                        type="number"
                        defaultValue={120}
                        className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <div className="border-b border-gray-200 pb-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">アクセス制御</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">
                          管理者専用機能の分離
                        </label>
                        <p className="text-sm text-gray-500">
                          セキュリティ機能を管理者のみに制限
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-4">監査ログ</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">
                          詳細ログの記録
                        </label>
                        <p className="text-sm text-gray-500">
                          すべてのアクセスとアクションをログに記録
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-6">
                  <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
                    設定を保存
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminSecurityPage;
