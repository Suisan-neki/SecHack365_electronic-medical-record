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
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="card shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <span className="text-2xl">❌</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                WebAuthn認証
              </h1>
            </div>
            
            <div className="alert alert-error text-center">
              <h3 className="font-semibold mb-2">❌ 非対応ブラウザ</h3>
              <p className="text-sm">
                このブラウザはWebAuthnをサポートしていません。<br/>
                最新のChrome、Firefox、Safari、Edgeをお使いください。
              </p>
            </div>
            
            <div className="mt-6 text-center">
              <Button variant="secondary" onClick={handleBackToLogin} className="px-6 py-3">
                通常ログインに戻る
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-medical-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="card shadow-medical-lg border-0 bg-white/80 backdrop-blur-sm">
          {/* ヘッダー */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-full mb-4">
              <span className="text-2xl">🔐</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              WebAuthn認証
            </h1>
            <p className="text-sm text-gray-600">
              生体認証による安全なログイン
            </p>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center mb-6">
            <div className="text-sm text-blue-800">
              <strong className="block mb-1">指紋・顔認証でログイン</strong>
              <span className="text-xs">
                ユーザー名を入力して、生体認証でログインしてください
              </span>
            </div>
          </div>

          <div className="form-group">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ユーザー名
            </label>
            <Input
              type="text"
              value={username}
              onChange={setUsername}
              placeholder="ユーザー名を入力（例: doctor1, admin1）"
              disabled={isLoading}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            />
          </div>

          <div className="flex gap-3 mb-6">
            <Button
              variant="primary"
              onClick={handleWebAuthnLogin}
              disabled={isLoading || !username.trim()}
              className="flex-1 py-3 text-base font-medium"
            >
              {isLoading ? '認証中...' : '🔐 WebAuthn認証'}
            </Button>
            
            <Button
              variant="secondary"
              onClick={handleBackToLogin}
              disabled={isLoading}
              className="flex-1 py-3 text-base font-medium"
            >
              戻る
            </Button>
          </div>

          {isFirstTime && (
            <div className="mt-6 p-4 bg-medical-50 border border-medical-200 rounded-lg text-center">
              <div className="flex items-center justify-center mb-2">
                <span className="text-2xl mr-2">🎉</span>
                <h4 className="text-medical-800 font-semibold">初回登録完了！</h4>
              </div>
              <p className="text-sm text-medical-700">
                指紋認証情報が登録されました。<br/>
                今後は同じユーザー名で指紋認証ができます。
              </p>
            </div>
          )}

          <div className="mt-6 text-center">
            <div className="text-sm text-gray-600 mb-2">利用可能なユーザー:</div>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <span className="bg-gray-100 px-2 py-1 rounded">doctor1</span>
              <span className="bg-gray-100 px-2 py-1 rounded">admin1</span>
              <span className="bg-gray-100 px-2 py-1 rounded">patient1</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebAuthnLoginPage;
