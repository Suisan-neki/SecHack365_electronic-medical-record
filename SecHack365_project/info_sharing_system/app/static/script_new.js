// SecHack365 医療DXシステム - 新しいJavaScript（Flask-Login対応）

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('SecHack365 医療DXシステム - Flask-Login版');
    
    // 古い認証システムの要素を非表示にする
    const oldAuthSection = document.getElementById('auth-section');
    if (oldAuthSection) {
        oldAuthSection.style.display = 'none';
    }
    
    // 古い認証ヘッダーを非表示にする
    const oldAuthHeader = document.getElementById('authenticated-header');
    if (oldAuthHeader) {
        oldAuthHeader.style.display = 'none';
    }
});

// 画面切り替え機能（患者向けビュー用）
function switchView(viewType) {
    if (viewType === 'patient') {
        document.getElementById('private-view').style.display = 'none';
        document.getElementById('patient-view').style.display = 'block';
        document.getElementById('medical-detail-view').style.display = 'none';
        // 患者データの読み込み（認証が必要な場合はサーバー側で処理）
        loadPatientDataIfAuthenticated();
    } else {
        document.getElementById('private-view').style.display = 'block';
        document.getElementById('patient-view').style.display = 'none';
        document.getElementById('medical-detail-view').style.display = 'none';
    }
}

// 認証が必要な患者データ読み込み
async function loadPatientDataIfAuthenticated() {
    console.log('患者データの読み込みを開始...');
    
    try {
        // 固定の患者ID P001を使用（実際のシステムでは動的に取得）
        const patientId = 'P001';
        console.log(`APIエンドポイントにアクセス中: /api/patient/${patientId}`);
        
        const response = await fetch(`/api/patient/${patientId}`, {
            method: 'GET',
            credentials: 'same-origin', // セッションクッキーを含める
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('患者データを取得しました:', data);
            
            // 医師向けプライベートビューに患者情報を表示
            displayPatientDataInPrivateView(data);
            
            // 患者向けビュー用のデータも設定
            displayPatientData(data);
            
            // ボタンの状態を更新
            enableSecondaryButtons();
            
            // 操作履歴に追加
            addOperationHistory('患者情報を抽出しました', data.patient_info?.name);
            
        } else if (response.status === 401) {
            try {
                const errorData = await response.json();
                console.error('認証エラー:', errorData);
                
                if (errorData.auth_method === 'password_required') {
                    alert('暗号化された患者データにアクセスするには、パスワード認証でログインしてください。\nWebAuthn認証では暗号化キーが利用できません。');
                    window.location.href = '/login';
                } else if (errorData.auth_method === 'decryption_failed') {
                    alert('暗号化データの復号に失敗しました。\n管理者に連絡してください。\n\nエラー: ' + errorData.error);
                } else if (errorData.auth_method === 'key_error') {
                    alert('暗号化キーの取得に失敗しました。\n再度ログインしてください。\n\nエラー: ' + errorData.error);
                    window.location.href = '/login';
                } else {
                    alert('認証エラーが発生しました。再度ログインしてください。\n\nエラー: ' + (errorData.error || '不明なエラー'));
                    window.location.href = '/login';
                }
            } catch (jsonError) {
                console.error('401エラーのJSONパースに失敗:', jsonError);
                alert('認証エラーが発生しました。再度ログインしてください。');
                window.location.href = '/login';
            }
        } else if (response.status === 403) {
            alert('この患者データへのアクセス権限がありません。');
        } else if (response.status === 404) {
            alert('患者データが見つかりません。');
        } else {
            try {
                const errorData = await response.json();
                alert(`エラー: ${errorData.error || '患者データの取得に失敗しました'}`);
            } catch (jsonError) {
                console.error('JSONパースエラー:', jsonError);
                alert(`HTTPエラー: ${response.status} ${response.statusText}\n患者データの取得に失敗しました。`);
            }
        }
    } catch (error) {
        console.error('患者データの読み込みエラー:', error);
        console.error('エラーの詳細:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        
        // より詳細なエラーメッセージを表示
        let errorMessage = 'データの読み込み中にエラーが発生しました。\n\n';
        errorMessage += `エラー種別: ${error.name}\n`;
        errorMessage += `エラー詳細: ${error.message}\n\n`;
        errorMessage += 'ブラウザのコンソール（F12）で詳細を確認してください。';
        
        alert(errorMessage);
    }
}

// 患者データ表示（患者向けビュー用）
function displayPatientData(data) {
    if (data.patient_info) {
        const patientNameElement = document.getElementById('patient-name');
        if (patientNameElement) {
            patientNameElement.textContent = data.patient_info.name || '患者名不明';
        }
    }
    // その他の患者データ表示処理...
}

// 医師向けプライベートビューに患者データを表示
function displayPatientDataInPrivateView(data) {
    console.log('医師向けビューに患者データを表示:', data);
    
    if (data.patient_info) {
        // 患者名を表示
        const nameElement = document.getElementById('doctor-patient-name');
        if (nameElement) {
            nameElement.textContent = data.patient_info.name || '患者名不明';
        }
        
        // 年齢を表示
        const ageElement = document.getElementById('doctor-patient-age');
        if (ageElement) {
            ageElement.textContent = data.patient_info.age ? `${data.patient_info.age}歳` : '-';
        }
        
        // 性別を表示
        const genderElement = document.getElementById('doctor-patient-gender');
        if (genderElement) {
            genderElement.textContent = data.patient_info.gender || '-';
        }
        
        // 患者IDを表示
        const idElement = document.getElementById('doctor-patient-id');
        if (idElement) {
            idElement.textContent = data.patient_info.id || '-';
        }
        
        // 患者カードのステータスを更新
        const statusElement = document.querySelector('.patient-status');
        if (statusElement) {
            statusElement.textContent = '患者情報を正常に取得しました';
            statusElement.style.color = '#28a745';
        }
    }
    
    // セキュリティ検証結果を表示
    if (data.signature_status || data.hash_chain_status) {
        console.log(`デジタル署名: ${data.signature_status}, ハッシュチェーン: ${data.hash_chain_status}`);
    }
}

// セカンダリボタンを有効化
function enableSecondaryButtons() {
    const rawDataBtn = document.getElementById('raw-data-btn');
    const patientViewBtn = document.getElementById('patient-view-btn');
    
    if (rawDataBtn) {
        rawDataBtn.disabled = false;
        rawDataBtn.classList.remove('disabled');
    }
    
    if (patientViewBtn) {
        patientViewBtn.disabled = false;
        patientViewBtn.classList.remove('disabled');
    }
}

// 操作履歴に追加
function addOperationHistory(operation, patientName = '') {
    const historyElement = document.getElementById('operation-history');
    if (historyElement) {
        const timestamp = new Date().toLocaleTimeString('ja-JP');
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <span class="history-time">${timestamp}</span>
            <span class="history-operation">${operation}</span>
            ${patientName ? `<span class="history-patient">(${patientName})</span>` : ''}
        `;
        historyElement.insertBefore(historyItem, historyElement.firstChild);
        
        // 履歴が多すぎる場合は古いものを削除
        while (historyElement.children.length > 5) {
            historyElement.removeChild(historyElement.lastChild);
        }
    }
}

// 医療詳細画面の表示
function showMedicalDetail(detailType) {
    document.getElementById('patient-view').style.display = 'none';
    document.getElementById('medical-detail-view').style.display = 'block';
    
    // すべての詳細セクションを非表示
    document.querySelectorAll('.detail-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // 選択された詳細タイプに応じて表示
    const detailTitleElement = document.getElementById('detail-title');
    const patientNameElement = document.getElementById('detail-patient-name');
    const patientName = document.getElementById('patient-name').textContent;
    
    if (patientNameElement) {
        patientNameElement.textContent = patientName;
    }
    
    switch(detailType) {
        case 'conditions':
            if (detailTitleElement) detailTitleElement.textContent = '現在の病気・症状';
            const conditionsDetail = document.getElementById('conditions-detail');
            if (conditionsDetail) conditionsDetail.style.display = 'block';
            loadConditionsDetail();
            break;
        case 'medications':
            if (detailTitleElement) detailTitleElement.textContent = '処方薬';
            const medicationsDetail = document.getElementById('medications-detail');
            if (medicationsDetail) medicationsDetail.style.display = 'block';
            loadMedicationsDetail();
            break;
        case 'tests':
            if (detailTitleElement) detailTitleElement.textContent = '検査結果';
            const testsDetail = document.getElementById('tests-detail');
            if (testsDetail) testsDetail.style.display = 'block';
            loadTestsDetail();
            break;
    }
}

// メニューに戻る
function backToMenu() {
    document.getElementById('medical-detail-view').style.display = 'none';
    document.getElementById('patient-view').style.display = 'block';
}

// 詳細データ読み込み関数
async function loadConditionsDetail() {
    console.log('病気・症状の詳細を読み込み中...');
    
    try {
        const patientId = 'P001';
        const response = await fetch(`/api/patient/${patientId}`);
        
        if (response.ok) {
            const data = await response.json();
            const conditionsContainer = document.getElementById('conditions-list');
            
            if (data.latest_record && conditionsContainer) {
                const diagnosis = data.latest_record.diagnosis || '診断情報なし';
                conditionsContainer.innerHTML = `
                    <div class="condition-item">
                        <h3>診断</h3>
                        <p>${diagnosis}</p>
                        <div class="condition-details">
                            <p><strong>担当医:</strong> ${data.latest_record.doctor || '不明'}</p>
                            <p><strong>診断日:</strong> ${new Date(data.latest_record.timestamp || Date.now()).toLocaleDateString('ja-JP')}</p>
                        </div>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('病気・症状データの読み込みエラー:', error);
    }
}

async function loadMedicationsDetail() {
    console.log('処方薬の詳細を読み込み中...');
    
    try {
        const patientId = 'P001';
        const response = await fetch(`/api/patient/${patientId}`);
        
        if (response.ok) {
            const data = await response.json();
            const medicationsContainer = document.getElementById('medications');
            
            if (data.latest_record && medicationsContainer) {
                const medication = data.latest_record.medication || '処方薬なし';
                medicationsContainer.innerHTML = `
                    <li class="medication-item">
                        <h4>現在の処方薬</h4>
                        <p><strong>薬名・用量:</strong> ${medication}</p>
                        <p><strong>処方医:</strong> ${data.latest_record.doctor || '不明'}</p>
                        <p><strong>処方日:</strong> ${new Date(data.latest_record.timestamp || Date.now()).toLocaleDateString('ja-JP')}</p>
                        <div class="medication-notes">
                            <p><strong>注意事項:</strong> ${data.latest_record.notes || '特記事項なし'}</p>
                        </div>
                    </li>
                `;
            }
        }
    } catch (error) {
        console.error('処方薬データの読み込みエラー:', error);
    }
}

async function loadTestsDetail() {
    console.log('検査結果の詳細を読み込み中...');
    
    try {
        const patientId = 'P001';
        const response = await fetch(`/api/patient/${patientId}`);
        
        if (response.ok) {
            const data = await response.json();
            const testsContainer = document.getElementById('test-results');
            
            if (data.latest_record && testsContainer) {
                const bloodPressure = data.latest_record.blood_pressure || '測定なし';
                const temperature = data.latest_record.temperature || '測定なし';
                
                testsContainer.innerHTML = `
                    <div class="test-result-item">
                        <h4>最新の検査結果</h4>
                        <div class="vital-signs">
                            <div class="vital-item">
                                <span class="vital-label">血圧:</span>
                                <span class="vital-value">${bloodPressure}</span>
                            </div>
                            <div class="vital-item">
                                <span class="vital-label">体温:</span>
                                <span class="vital-value">${temperature}</span>
                            </div>
                        </div>
                        <div class="test-details">
                            <p><strong>検査日:</strong> ${new Date(data.latest_record.timestamp || Date.now()).toLocaleDateString('ja-JP')}</p>
                            <p><strong>担当医:</strong> ${data.latest_record.doctor || '不明'}</p>
                            <p><strong>備考:</strong> ${data.latest_record.notes || '特記事項なし'}</p>
                        </div>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('検査結果データの読み込みエラー:', error);
    }
}

// セキュリティ検証ページを開く
function openSecurityVerificationPage() {
    // 新しいウィンドウでセキュリティ検証ページを開く
    window.open('/security_verification', '_blank');
}

// 患者情報抽出ボタン
function loadPatientData() {
    loadPatientDataIfAuthenticated();
}

// 生データ確認ボタン
async function showRawEHRData() {
    console.log('生データ確認を開始...');
    
    try {
        const patientId = 'P001';
        const response = await fetch(`/api/patient/${patientId}`);
        
        if (response.ok) {
            const data = await response.json();
            
            // 新しいウィンドウで生データを表示
            const rawDataWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
            rawDataWindow.document.write(`
                <!DOCTYPE html>
                <html lang="ja">
                <head>
                    <meta charset="UTF-8">
                    <title>生データ確認 - 患者ID: ${patientId}</title>
                    <style>
                        body { font-family: monospace; padding: 20px; background: #f5f5f5; }
                        .data-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
                        .section h3 { margin-top: 0; color: #333; }
                        pre { background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
                        .status { padding: 5px 10px; border-radius: 3px; font-weight: bold; }
                        .status.valid { background: #d4edda; color: #155724; }
                        .status.invalid { background: #f8d7da; color: #721c24; }
                    </style>
                </head>
                <body>
                    <div class="data-container">
                        <h1>電子カルテ生データ確認</h1>
                        <p><strong>患者ID:</strong> ${patientId}</p>
                        <p><strong>取得日時:</strong> ${new Date().toLocaleString('ja-JP')}</p>
                        
                        <div class="section">
                            <h3>セキュリティ検証結果</h3>
                            <p>デジタル署名: <span class="status ${data.signature_status === 'Valid' ? 'valid' : 'invalid'}">${data.signature_status}</span></p>
                            <p>ハッシュチェーン: <span class="status ${data.hash_chain_status === 'Valid' ? 'valid' : 'invalid'}">${data.hash_chain_status}</span></p>
                        </div>
                        
                        <div class="section">
                            <h3>患者基本情報（JSON形式）</h3>
                            <pre>${JSON.stringify(data.patient_info, null, 2)}</pre>
                        </div>
                        
                        <div class="section">
                            <h3>最新診療記録（JSON形式）</h3>
                            <pre>${JSON.stringify(data.latest_record, null, 2)}</pre>
                        </div>
                        
                        <div class="section">
                            <h3>完全なAPIレスポンス</h3>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    </div>
                </body>
                </html>
            `);
            rawDataWindow.document.close();
            
            // 操作履歴に追加
            addOperationHistory('生データを確認しました', data.patient_info?.name);
            
        } else {
            alert('生データの取得に失敗しました。');
        }
    } catch (error) {
        console.error('生データ取得エラー:', error);
        alert('生データの取得中にエラーが発生しました。');
    }
}
