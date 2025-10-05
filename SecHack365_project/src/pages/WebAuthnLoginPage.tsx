import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { authenticateWebAuthn, registerWebAuthn, isWebAuthnSupported } from '../utils/webauthn';
import Button from '../components/Button';
import Input from '../components/Input';

const WebAuthnLoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [webAuthnSupported, setWebAuthnSupported] = useState(false);
  const [isFirstTime, setIsFirstTime] = useState(false);
  const { setUser, setError } = useAppStore();
  const navigate = useNavigate();

  useEffect(() => {
    setWebAuthnSupported(isWebAuthnSupported());
  }, []);

  const handleWebAuthnLogin = async () => {
    if (!webAuthnSupported) {
      setError('このブラウザはWebAuthnをサポートしていません');
      return;
    }

    if (!username.trim()) {
      setError('ユーザー名を入力してください');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // まず登録を試行
      const registerResponse = await registerWebAuthn(username);
      if (registerResponse.success) {
        setError('WebAuthn認証情報を登録しました。認証を開始します...');
        setIsFirstTime(true);
        // 少し待ってから認証を実行
        setTimeout(async () => {
          try {
            const authResponse = await authenticateWebAuthn(username);
            if (authResponse.success && authResponse.user) {
              setError('認証成功！ログインしています...');
              setUser(authResponse.user);
              localStorage.setItem('auth_token', 'webauthn_token');
              navigate('/dashboard');
            } else {
              // キャンセルされた場合は特別なメッセージを表示
              if (authResponse.error && authResponse.error.includes('キャンセル')) {
                setError('認証がキャンセルされました。再度お試しください。');
              } else {
                setError(authResponse.error || 'WebAuthn認証に失敗しました');
              }
            }
          } catch (error) {
            setError('WebAuthn認証に失敗しました');
          } finally {
            setIsLoading(false);
          }
        }, 2000);
      } else {
        // 登録が失敗した場合、既存の認証情報で認証を試行
        const authResponse = await authenticateWebAuthn(username);
        if (authResponse.success && authResponse.user) {
          setError('認証成功！ログインしています...');
          setUser(authResponse.user);
          localStorage.setItem('auth_token', 'webauthn_token');
          navigate('/dashboard');
        } else {
          // キャンセルされた場合は特別なメッセージを表示
          if (authResponse.error && authResponse.error.includes('キャンセル')) {
            setError('認証がキャンセルされました。再度お試しください。');
          } else {
            setError(authResponse.error || 'WebAuthn認証に失敗しました');
          }
        }
        setIsLoading(false);
      }
    } catch (error) {
      setError('WebAuthn認証に失敗しました');
      setIsLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate('/login');
  };

  if (!webAuthnSupported) {
    return (
      <div className="container">
        <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
          <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
            WebAuthn認証
          </h1>
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#f8d7da', 
            border: '1px solid #f5c6cb', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#721c24', marginBottom: '10px' }}>❌ 非対応ブラウザ</h3>
            <p style={{ color: '#721c24' }}>
              このブラウザはWebAuthnをサポートしていません。<br/>
              最新のChrome、Firefox、Safari、Edgeをお使いください。
            </p>
          </div>
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <Button variant="secondary" onClick={handleBackToLogin}>
              通常ログインに戻る
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          🔐 WebAuthn認証
        </h1>
        
        <div style={{ 
          fontSize: '14px', 
          color: '#666', 
          textAlign: 'center', 
          marginBottom: '30px',
          padding: '15px',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px'
        }}>
          <strong>指紋・顔認証でログイン</strong><br/>
          ユーザー名を入力して、生体認証でログインしてください
        </div>

        <div className="form-group">
          <label>ユーザー名</label>
          <Input
            type="text"
            value={username}
            onChange={setUsername}
            placeholder="ユーザー名を入力（例: doctor1, admin1）"
            disabled={isLoading}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <Button
            variant="primary"
            onClick={handleWebAuthnLogin}
            disabled={isLoading || !username.trim()}
            style={{ flex: 1 }}
          >
            {isLoading ? '認証中...' : '🔐 WebAuthn認証'}
          </Button>
          
          <Button
            variant="secondary"
            onClick={handleBackToLogin}
            disabled={isLoading}
            style={{ flex: 1 }}
          >
            戻る
          </Button>
        </div>

        {isFirstTime && (
          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            backgroundColor: '#d1ecf1', 
            border: '1px solid #bee5eb', 
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            <h4 style={{ color: '#0c5460', marginBottom: '10px' }}>🎉 初回登録完了！</h4>
            <p style={{ color: '#0c5460' }}>
              指紋認証情報が登録されました。<br/>
              今後は同じユーザー名で指紋認証ができます。
            </p>
          </div>
        )}

        <div style={{ textAlign: 'center', fontSize: '12px', color: '#666', marginTop: '20px' }}>
          <p><strong>利用可能なユーザー:</strong></p>
          <p>doctor1, admin1, patient1</p>
        </div>
      </div>
    </div>
  );
};

export default WebAuthnLoginPage;
