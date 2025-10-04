// ブラウザの標準WebAuthn APIを直接使用

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
    const response = await fetch('/api/webauthn/register/begin', {
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

    // 2. ブラウザでWebAuthn認証情報を作成
    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: new Uint8Array(options.challenge),
        rp: options.rp,
        user: options.user,
        pubKeyCredParams: options.pubKeyCredParams,
        authenticatorSelection: options.authenticatorSelection,
        timeout: options.timeout,
        attestation: options.attestation
      }
    }) as PublicKeyCredential;

    if (!credential) {
      throw new Error('認証情報の作成に失敗しました');
    }

    // 3. サーバーに認証情報を送信
    const verifyResponse = await fetch('/api/webauthn/register/complete', {
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
    return {
      success: false,
      error: error instanceof Error ? error.message : 'WebAuthn登録に失敗しました',
    };
  }
};

/**
 * WebAuthn認証を実行
 */
export const authenticateWebAuthn = async (username: string): Promise<WebAuthnAuthenticationResponse> => {
  try {
    // 1. サーバーから認証オプションを取得
    const response = await fetch('/api/webauthn/authenticate/begin', {
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

    // 2. ブラウザでWebAuthn認証を実行
    const credential = await navigator.credentials.get({
      publicKey: {
        challenge: new Uint8Array(options.challenge),
        allowCredentials: options.allowCredentials,
        userVerification: options.userVerification,
        timeout: options.timeout
      }
    }) as PublicKeyCredential;

    // 3. サーバーに認証結果を送信
    const verifyResponse = await fetch('/api/webauthn/authenticate/complete', {
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
    return {
      success: false,
      error: error instanceof Error ? error.message : 'WebAuthn認証に失敗しました',
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
