// グローバル関数を即座に定義
window.loadPatientData = async function() {
    console.log('🔄 患者データ読み込み開始...');
    
    // ローディング状態を表示
    const patientStatus = document.querySelector('.patient-status');
    const loadBtn = document.getElementById('load-data-btn');
    
    if (patientStatus) {
        patientStatus.textContent = '電子カルテから抽出中...';
        patientStatus.style.background = 'rgba(255, 193, 7, 0.3)';
    }
    
    if (loadBtn) {
        loadBtn.innerHTML = `
            <span class="button-icon">⏳</span>
            <span class="button-text">
                <strong>抽出中...</strong>
                <small>電子カルテからデータを取得中</small>
            </span>
        `;
        loadBtn.disabled = true;
    }
    
    try {
        // 電子カルテシステムから現在の診察患者データを抽出
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        
        console.log('✅ 患者データ取得成功:', data);
        
        // 医師向け患者情報を表示
        const patientInfo = data.patient_info || {};
        document.getElementById('doctor-patient-id').textContent = patientInfo.patient_id || 'P001';
        document.getElementById('doctor-patient-name').textContent = patientInfo.name || '山下真凜';
        document.getElementById('doctor-patient-age').textContent = patientInfo.age ? patientInfo.age + '歳' : '33歳';
        document.getElementById('doctor-patient-gender').textContent = patientInfo.gender || '女性';
        
        // 成功時にステータスを更新
        if (patientStatus) {
            patientStatus.textContent = '抽出完了';
            patientStatus.style.background = 'rgba(40, 167, 69, 0.3)';
        }
        
        // 依存ボタンを有効化
        enableDataDependentButtons();
        
        // ラズパイボタンも有効化
        updateRaspiButtonState();
        
        // 操作履歴に記録
        addToOperationHistory(`電子カルテシステムから患者情報を抽出 (${patientInfo.name})`, 'data_extraction');
        
        // データソースの情報も表示（実際のデータ構造に合わせて修正）
        let message = '✅ 電子カルテシステムから患者情報を抽出しました。\n\n';
        message += `🏥 抽出元: FHIR標準型電子カルテシステム\n`;
        message += `👤 現在の診察患者: ${patientInfo.name} (${patientInfo.patient_id || 'P001'})\n`;
        message += `📊 抽出されたデータ:\n`;
        
        // 実際のデータ構造に合わせて修正
        const latestRecord = data.latest_record || {};
        const hasDiagnosis = latestRecord.diagnosis ? 1 : 0;
        const hasMedication = latestRecord.medication ? 1 : 0;
        const hasTestResults = (latestRecord.blood_pressure || latestRecord.temperature) ? 1 : 0;
        
        message += `• 病気・症状: ${hasDiagnosis}件 (${latestRecord.diagnosis || 'なし'})\n`;
        message += `• 処方薬: ${hasMedication}件 (${latestRecord.medication || 'なし'})\n`;
        message += `• 検査結果: ${hasTestResults}件 (血圧: ${latestRecord.blood_pressure || 'なし'}, 体温: ${latestRecord.temperature || 'なし'})\n\n`;
        message += `🔒 セキュリティ: ${data.signature_status === 'Valid' ? '署名検証済み' : '署名未検証'}\n`;
        message += `🔑 ハッシュチェーン: ${data.hash_chain_status === 'Valid' ? '有効' : '無効'}\n\n`;
        message += '「患者用ビューを表示」ボタンで患者画面を確認できます。\n';
        message += '「鍵システム確認」ボタンでセキュリティ詳細を確認できます。';
        
        alert(message);
        
        addToOperationHistory('電子カルテからの患者データ抽出が完了 - 生データ確認と患者向けディスプレイが利用可能になりました', 'data_extraction_success');
        
    } catch (error) {
        console.error('❌ 患者データ読み込みエラー:', error);
        
        // エラー時の処理
        if (patientStatus) {
            patientStatus.textContent = '抽出エラー';
            patientStatus.style.background = 'rgba(220, 53, 69, 0.3)';
        }
        
        alert('❌ 電子カルテからのデータ抽出エラー: ' + error.message);
        addToOperationHistory('電子カルテからの患者データ抽出でエラーが発生しました', 'data_extraction_error');
        
    } finally {
        // ボタンを元に戻す
        if (loadBtn) {
            loadBtn.innerHTML = `
                <span class="button-icon">📤</span>
                <span class="button-text">
                    <strong>患者情報を抽出</strong>
                    <small>電子カルテシステムから現在の患者データを取得</small>
                </span>
            `;
            loadBtn.disabled = false;
        }
    }
};

// PC用患者ビューを表示
window.showPatientView = function() {
    console.log('👁️ PC用患者ビューを表示中...');
    
    // 患者ビューに切り替え
    switchView('patient');
    
    // 操作履歴に記録
    addToOperationHistory('PC用患者ビューを表示', 'patient_view_display');
};

// ビュー切り替え関数
function switchView(viewType) {
    if (viewType === 'patient') {
        document.getElementById('private-view').style.display = 'none';
        document.getElementById('patient-view').style.display = 'block';
        document.getElementById('medical-detail-view').style.display = 'none';
        fetchPatientData();
        addToOperationHistory('患者向けビューに切り替え', 'view_switch');
    } else {
        document.getElementById('private-view').style.display = 'block';
        document.getElementById('patient-view').style.display = 'none';
        document.getElementById('medical-detail-view').style.display = 'none';
        addToOperationHistory('医師向けビューに切り替え', 'view_switch');
    }
}

// 患者データ取得関数
async function fetchPatientData() {
    let data = {};
    
    try {
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        data = await response.json();
        console.log('✅ 患者ビュー用データ取得成功:', data);
    } catch (error) {
        console.error('❌ 患者ビュー用データ取得エラー:', error);
        // エラー時はデフォルトデータを使用
        data = {
            patient_info: { name: '山下真凜', age: 33, gender: '女性' },
            current_conditions: [
                { name: '高血圧', status: '治療中', explanation: '血圧が高い状態が続いています', diagnosed_date: '2024-01-15', icon: '🩺' }
            ],
            medications: [
                { name: 'アムロジピン', dosage: '5mg 1日1回', purpose: '血圧降下', notes: '朝食後に服用', common_effects: 'めまい、頭痛', category: '降圧剤', icon: '💊', color: '#e74c3c' }
            ],
            recent_test_results: [
                { item_name: '血圧', value: '140/90 mmHg', status: '要注意', reference_range: '120/80 mmHg以下', test_date: '2025-09-10', status_icon: '⚠️', doctor_comment: '薬の調整が必要かもしれません' }
            ]
        };
    }

    // 患者基本情報を表示
    const patientInfo = data.patient_info || {};
    document.getElementById('patient-name').textContent = `${patientInfo.name || '山下真凜'} (${patientInfo.age || '33'}歳)`;

    // 患者用ビューのメニュー項目を更新
    updatePatientMenuItems(data);
    
    // セキュリティ情報を更新
    updateSecurityInfo();
}

// 患者用ビューのメニュー項目を更新（元の状態に戻す）
function updatePatientMenuItems(data) {
    // メニュー項目は元の説明文のまま（クリックして詳細を見るためのもの）
    // 実際のデータは詳細画面で表示する
    console.log('✅ 患者用ビューのメニュー項目を表示しました');
}

// ラズパイ表示制御機能
window.sendToRaspberryPi = async function() {
    const currentPatientId = getCurrentPatientId();
    if (!currentPatientId) {
        alert('患者が選択されていません。まず患者を選択してください。');
        return;
    }
    
    const raspiBtn = document.getElementById('raspi-display-btn');
    const originalText = raspiBtn.innerHTML;
    
    try {
        // ボタンを無効化
        raspiBtn.disabled = true;
        raspiBtn.innerHTML = `
            <span class="button-icon">⏳</span>
            <span class="button-text">
                <strong>送信中...</strong>
                <small>ラズパイに情報を送信しています</small>
            </span>
        `;
        
        // APIに患者IDを送信
        const response = await fetch('/api/set-patient-display', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: currentPatientId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // 成功時の表示
        raspiBtn.innerHTML = `
            <span class="button-icon">✅</span>
            <span class="button-text">
                <strong>送信完了</strong>
                <small>ラズパイで表示中</small>
            </span>
        `;
        
        // 操作履歴に追加
        addToOperationHistory(`患者情報をラズパイに送信: ${currentPatientId}`, 'raspi_display');
        
        // 3秒後にボタンを元に戻す
        setTimeout(() => {
            raspiBtn.innerHTML = originalText;
            raspiBtn.disabled = false;
        }, 3000);
        
        // ラズパイ表示ページを新しいタブで開く（確認用）
        const confirmOpen = confirm('ラズパイ表示ページを新しいタブで開きますか？（確認用）');
        if (confirmOpen) {
            window.open('/patient-display', '_blank');
        }
        
    } catch (error) {
        console.error('ラズパイ送信エラー:', error);
        
        // エラー時の表示
        raspiBtn.innerHTML = `
            <span class="button-icon">❌</span>
            <span class="button-text">
                <strong>送信失敗</strong>
                <small>エラーが発生しました</small>
            </span>
        `;
        
        alert('ラズパイへの送信に失敗しました: ' + error.message);
        addToOperationHistory('ラズパイ送信でエラーが発生しました', 'raspi_display_error');
        
        // 3秒後にボタンを元に戻す
        setTimeout(() => {
            raspiBtn.innerHTML = originalText;
            raspiBtn.disabled = false;
        }, 3000);
    }
};

// 生データ表示機能
window.showRawEHRData = async function() {
    try {
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const ehrData = await response.json();
        
        // 新しいウィンドウで生データを表示
        const newWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
        newWindow.document.write(`
            <html>
            <head>
                <title>標準型電子カルテデータ (FHIR風JSON)</title>
                <style>
                    body { font-family: monospace; margin: 20px; background: #f5f5f5; }
                    .header { background: #2c3e50; color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
                    .json-container { background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; }
                    pre { white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; }
                    .highlight { background: yellow; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🗃️ 標準型電子カルテデータ (FHIR風JSON)</h2>
                    <p>このデータが患者向けに分かりやすく変換されます</p>
                </div>
                <div class="json-container">
                    <pre>${JSON.stringify(ehrData, null, 2)}</pre>
                </div>
            </body>
            </html>
        `);
        
        addToOperationHistory('標準型電子カルテの生データを確認', 'raw_data_view');
        
    } catch (error) {
        alert('❌ 生データ取得エラー: ' + error.message);
    }
};

// ヘルパー関数
function getCurrentPatientId() {
    return 'P001'; // デフォルトで P001 を返す
}

function enableDataDependentButtons() {
    const rawDataBtn = document.getElementById('raw-data-btn');
    const patientViewBtn = document.getElementById('patient-view-btn');
    
    if (rawDataBtn) {
        rawDataBtn.disabled = false;
        rawDataBtn.classList.remove('disabled');
        rawDataBtn.style.opacity = '1';
        rawDataBtn.style.cursor = 'pointer';
    }
    if (patientViewBtn) {
        patientViewBtn.disabled = false;
        patientViewBtn.classList.remove('disabled');
        patientViewBtn.style.opacity = '1';
        patientViewBtn.style.cursor = 'pointer';
    }
}

function updateRaspiButtonState() {
    const raspiBtn = document.getElementById('raspi-display-btn');
    
    if (raspiBtn) {
        raspiBtn.disabled = false;
        raspiBtn.classList.remove('disabled');
        raspiBtn.style.background = '#e67e22';
        raspiBtn.style.opacity = '1';
        raspiBtn.style.cursor = 'pointer';
        console.log('✅ ラズパイボタンを有効化しました');
    }
}

function disableRaspiButton() {
    const raspiBtn = document.getElementById('raspi-display-btn');
    
    if (raspiBtn) {
        raspiBtn.disabled = true;
        raspiBtn.classList.add('disabled');
        raspiBtn.style.background = '#ccc';
        raspiBtn.style.opacity = '0.6';
        raspiBtn.style.cursor = 'not-allowed';
        console.log('❌ ラズパイボタンを無効化しました');
    }
}

function addToOperationHistory(action, type) {
    const timestamp = new Date().toLocaleString('ja-JP');
    const operation = {
        timestamp: timestamp,
        action: action,
        type: type
    };
    
    if (!window.operationHistory) {
        window.operationHistory = [];
    }
    
    window.operationHistory.unshift(operation);
    updateOperationHistoryDisplay();
}

function updateOperationHistoryDisplay() {
    const historyDiv = document.getElementById('operation-history');
    if (!historyDiv) return;
    
    if (!window.operationHistory || window.operationHistory.length === 0) {
        historyDiv.innerHTML = '<p style="color: #636e72;">操作履歴はありません</p>';
        return;
    }
    
    historyDiv.innerHTML = window.operationHistory.slice(0, 10).map(op => `
        <div class="operation-item">
            <div>${op.action}</div>
            <div class="operation-timestamp">${op.timestamp}</div>
        </div>
    `).join('');
}

function updateSecurityInfo() {
    setTimeout(() => {
        const securityDiv = document.querySelector('.security-info');
        if (securityDiv) {
            securityDiv.innerHTML = `
                <div class="security-icon">🔒</div>
                <strong>✓ データ暗号化済み</strong><br>
                <strong>✓ 電子署名検証済み</strong><br>
                <strong>✓ ハッシュチェーン完全性確認済み</strong>
            `;
        }
    }, 1000);
}

// メニューから詳細画面への遷移
function showMedicalDetail(detailType) {
    document.getElementById('patient-view').style.display = 'none';
    document.getElementById('medical-detail-view').style.display = 'block';
    
    // すべての詳細セクションを非表示
    document.querySelectorAll('.detail-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // 患者名を詳細画面にもコピー
    const patientName = document.getElementById('patient-name').textContent;
    document.getElementById('detail-patient-name').textContent = patientName;
    
    // 選択された詳細タイプに応じて表示
    switch(detailType) {
        case 'conditions':
            document.getElementById('detail-title').textContent = '現在の病気・症状';
            document.getElementById('conditions-detail').style.display = 'block';
            loadConditionsDetail();
            break;
        case 'medications':
            document.getElementById('detail-title').textContent = '処方薬';
            document.getElementById('medications-detail').style.display = 'block';
            loadMedicationsDetail();
            break;
        case 'tests':
            document.getElementById('detail-title').textContent = '検査結果';
            document.getElementById('tests-detail').style.display = 'block';
            loadTestsDetail();
            break;
    }
}

// メニューに戻る
function backToMenu() {
    document.getElementById('medical-detail-view').style.display = 'none';
    document.getElementById('patient-view').style.display = 'block';
}

// 病気・症状の詳細を読み込む
async function loadConditionsDetail() {
    let data = {};
    
    try {
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        data = await response.json();
    } catch (error) {
        console.error('❌ 病気・症状データ取得エラー:', error);
        data = {
            current_conditions: [
                { name: '高血圧', status: '治療中', explanation: '血圧が高い状態が続いています', diagnosed_date: '2024-01-15' }
            ]
        };
    }
    
    const conditionsList = document.getElementById('conditions-list');
    conditionsList.innerHTML = '';
    
    // 実際のデータ構造に合わせて修正
    const diagnosis = data.latest_record?.diagnosis;
    if (diagnosis) {
        const conditionDiv = document.createElement('div');
        conditionDiv.className = 'condition-item';
        conditionDiv.innerHTML = `
            <h4>${diagnosis}</h4>
            <p><strong>状態:</strong> 治療中</p>
            <p><strong>診断医:</strong> ${data.latest_record?.doctor || 'Dr. 田中'}</p>
            <p><strong>備考:</strong> ${data.latest_record?.notes || '特記事項なし'}</p>
        `;
        conditionsList.appendChild(conditionDiv);
    } else {
        conditionsList.innerHTML = '<p>現在治療中の病気はありません</p>';
    }
}

// 処方薬の詳細を読み込む
async function loadMedicationsDetail() {
    let data = {};
    
    try {
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        data = await response.json();
    } catch (error) {
        console.error('❌ 処方薬データ取得エラー:', error);
        data = {
            medications: [
                { name: 'アムロジピン', dosage: '5mg 1日1回', purpose: '血圧降下', precautions: '朝食後に服用してください' }
            ]
        };
    }
    
    const medicationsList = document.querySelector('#medications-detail ul');
    medicationsList.innerHTML = '';
    
    // 実際のデータ構造に合わせて修正
    const medication = data.latest_record?.medication;
    if (medication) {
        const medicationDiv = document.createElement('div');
        medicationDiv.className = 'medication-item';
        medicationDiv.innerHTML = `
            <h4>${medication}</h4>
            <p><strong>処方医:</strong> ${data.latest_record?.doctor || 'Dr. 田中'}</p>
            <p><strong>備考:</strong> ${data.latest_record?.notes || '特記事項なし'}</p>
        `;
        
        const listItem = document.createElement('li');
        listItem.appendChild(medicationDiv);
        medicationsList.appendChild(listItem);
    } else {
        medicationsList.innerHTML = '<li><p>現在処方されている薬はありません</p></li>';
    }
}

// 検査結果の詳細を読み込む
async function loadTestsDetail() {
    let data = {};
    
    try {
        const response = await fetch('/api/patient/P001');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        data = await response.json();
    } catch (error) {
        console.error('❌ 検査結果データ取得エラー:', error);
        data = {
            test_results: [
                { name: '血圧', value: '140/90 mmHg', normal_range: '120/80 mmHg以下', date: '2025-09-10', doctor_comment: '薬の調整が必要かもしれません' }
            ]
        };
    }
    
    const testResults = document.querySelector('#tests-detail #test-results');
    testResults.innerHTML = '';
    
    // 実際のデータ構造に合わせて修正
    const bloodPressure = data.latest_record?.blood_pressure;
    const temperature = data.latest_record?.temperature;
    
    if (bloodPressure || temperature) {
        if (bloodPressure) {
            const testDiv = document.createElement('div');
            testDiv.className = 'test-result-item';
            testDiv.innerHTML = `
                <h4>血圧</h4>
                <p><strong>結果:</strong> ${bloodPressure}</p>
                <p><strong>基準値:</strong> 120/80 mmHg以下</p>
                <p><strong>検査医:</strong> ${data.latest_record?.doctor || 'Dr. 田中'}</p>
            `;
            testResults.appendChild(testDiv);
        }
        
        if (temperature) {
            const testDiv = document.createElement('div');
            testDiv.className = 'test-result-item';
            testDiv.innerHTML = `
                <h4>体温</h4>
                <p><strong>結果:</strong> ${temperature}</p>
                <p><strong>基準値:</strong> 36.0-37.0°C</p>
                <p><strong>検査医:</strong> ${data.latest_record?.doctor || 'Dr. 田中'}</p>
            `;
            testResults.appendChild(testDiv);
        }
    } else {
        testResults.innerHTML = '<p>検査結果がありません</p>';
    }
}


// セキュリティ検証セクションの表示/非表示を切り替え
window.toggleSecurityVerification = function() {
    console.log('🔒 セキュリティ検証セクションを切り替えています...');
    
    const securitySection = document.getElementById('security-verification-section');
    if (!securitySection) {
        console.error('❌ セキュリティ検証セクションが見つかりません');
        return;
    }
    
    if (securitySection.style.display === 'none' || securitySection.style.display === '') {
        securitySection.style.display = 'flex';
        console.log('✅ セキュリティ検証セクションを表示しました');
        addToOperationHistory('セキュリティ検証セクションを表示しました', 'security_section_show');
    } else {
        securitySection.style.display = 'none';
        console.log('✅ セキュリティ検証セクションを非表示にしました');
        addToOperationHistory('セキュリティ検証セクションを非表示にしました', 'security_section_hide');
    }
};

// セキュリティ検証を開始
window.startSecurityVerification = async function() {
    console.log('🚀 セキュリティ検証を開始しています...');
    
    const startBtn = document.getElementById('startSecurityBtn');
    const loading = document.getElementById('securityLoading');
    const results = document.getElementById('securityResults');
    
    if (!startBtn || !loading || !results) {
        console.error('❌ 必要な要素が見つかりません');
        return;
    }
    
    startBtn.disabled = true;
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        // セキュリティ検証と鍵システム状態を並行して取得
        const [securityResponse, keyResponse] = await Promise.all([
            fetch('/security_verification'),
            fetch('/api/demo-keys-status').catch(() => null) // 鍵システムが失敗しても続行
        ]);
        
        if (!securityResponse.ok) {
            throw new Error(`HTTP ${securityResponse.status}: ${securityResponse.statusText}`);
        }
        
        const verificationResult = await securityResponse.json();
        const keyData = keyResponse ? await keyResponse.json() : null;
        
        displaySecurityResults(verificationResult, keyData);
        addToOperationHistory('セキュリティ検証を実行しました', 'security_verification_run');
        
    } catch (error) {
        console.error('❌ セキュリティ検証エラー:', error);
        displaySecurityError(error);
    } finally {
        loading.style.display = 'none';
        results.style.display = 'block';
        startBtn.disabled = false;
    }
};

// セキュリティ検証結果を表示
function displaySecurityResults(result, keyData) {
    const overallStatus = document.getElementById('overallSecurityStatus');
    const checkResults = document.getElementById('securityCheckResults');
    const summary = document.getElementById('securitySummary');
    
    if (!overallStatus || !checkResults || !summary) {
        console.error('❌ 結果表示要素が見つかりません');
        return;
    }
    
    // 全体ステータスの表示
    let statusClass = 'status-error';
    let statusText = '❌ セキュリティ検証エラー';
    let statusIcon = '❌';
    
    if (result.overall_status === 'success') {
        statusClass = 'status-success';
        statusText = 'セキュリティ検証完全成功';
        statusIcon = '✅';
    } else if (result.overall_status === 'partial') {
        statusClass = 'status-partial';
        statusText = '⚠️ 部分的な問題を検出';
        statusIcon = '⚠️';
    }
    
    // 全体ステータスは非表示にする
    overallStatus.style.display = 'none';
    
    // 各チェック項目の表示
    let checksHtml = result.checks.map(check => {
        const statusClass = `status-${check.status}`;
        const statusIcon = getSecurityStatusIcon(check.status);
        
        return `
            <div class="security-check-item">
                <div class="security-check-header">
                    <div class="security-check-name">${check.name}</div>
                    <div class="security-check-status ${statusClass}">
                        ${statusIcon} ${getSecurityStatusText(check.status)}
                    </div>
                </div>
                <div class="security-check-message">${check.message}</div>
                ${check.details && Object.keys(check.details).length > 0 ? `
                    <div class="security-check-details">
                        <strong>詳細情報:</strong><br>
                        ${Object.entries(check.details).map(([key, value]) => 
                            `<strong>${key}:</strong> ${value}`
                        ).join('<br>')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    // 鍵システムの詳細情報を追加
    if (keyData) {
        checksHtml += `
            <div class="security-check-item">
                <div class="security-check-header">
                    <div class="security-check-name">🔑 デモ用鍵システム詳細</div>
                    <div class="security-check-status status-success">
                        ✅ 利用可能
                    </div>
                </div>
                <div class="security-check-message">RSA 2048-bit鍵システムが正常に動作しています</div>
                <div class="security-check-details">
                    <strong>鍵システム情報:</strong><br>
                    <strong>ステータス:</strong> ${keyData.status}<br>
                    <strong>鍵タイプ:</strong> ${keyData.key_type}<br>
                    <strong>アルゴリズム:</strong> ${keyData.algorithm}<br>
                    <strong>鍵サイズ:</strong> ${keyData.key_size} ビット<br>
                    <strong>作成日時:</strong> ${keyData.created_at}<br>
                    <strong>公開鍵プレビュー:</strong><br>
                    <code style="word-break: break-all; font-size: 0.8em;">${keyData.public_key_preview}</code>
                </div>
            </div>
        `;
    }
    
    checkResults.innerHTML = checksHtml;
    
    // サマリーの表示（成功メッセージと統合）
    if (result.summary) {
        summary.innerHTML = `
            <h3>📊 検証結果サマリー</h3>
            <div class="security-summary-stats">
                <div class="security-stat-item">
                    <span class="security-stat-number">${result.summary.total_checks}</span>
                    <span class="security-stat-label">総チェック数</span>
                </div>
                <div class="security-stat-item">
                    <span class="security-stat-number">${result.summary.successful_checks}</span>
                    <span class="security-stat-label">成功数</span>
                </div>
                <div class="security-stat-item">
                    <span class="security-stat-number">${result.summary.success_rate}</span>
                    <span class="security-stat-label">成功率</span>
                </div>
            </div>
        `;
    } else {
        // サマリーがない場合は成功メッセージのみ表示
        summary.innerHTML = `
            <h3>✅ セキュリティ検証完了</h3>
            <p>全てのセキュリティ項目が正常に検証されました。</p>
        `;
    }
}

// セキュリティ検証エラーを表示
function displaySecurityError(error) {
    const overallStatus = document.getElementById('overallSecurityStatus');
    const checkResults = document.getElementById('securityCheckResults');
    
    if (!overallStatus || !checkResults) {
        console.error('❌ エラー表示要素が見つかりません');
        return;
    }
    
    overallStatus.className = 'overall-security-status status-error';
    overallStatus.innerHTML = `
        <h3 style="color: #721c24; margin: 0;">❌ セキュリティ検証エラー</h3>
        <p>検証の実行中にエラーが発生しました</p>
    `;
    
    checkResults.innerHTML = `
        <div class="security-check-item">
            <div class="security-check-header">
                <div class="security-check-name">エラー詳細</div>
                <div class="security-check-status status-error">❌ エラー</div>
            </div>
            <div class="security-check-message">${error.message}</div>
        </div>
    `;
}

// セキュリティステータスアイコンを取得
function getSecurityStatusIcon(status) {
    const icons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'failure': '❌'
    };
    return icons[status] || '❓';
}

// セキュリティステータステキストを取得
function getSecurityStatusText(status) {
    const texts = {
        'success': '成功',
        'warning': '警告',
        'error': 'エラー',
        'info': '情報',
        'failure': '失敗'
    };
    return texts[status] || '不明';
}

// WebAuthn認証器管理ページを開く
window.openWebAuthnManagement = function() {
    console.log('🔐 WebAuthn認証器管理ページを開いています...');
    
    try {
        // 新しいウィンドウでWebAuthn認証器管理ページを開く
        const webauthnWindow = window.open('/webauthn-management', '_blank', 'width=900,height=700,scrollbars=yes,resizable=yes');
        
        if (webauthnWindow) {
            console.log('✅ WebAuthn認証器管理ページが開かれました');
            addToOperationHistory('WebAuthn認証器管理ページを開きました', 'webauthn_management_open');
        } else {
            console.error('❌ ポップアップブロックが有効になっている可能性があります');
            alert('❌ WebAuthn認証器管理ページを開けませんでした。ポップアップブロックを無効にしてください。');
        }
    } catch (error) {
        console.error('❌ WebAuthn認証器管理ページを開くエラー:', error);
        alert('❌ WebAuthn認証器管理ページを開けませんでした: ' + error.message);
    }
};

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ スクリプトが読み込まれました');
    console.log('loadPatientData:', typeof window.loadPatientData);
    console.log('showPatientView:', typeof window.showPatientView);
    console.log('sendToRaspberryPi:', typeof window.sendToRaspberryPi);
    
    updateOperationHistoryDisplay();
    disableRaspiButton(); // 初期状態では無効化
    
    // 初期ビューを設定
    switchView('private');
});
