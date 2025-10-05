// ブラウザの標準WebAuthn APIを直接使用

/**
 * Base64URL文字列をUint8Arrayに変換
 */
const base64urlToUint8Array = (base64url: string): Uint8Array => {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
};

export interface WebAuthnCredential {
  id: string;
  publicKey: string;
  counter: number;
  deviceType: string;
  backedUp: boolean;
  transports: string[];
}

export interface WebAuthnRegistrationResponse {
  success: boolean;
  credential?: WebAuthnCredential;
  error?: string;
}

export interface WebAuthnAuthenticationResponse {
  success: boolean;
  user?: {
    username: string;
    role: string;
  };
  error?: string;
}

/**
 * WebAuthn認証情報を登録
 */
export const registerWebAuthn = async (username: string): Promise<WebAuthnRegistrationResponse> => {
  try {
    // 1. サーバーから登録オプションを取得
    const response = await fetch('http://localhost:5002/api/webauthn/register/begin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username }),
    });

    if (!response.ok) {
      throw new Error('登録オプションの取得に失敗しました');
    }

    const options = await response.json();

    // 2. ブラウザでWebAuthn認証情報を作成（軽量化設定）
    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: base64urlToUint8Array(options.challenge),
        rp: options.rp,
        user: {
          ...options.user,
          id: base64urlToUint8Array(options.user.id)
        },
        pubKeyCredParams: options.pubKeyCredParams,
        timeout: options.timeout
      }
    }) as PublicKeyCredential;

    if (!credential) {
      throw new Error('認証情報の作成に失敗しました');
    }

    // 3. サーバーに認証情報を送信
    const verifyResponse = await fetch('http://localhost:5002/api/webauthn/register/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        credential: {
          id: credential.id,
          rawId: Array.from(new Uint8Array(credential.rawId)),
          response: {
            attestationObject: Array.from(new Uint8Array(credential.response.attestationObject)),
            clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON))
          },
          type: credential.type
        },
      }),
    });

    if (!verifyResponse.ok) {
      throw new Error('認証情報の検証に失敗しました');
    }

    const result = await verifyResponse.json();
    return result;

  } catch (error) {
    console.error('WebAuthn登録エラー:', error);

    let errorMessage = 'WebAuthn登録に失敗しました';

    if (error instanceof Error) {
      if (error.name === 'NotAllowedError') {
        errorMessage = '認証がキャンセルされました。';
      } else if (error.name === 'NotSupportedError') {
        errorMessage = 'このデバイスはWebAuthnをサポートしていません。';
      } else if (error.name === 'SecurityError') {
        errorMessage = 'セキュリティエラーが発生しました。';
      } else if (error.name === 'AbortError') {
        errorMessage = '認証が中断されました。';
      } else if (error.name === 'InvalidStateError') {
        errorMessage = '認証状態が無効です。';
      } else {
        errorMessage = error.message;
      }
    }

    return {
      success: false,
      error: errorMessage,
    };
  }
};

/**
 * WebAuthn認証を実行
 */
export const authenticateWebAuthn = async (username: string): Promise<WebAuthnAuthenticationResponse> => {
  try {
    // 1. サーバーから認証オプションを取得
    const response = await fetch('http://localhost:5002/api/webauthn/authenticate/begin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username }),
    });

    if (!response.ok) {
      throw new Error('認証オプションの取得に失敗しました');
    }

    const options = await response.json();
    console.log('認証オプション:', options);
    
    // 認証情報IDを正しい形式に変換
    if (options.allowCredentials && options.allowCredentials.length > 0) {
      options.allowCredentials[0].id = base64urlToUint8Array(options.allowCredentials[0].id);
    }

    // 2. ブラウザでWebAuthn認証を実行（軽量化設定）
    const credential = await navigator.credentials.get({
      publicKey: {
        challenge: base64urlToUint8Array(options.challenge),
        allowCredentials: options.allowCredentials,
        timeout: options.timeout
      }
    }) as PublicKeyCredential;

    // 3. サーバーに認証結果を送信
    const verifyResponse = await fetch('http://localhost:5002/api/webauthn/authenticate/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        credential: {
          id: credential.id,
          rawId: Array.from(new Uint8Array(credential.rawId)),
          response: {
            authenticatorData: Array.from(new Uint8Array(credential.response.authenticatorData)),
            clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON)),
            signature: Array.from(new Uint8Array(credential.response.signature)),
            userHandle: credential.response.userHandle ? Array.from(new Uint8Array(credential.response.userHandle)) : null
          },
          type: credential.type
        },
      }),
    });

    if (!verifyResponse.ok) {
      throw new Error('認証の検証に失敗しました');
    }

    const result = await verifyResponse.json();
    return result;

  } catch (error) {
    console.error('WebAuthn認証エラー:', error);

    let errorMessage = 'WebAuthn認証に失敗しました';

    if (error instanceof Error) {
      if (error.name === 'NotAllowedError') {
        errorMessage = '認証がキャンセルされました。';
      } else if (error.name === 'NotSupportedError') {
        errorMessage = 'このデバイスはWebAuthnをサポートしていません。';
      } else if (error.name === 'SecurityError') {
        errorMessage = 'セキュリティエラーが発生しました。';
      } else if (error.name === 'AbortError') {
        errorMessage = '認証が中断されました。';
      } else if (error.name === 'InvalidStateError') {
        errorMessage = '認証状態が無効です。';
      } else {
        errorMessage = error.message;
      }
    }

    return {
      success: false,
      error: errorMessage,
    };
  }
};

/**
 * WebAuthnが利用可能かチェック
 */
export const isWebAuthnSupported = (): boolean => {
  return !!(
    window.PublicKeyCredential &&
    window.navigator.credentials &&
    window.navigator.credentials.create &&
    window.navigator.credentials.get
  );
};

/**
 * 利用可能な認証方法を取得
 */
export const getAvailableAuthenticators = async (): Promise<string[]> => {
  const authenticators: string[] = [];

  try {
    // 生体認証（指紋・顔認証）のサポートチェック
    if (window.PublicKeyCredential) {
      const available = await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
      if (available) {
        authenticators.push('生体認証（指紋・顔認証）');
      }
    }

    // セキュリティキーのサポートチェック
    if (window.PublicKeyCredential) {
      const available = await window.PublicKeyCredential.isConditionalMediationAvailable();
      if (available) {
        authenticators.push('セキュリティキー');
      }
    }

    // その他の認証方法
    authenticators.push('スマートフォン認証');
    authenticators.push('USB認証デバイス');

  } catch (error) {
    console.error('認証方法の確認エラー:', error);
  }

  return authenticators;
};
