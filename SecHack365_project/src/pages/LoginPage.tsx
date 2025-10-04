import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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

  const handleWebAuthnLogin = async () => {
    if (!webAuthnSupported) {
      setError('このブラウザはWebAuthnをサポートしていません');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // デモ用のユーザー名を設定
      const username = 'doctor1';
      
      setError('WebAuthn認証を開始しています...');
      
      // まず登録を試行
      const registerResponse = await registerWebAuthn(username);
      if (registerResponse.success) {
        setError('WebAuthn認証情報を登録しました。認証を開始します...');
      }
      
      // 実際のWebAuthn認証を実行
      const response = await authenticateWebAuthn(username);
      
      if (response.success && response.user) {
        setError('認証成功！ログインしています...');
        setUser(response.user);
        localStorage.setItem('auth_token', 'webauthn_token');
        navigate('/dashboard');
      } else {
        setError(response.error || 'WebAuthn認証に失敗しました');
      }
    } catch (error) {
      setError('WebAuthn認証に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          患者情報共有システム
        </h1>
        
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>ユーザー名</label>
            <Input
              type="text"
              value={credentials.username}
              onChange={(value) => setCredentials({ ...credentials, username: value })}
              placeholder="ユーザー名を入力"
              required
            />
          </div>
          
          <div className="form-group">
            <label>パスワード</label>
            <Input
              type="password"
              value={credentials.password}
              onChange={(value) => setCredentials({ ...credentials, password: value })}
              placeholder="パスワードを入力"
              required
            />
          </div>
          
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <Button
              type="submit"
              variant="primary"
              disabled={isLoading}
              style={{ flex: 1 }}
            >
              {isLoading ? 'ログイン中...' : 'ログイン'}
            </Button>
            
            <Button
              type="button"
              variant="secondary"
              onClick={handleWebAuthnLogin}
              disabled={isLoading}
              style={{ flex: 1 }}
            >
              WebAuthn
            </Button>
          </div>
        </form>

        <div style={{ textAlign: 'center', fontSize: '14px', color: '#666' }}>
          <p>デモアカウント:</p>
          <p>doctor1 / admin1 / patient1</p>
        </div>
        
        {isLoading && (
          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            backgroundColor: '#f0f8ff', 
            border: '1px solid #007bff', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <div style={{ marginBottom: '10px' }}>
              <div style={{ 
                width: '20px', 
                height: '20px', 
                border: '2px solid #007bff', 
                borderTop: '2px solid transparent', 
                borderRadius: '50%', 
                animation: 'spin 1s linear infinite',
                margin: '0 auto'
              }}></div>
            </div>
            <div style={{ color: '#007bff', fontWeight: 'bold' }}>
              WebAuthn認証中...
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
