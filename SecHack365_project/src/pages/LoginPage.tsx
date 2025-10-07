import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import Button from '../components/Button';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { setUser } = useAppStore();
  const navigate = useNavigate();

  // ユーザーアカウントの定義
  const accounts = [
    { username: 'doctor1', password: 'doctor123', role: 'doctor', name: '医師1' },
    { username: 'doctor2', password: 'doctor456', role: 'doctor', name: '医師2' },
    { username: 'admin1', password: 'admin123', role: 'admin', name: '管理者1' },
    { username: 'admin2', password: 'admin456', role: 'admin', name: '管理者2' },
    { username: 'nurse1', password: 'nurse123', role: 'nurse', name: '看護師1' },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // アカウント認証
      const account = accounts.find(acc => 
        acc.username === username && acc.password === password
      );

      if (!account) {
        setError('ユーザー名またはパスワードが正しくありません');
        setIsLoading(false);
        return;
      }

      // ユーザー情報を設定
      const user = {
        username: account.username,
        role: account.role,
        name: account.name,
        loginTime: new Date().toISOString()
      };

      setUser(user);
      
      // ロールに応じてリダイレクト
      if (account.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }

    } catch (err) {
      setError('ログインに失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (account: typeof accounts[0]) => {
    setUsername(account.username);
    setPassword(account.password);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* ヘッダー */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl">🏥</span>
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            患者情報共有システム
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            アカウントにログインしてください
          </p>
        </div>

        {/* ログインフォーム */}
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                ユーザー名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-control mt-1"
                placeholder="ユーザー名を入力"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                パスワード
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-control mt-1"
                placeholder="パスワードを入力"
              />
            </div>
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          <div>
            <Button
              type="submit"
              variant="primary"
              className="w-full py-3"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="spinner w-5 h-5 mr-2"></div>
                  ログイン中...
                </div>
              ) : (
                'ログイン'
              )}
            </Button>
          </div>
        </form>

        {/* クイックログイン */}
        <div className="mt-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-4">クイックログイン</p>
            <div className="grid grid-cols-2 gap-3">
              {accounts.map((account) => (
                <button
                  key={account.username}
                  onClick={() => handleQuickLogin(account)}
                  className="btn btn-secondary py-2 text-xs"
                >
                  <div className="text-left">
                    <div className="font-medium">{account.name}</div>
                    <div className="text-xs opacity-75">
                      {account.role === 'doctor' ? '👨‍⚕️' : 
                       account.role === 'admin' ? '👨‍💼' : '👩‍⚕️'}
                      {account.role}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* アカウント情報 */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-medium text-blue-900 mb-2">利用可能なアカウント</h3>
          <div className="text-xs text-blue-700 space-y-1">
            <div><strong>医師:</strong> doctor1/doctor123, doctor2/doctor456</div>
            <div><strong>管理者:</strong> admin1/admin123, admin2/admin456</div>
            <div><strong>看護師:</strong> nurse1/nurse123</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;