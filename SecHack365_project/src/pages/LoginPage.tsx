import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { api } from '../api/client';
import { authenticateWebAuthn, registerWebAuthn, isWebAuthnSupported, getAvailableAuthenticators } from '../utils/webauthn';
import Button from '../components/Button';
import Input from '../components/Input';

const LoginPage: React.FC = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [webAuthnSupported, setWebAuthnSupported] = useState(false);
  const [availableAuthenticators, setAvailableAuthenticators] = useState<string[]>([]);
  const { setUser, setError } = useAppStore();
  const navigate = useNavigate();

  useEffect(() => {
    // WebAuthnサポートチェック
    setWebAuthnSupported(isWebAuthnSupported());
    
    if (isWebAuthnSupported()) {
      getAvailableAuthenticators().then(setAvailableAuthenticators);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.login(credentials);
      if (response.success) {
        setUser(response.data.user);
        localStorage.setItem('auth_token', response.data.token);
        navigate('/dashboard');
      } else {
        setError(response.message || 'ログインに失敗しました');
      }
    } catch (error) {
      setError('ログインに失敗しました');
    } finally {
      setIsLoading(false);
    }
  };


  return (
         <div className="min-h-screen flex items-center justify-center px-4">
           <div className="w-full max-w-md">
             <div className="card">
          {/* ヘッダー */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-full mb-4">
              <span className="text-2xl">🏥</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              患者情報共有システム
            </h1>
            <p className="text-sm text-gray-600">
              安全で効率的な医療情報管理
            </p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ユーザー名
              </label>
              <Input
                type="text"
                value={credentials.username}
                onChange={(value) => setCredentials({ ...credentials, username: value })}
                placeholder="ユーザー名を入力"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
            </div>
            
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                パスワード
              </label>
              <Input
                type="password"
                value={credentials.password}
                onChange={(value) => setCredentials({ ...credentials, password: value })}
                placeholder="パスワードを入力"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
            </div>
            
                 <Button
                   type="submit"
                   variant="primary"
                   disabled={isLoading}
                   className="w-full py-3 text-base font-medium"
                 >
                   {isLoading ? 'ログイン中...' : 'ログイン'}
                 </Button>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <div className="text-sm text-green-800">
                <strong className="block mb-1">シンプルログイン:</strong>
                <span className="text-xs">
                  ユーザー名とパスワードで簡単ログイン<br/>
                  デモアカウントでお試しください
                </span>
              </div>
            </div>
          </form>

          <div className="mt-6 text-center">
            <div className="text-sm text-gray-600 mb-2">デモアカウント（パスワード: 123456）:</div>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <span className="bg-blue-100 px-2 py-1 rounded text-blue-800">doctor1</span>
              <span className="bg-purple-100 px-2 py-1 rounded text-purple-800">admin1</span>
              <span className="bg-green-100 px-2 py-1 rounded text-green-800">patient1</span>
            </div>
          </div>
          
          {isLoading && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
              <div className="spinner mb-3"></div>
              <div className="text-blue-700 font-medium">
                ログイン中...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
