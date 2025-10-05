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
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="card shadow-medical-lg border-0 bg-white/80 backdrop-blur-sm">
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
            
            <div className="flex gap-3">
              <Button
                type="submit"
                variant="primary"
                disabled={isLoading}
                className="flex-1 py-3 text-base font-medium"
              >
                {isLoading ? 'ログイン中...' : 'パスワードログイン'}
              </Button>
              
              <Link
                to="/webauthn-login"
                className="flex-1"
              >
                <Button
                  type="button"
                  variant="secondary"
                  disabled={isLoading}
                  className="w-full py-3 text-base font-medium"
                >
                  🔐 WebAuthn
                </Button>
              </Link>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
              <div className="text-sm text-blue-800">
                <strong className="block mb-1">WebAuthn認証:</strong>
                <span className="text-xs">
                  指紋・顔認証などの生体認証でログインできます<br/>
                  専用ページでユーザー名を入力してください
                </span>
              </div>
            </div>
          </form>

          <div className="mt-6 text-center">
            <div className="text-sm text-gray-600 mb-2">デモアカウント:</div>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <span className="bg-gray-100 px-2 py-1 rounded">doctor1</span>
              <span className="bg-gray-100 px-2 py-1 rounded">admin1</span>
              <span className="bg-gray-100 px-2 py-1 rounded">patient1</span>
            </div>
          </div>
          
          {isLoading && (
            <div className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-lg text-center">
              <div className="spinner mb-3"></div>
              <div className="text-primary-700 font-medium">
                WebAuthn認証中...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
