import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { api } from '../api/client';
import Button from '../components/Button';
import Input from '../components/Input';

const LoginPage: React.FC = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const { setUser, setError } = useAppStore();
  const navigate = useNavigate();

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
    setIsLoading(true);
    setError(null);

    try {
      // デモ用のユーザー名を設定
      const username = 'doctor1';
      const response = await api.authenticateWebAuthn(username);
      if (response.success) {
        setUser(response.user);
        localStorage.setItem('auth_token', 'demo_token');
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
      </div>
    </div>
  );
};

export default LoginPage;
