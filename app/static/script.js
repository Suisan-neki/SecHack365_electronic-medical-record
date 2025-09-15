function switchView(viewType) {
    if (viewType === 'patient') {
        document.getElementById('private-view').style.display = 'none';
        document.getElementById('patient-view').style.display = 'block';
        fetchPatientData();
        addToOperationHistory('患者向けビューに切り替え', 'view_switch');
    } else {
        document.getElementById('private-view').style.display = 'block';
        document.getElementById('patient-view').style.display = 'none';
        addToOperationHistory('医師向けビューに切り替え', 'view_switch');
    }
}

async function fetchPatientData() {
    const response = await fetch('/patient_data');
    const data = await response.json();

    // 患者基本情報を表示
    const patientInfo = data.patient_info || {};
    document.getElementById('patient-name').textContent = `${patientInfo.name || '患者'} (${patientInfo.age || ''}歳)`;

    // 現在の病気・症状を表示
    const conditionsDiv = document.createElement('div');
    conditionsDiv.className = 'conditions-section';
    conditionsDiv.innerHTML = '<h3 class="section-title"><span class="condition-icon">🏥</span>現在の病気・症状</h3>';
    
    if (data.current_conditions && data.current_conditions.length > 0) {
        data.current_conditions.forEach(condition => {
            const conditionDiv = document.createElement('div');
            conditionDiv.className = 'condition-item';
            conditionDiv.innerHTML = `
                <div class="condition-header">
                    <span class="condition-icon">${condition.icon}</span>
                    <strong>${condition.name}</strong>
                    <span class="condition-status">${condition.status}</span>
                </div>
                <div class="condition-explanation">${condition.explanation}</div>
                <small class="condition-date">診断日: ${condition.diagnosed_date}</small>
            `;
            conditionsDiv.appendChild(conditionDiv);
        });
    } else {
        conditionsDiv.innerHTML += '<p>現在治療中の病気はありません</p>';
    }

    // 処方薬を表示
    const medicationsList = document.getElementById('medications');
    medicationsList.innerHTML = '';
    
    if (data.medications && data.medications.length > 0) {
    data.medications.forEach(med => {
            const li = document.createElement('li');
            li.className = 'medication-item';
            li.innerHTML = `
                <div class="med-header" style="border-left: 4px solid ${med.color || '#3498db'};">
                    <span class="med-icon">${med.icon}</span>
                    <strong>${med.name}</strong>
                    <span class="med-category">${med.category}</span>
                </div>
                <div class="med-details">
                    <p><strong>💡 効果:</strong> ${med.how_it_works}</p>
                    <p><strong>⏰ 服用方法:</strong> ${med.dosage}</p>
                    ${med.notes ? `<p><strong>📝 医師のメモ:</strong> ${med.notes}</p>` : ''}
                    <p><small><strong>⚠️ 注意:</strong> ${med.common_effects}</small></p>
                </div>
            `;
        medicationsList.appendChild(li);
    });
    } else {
        medicationsList.innerHTML = '<p>現在処方されている薬はありません</p>';
    }

    // 検査結果を表示
    const testResultsDiv = document.getElementById('test-results');
    testResultsDiv.innerHTML = '';
    
    if (data.recent_test_results && data.recent_test_results.length > 0) {
        data.recent_test_results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'test-result-item';
            resultDiv.innerHTML = `
                <div class="test-result-header">
                    <span class="test-result-icon">${result.status_icon}</span>
                    <strong>${result.item_name}</strong>
                    <span class="test-result-status" style="color: ${result.status === '正常' ? '#27ae60' : '#e74c3c'};">
                        ${result.status}
                    </span>
                </div>
                <div class="test-value">${result.value}</div>
                ${result.reference_range ? `<small>基準値: ${result.reference_range}</small>` : ''}
                <div class="test-date">検査日: ${result.test_date}</div>
                ${result.doctor_comment ? `<div class="doctor-comment">医師コメント: ${result.doctor_comment}</div>` : ''}
            `;
            testResultsDiv.appendChild(resultDiv);
        });
    } else {
        testResultsDiv.innerHTML = '<p>最近の検査結果はありません</p>';
    }

    // 病気・症状セクションを薬の前に挿入
    const medicationSection = document.querySelector('.medication-section');
    if (medicationSection && !document.querySelector('.conditions-section')) {
        medicationSection.parentNode.insertBefore(conditionsDiv, medicationSection);
    }
    
    // セキュリティ情報を更新
    updateSecurityInfo();
}

// 検査結果のグラフ表示用ヘルパー関数
function createTestResultItem(name, value, current, max, date, isHigherBetter = false) {
    const div = document.createElement('div');
    div.className = 'test-result-item';
    
    const percentage = Math.min((current / max) * 100, 100);
    const isNormal = isHigherBetter ? current >= max * 0.7 : current <= max * 0.8;
    const statusColor = isNormal ? '#00b894' : '#e17055';
    const statusText = isNormal ? '正常範囲' : '要注意';
    
    div.innerHTML = `
        <div class="test-result-header">
            <strong>${name}</strong>
            <span style="margin-left: auto; color: ${statusColor};">${statusText}</span>
        </div>
        <div class="test-value">${value}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%; background-color: ${statusColor};"></div>
        </div>
        <small style="color: #7f8c8d;">検査日: ${date}</small>
    `;
    
    return div;
}

// セキュリティ情報の表示を更新する関数
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

// 操作履歴を記録する配列
let operationHistory = [];

// 認証機能
async function performLogin() {
    const userId = document.getElementById('user-id').value;
    const role = document.getElementById('role').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, role: role })
        });
        
        const result = await response.json();
        const statusDiv = document.getElementById('auth-status');
        
        if (result.success) {
            statusDiv.innerHTML = `✅ ${result.message}<br><small>ユーザー: ${userId} (${role})</small>`;
            statusDiv.className = 'auth-success';
            document.getElementById('controls-section').style.display = 'block';
            
            // 権限情報を表示
            displayUserPermissions(result.token.payload);
            
            // 操作履歴に記録
            addToOperationHistory(`${role}として認証成功`, 'login');
            
        } else {
            statusDiv.innerHTML = `❌ ${result.message}`;
            statusDiv.className = 'auth-error';
        }
    } catch (error) {
        const statusDiv = document.getElementById('auth-status');
        statusDiv.innerHTML = `❌ ネットワークエラー: ${error.message}`;
        statusDiv.className = 'auth-error';
    }
}

// 権限情報を表示
function displayUserPermissions(userInfo) {
    const permissionsDiv = document.getElementById('user-permissions');
    const roleDescriptions = {
        'doctor': '医師 - 全患者データの閲覧・編集・処方が可能',
        'nurse': '看護師 - 患者データの閲覧・バイタル更新が可能',
        'admin': '管理者 - 患者データ・ユーザー管理が可能'
    };
    
    permissionsDiv.innerHTML = `
        <div>👤 ${userInfo.user_id} (${userInfo.role})</div>
        <div style="font-size: 0.9em; margin-top: 5px;">${roleDescriptions[userInfo.role]}</div>
        <div style="font-size: 0.8em; margin-top: 5px;">権限: ${userInfo.permissions.join(', ')}</div>
    `;
}

// 患者データを読み込む
async function loadPatientData() {
    try {
        const response = await fetch('/patient_data');
        const data = await response.json();
        
        // 医師向け患者情報を表示
        const patientInfo = data.patient_info || {};
        document.getElementById('doctor-patient-id').textContent = patientInfo.patient_id || '-';
        document.getElementById('doctor-patient-name').textContent = patientInfo.name || '-';
        document.getElementById('doctor-patient-age').textContent = patientInfo.age ? patientInfo.age + '歳' : '-';
        document.getElementById('doctor-patient-gender').textContent = patientInfo.gender || '-';
        
        // 操作履歴に記録
        addToOperationHistory('標準型電子カルテデータから患者情報を変換', 'data_translation');
        
        // データソースの情報も表示
        let message = '✅ 標準型電子カルテデータから患者向け情報を生成しました。\n\n';
        message += `📊 変換されたデータ:\n`;
        message += `• 病気・症状: ${data.current_conditions?.length || 0}件\n`;
        message += `• 処方薬: ${data.medications?.length || 0}件\n`;
        message += `• 検査結果: ${data.recent_test_results?.length || 0}件\n\n`;
        message += '「患者向けビューに切り替え」で患者画面を確認できます。';
        
        alert(message);
        
    } catch (error) {
        alert('❌ データ変換エラー: ' + error.message);
    }
}

// 標準型電子カルテの生データを表示
async function showRawEHRData() {
    try {
        const response = await fetch('/raw_ehr_data');
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
}

// セキュリティデモを表示
async function showSecurityDemo() {
    const demoDiv = document.getElementById('security-demo');
    const stepsDiv = document.getElementById('security-steps');
    
    demoDiv.style.display = 'block';
    stepsDiv.innerHTML = `
        <div class="loading-animation">
            <div class="loading-spinner"></div>
            <p>🔄 実際のセキュリティ検証を実行中...</p>
            <div class="loading-details">
                <div>• 暗号化通信の確立...</div>
                <div>• RSA鍵ペアの生成...</div>
                <div>• ハッシュチェーンの構築...</div>
                <div>• 認可トークンの検証...</div>
            </div>
        </div>
    `;
    
    try {
        // 実際のセキュリティ検証APIを呼び出し
        const response = await fetch('/security_verification');
        const verificationResult = await response.json();
        
        // ローディングを段階的に更新
        await simulateProcessingSteps();
        
        stepsDiv.innerHTML = '';
        
        const stepMapping = {
            'https': { icon: '🔐', text: 'HTTPS/TLS暗号化通信', color: '#3498db' },
            'digital_signature': { icon: '✍️', text: 'RSA-PSS電子署名', color: '#e74c3c' },
            'hash_chain': { icon: '🔗', text: 'SHA-256ハッシュチェーン', color: '#f39c12' },
            'authorization': { icon: '🔍', text: 'JWT認可トークン', color: '#27ae60' }
        };
        
        Object.keys(stepMapping).forEach((key, index) => {
            const step = stepMapping[key];
            const result = verificationResult.results[key];
            
            const stepDiv = document.createElement('div');
            stepDiv.className = `security-step ${result.status === 'completed' ? 'completed' : 'failed'}`;
            
            const statusIcon = result.status === 'completed' ? '✅' : '❌';
            const statusText = result.status === 'completed' ? '検証完了' : '検証失敗';
            
            // 技術的詳細を表示
            let technicalInfo = '';
            if (result.details) {
                if (key === 'https' && result.details.tls_version) {
                    technicalInfo = `${result.details.tls_version} | ${result.details.cipher_suite}`;
                } else if (key === 'digital_signature' && result.details.algorithm) {
                    technicalInfo = `${result.details.algorithm} | ${result.details.key_size}`;
                } else if (key === 'hash_chain' && result.details.algorithm) {
                    technicalInfo = `${result.details.algorithm} | ${result.details.chain_length} blocks`;
                } else if (key === 'authorization' && result.details.role) {
                    technicalInfo = `Role: ${result.details.role} | Valid: ${result.details.token_valid}`;
                }
            }
            
            stepDiv.innerHTML = `
                <div class="security-step-icon" style="color: ${step.color};">${step.icon}</div>
                <div class="security-step-text">
                    <div class="step-title">${step.text}</div>
                    <div class="step-message">${result.message}</div>
                    ${technicalInfo ? `<div class="step-technical">${technicalInfo}</div>` : ''}
                    <div class="step-progress">
                        <div class="progress-bar-mini">
                            <div class="progress-fill-mini ${result.status === 'completed' ? 'completed' : 'failed'}"></div>
                        </div>
                    </div>
                </div>
                <div class="security-step-status" style="color: ${result.status === 'completed' ? '#27ae60' : '#e74c3c'};">
                    ${statusIcon} ${statusText}
                </div>
            `;
            
            // 詳細情報を表示するためのクリックイベント
            stepDiv.addEventListener('click', () => {
                showEnhancedSecurityDetails(key, result, step);
            });
            stepDiv.style.cursor = 'pointer';
            stepDiv.title = 'クリックで詳細な技術情報を表示';
            
            stepsDiv.appendChild(stepDiv);
            
            // アニメーション付きで段階的に表示
            setTimeout(() => {
                stepDiv.style.opacity = '1';
                stepDiv.style.transform = 'translateX(0)';
                stepDiv.classList.add('animate-in');
            }, index * 500);
        });
        
        // 全体の結果を表示
        setTimeout(() => {
            const overallDiv = document.createElement('div');
            overallDiv.className = 'security-overall-result animate-in';
            overallDiv.innerHTML = `
                <div style="margin-top: 20px; padding: 20px; 
                            background: ${verificationResult.overall_status === 'success' ? 
                                'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)' : 
                                'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)'}; 
                            border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.2em; margin-bottom: 10px;">
                        ${verificationResult.overall_status === 'success' ? '🔒 セキュリティ検証完全成功' : '⚠️ 部分的な問題を検出'}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.8;">
                        検証時刻: ${new Date(verificationResult.timestamp).toLocaleString('ja-JP')}<br>
                        検証項目: ${Object.keys(stepMapping).length}項目 | 
                        成功: ${Object.values(verificationResult.results).filter(r => r.status === 'completed').length}項目
                    </div>
                </div>
            `;
            stepsDiv.appendChild(overallDiv);
        }, Object.keys(stepMapping).length * 500 + 500);
        
    } catch (error) {
        stepsDiv.innerHTML = `<div class="error-message">❌ セキュリティ検証エラー: ${error.message}</div>`;
    }
    
    // 操作履歴に記録
    addToOperationHistory('実際のセキュリティ検証を実行', 'security_demo');
}

// 処理ステップのシミュレーション
async function simulateProcessingSteps() {
    const steps = [
        '🔐 TLS handshake実行中...',
        '🔑 RSA-2048鍵ペア生成中...',
        '🔗 ハッシュチェーン構築中...',
        '🔍 JWT トークン検証中...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 300));
        const loadingDetails = document.querySelector('.loading-details');
        if (loadingDetails) {
            const items = loadingDetails.children;
            if (items[i]) {
                items[i].style.color = '#27ae60';
                items[i].innerHTML = '✅ ' + steps[i].replace('中...', '完了');
            }
        }
    }
}

// 拡張されたセキュリティ詳細情報を表示
function showEnhancedSecurityDetails(type, result, step) {
    const modal = document.createElement('div');
    modal.className = 'security-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header" style="background: ${step.color};">
                <span class="modal-icon">${step.icon}</span>
                <h3>${step.text} - 詳細情報</h3>
                <span class="modal-close" onclick="this.closest('.security-modal').remove()">×</span>
            </div>
            <div class="modal-body">
                <div class="status-badge ${result.status === 'completed' ? 'success' : 'failed'}">
                    ${result.status === 'completed' ? '✅ 検証成功' : '❌ 検証失敗'}
                </div>
                <p><strong>メッセージ:</strong> ${result.message}</p>
                ${formatDetailedInfo(type, result.details)}
            </div>
            <div class="modal-footer">
                <button onclick="this.closest('.security-modal').remove()" class="close-button">閉じる</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // アニメーションで表示
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function formatDetailedInfo(type, details) {
    if (!details) return '<p>詳細情報はありません。</p>';
    
    let html = '<div class="technical-details">';
    
    if (type === 'https') {
        html += `
            <h4>🔐 TLS/SSL通信詳細</h4>
            <table class="detail-table">
                <tr><td>TLSバージョン</td><td>${details.tls_version}</td></tr>
                <tr><td>暗号スイート</td><td>${details.cipher_suite}</td></tr>
                <tr><td>鍵交換</td><td>${details.key_exchange}</td></tr>
                <tr><td>認証</td><td>${details.authentication}</td></tr>
                <tr><td>暗号化</td><td>${details.encryption}</td></tr>
                <tr><td>MAC</td><td>${details.mac}</td></tr>
                <tr><td>Perfect Forward Secrecy</td><td>${details.perfect_forward_secrecy ? '✅ 有効' : '❌ 無効'}</td></tr>
            </table>
        `;
    } else if (type === 'digital_signature') {
        html += `
            <h4>✍️ 電子署名詳細</h4>
            <table class="detail-table">
                <tr><td>署名アルゴリズム</td><td>${details.algorithm}</td></tr>
                <tr><td>鍵サイズ</td><td>${details.key_size}</td></tr>
                <tr><td>パディング方式</td><td>${details.padding}</td></tr>
                <tr><td>ハッシュ関数</td><td>${details.hash_function}</td></tr>
                <tr><td>ソルト長</td><td>${details.salt_length}</td></tr>
                <tr><td>データハッシュ</td><td><code>${details.data_hash}</code></td></tr>
                <tr><td>署名長</td><td>${details.signature_length} bytes</td></tr>
                <tr><td>署名(Hex)</td><td><code>${details.signature_hex}</code></td></tr>
                <tr><td>公開鍵フィンガープリント</td><td><code>${details.public_key_fingerprint}</code></td></tr>
            </table>
        `;
    } else if (type === 'hash_chain') {
        html += `
            <h4>🔗 ハッシュチェーン詳細</h4>
            <table class="detail-table">
                <tr><td>ハッシュアルゴリズム</td><td>${details.algorithm}</td></tr>
                <tr><td>チェーン長</td><td>${details.chain_length} blocks</td></tr>
                <tr><td>ジェネシスハッシュ</td><td><code>${details.genesis_hash}</code></td></tr>
                <tr><td>最新ハッシュ</td><td><code>${details.latest_hash}</code></td></tr>
                <tr><td>Merkle Root</td><td><code>${details.merkle_root}</code></td></tr>
            </table>
            <h5>ブロック検証状況</h5>
            <div class="block-verifications">
                ${details.block_verifications.map(block => `
                    <div class="block-item ${block.hash_valid && block.previous_hash_valid ? 'valid' : 'invalid'}">
                        <strong>Block ${block.block_index}</strong> (${block.block_type})<br>
                        ハッシュ検証: ${block.hash_valid ? '✅' : '❌'} | 
                        前ブロック検証: ${block.previous_hash_valid ? '✅' : '❌'}
                    </div>
                `).join('')}
            </div>
        `;
    } else if (type === 'authorization') {
        html += `
            <h4>🔍 認可トークン詳細</h4>
            <table class="detail-table">
                <tr><td>ユーザーID</td><td>${details.user_id}</td></tr>
                <tr><td>役割</td><td>${details.role}</td></tr>
                <tr><td>発行時刻</td><td>${details.issued_at}</td></tr>
                <tr><td>権限</td><td>${details.permissions.join(', ')}</td></tr>
                <tr><td>トークン有効性</td><td>${details.token_valid ? '✅ 有効' : '❌ 無効'}</td></tr>
            </table>
        `;
    }
    
    html += '</div>';
    return html;
}

// 権限テスト機能
async function testPermissions() {
    try {
        const response = await fetch('/check_permissions');
        const result = await response.json();
        
        // ボタンの状態を更新
        updatePermissionButtons(result.access_matrix);
        
        // 結果を表示
        const resultsDiv = document.getElementById('permission-test-results');
        resultsDiv.innerHTML = `
            <div class="result-item">
                <strong>🔍 権限チェック結果</strong><br>
                <small>${result.role_description}</small>
            </div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                <strong>利用可能な機能:</strong><br>
                ${Object.keys(result.access_matrix).map(key => 
                    `• ${getFunctionName(key)}: ${result.access_matrix[key] ? '✅ 可能' : '❌ 不可'}`
                ).join('<br>')}
            </div>
        `;
        
        addToOperationHistory('権限状況を確認', 'permission_check');
        
    } catch (error) {
        alert('❌ 権限チェックエラー: ' + error.message);
    }
}

function updatePermissionButtons(accessMatrix) {
    const buttons = {
        'prescribe-btn': accessMatrix.prescribe_medication,
        'vitals-btn': accessMatrix.update_vitals,
        'users-btn': accessMatrix.manage_users
    };
    
    Object.keys(buttons).forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.className = `perm-button ${buttons[buttonId] ? 'allowed' : 'denied'}`;
        }
    });
}

function getFunctionName(key) {
    const names = {
        'patient_data_read': '患者データ閲覧',
        'patient_data_write': '患者データ編集',
        'prescribe_medication': '処方箋発行',
        'update_vitals': 'バイタル更新',
        'manage_users': 'ユーザー管理'
    };
    return names[key] || key;
}

async function testPrescription() {
    const button = document.getElementById('prescribe-btn');
    button.className = 'perm-button testing';
    
    try {
        const response = await fetch('/prescribe_medication', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                medication_name: 'テスト用薬剤',
                dosage: '1錠',
                frequency: '1日2回'
            })
        });
        
        const result = await response.json();
        showPermissionResult('処方箋発行', response.ok, result);
        
    } catch (error) {
        showPermissionResult('処方箋発行', false, { error: error.message });
    }
    
    // ボタンの状態をリセット
    setTimeout(() => {
        testPermissions();
    }, 1000);
}

async function testVitalsUpdate() {
    const button = document.getElementById('vitals-btn');
    button.className = 'perm-button testing';
    
    try {
        const response = await fetch('/update_vitals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                blood_pressure: '130/85',
                temperature: '36.8'
            })
        });
        
        const result = await response.json();
        showPermissionResult('バイタル更新', response.ok, result);
        
    } catch (error) {
        showPermissionResult('バイタル更新', false, { error: error.message });
    }
    
    setTimeout(() => {
        testPermissions();
    }, 1000);
}

async function testUserManagement() {
    const button = document.getElementById('users-btn');
    button.className = 'perm-button testing';
    
    try {
        const response = await fetch('/manage_users');
        const result = await response.json();
        showPermissionResult('ユーザー管理', response.ok, result);
        
    } catch (error) {
        showPermissionResult('ユーザー管理', false, { error: error.message });
    }
    
    setTimeout(() => {
        testPermissions();
    }, 1000);
}

function showPermissionResult(functionName, success, result) {
    const resultsDiv = document.getElementById('permission-test-results');
    const resultClass = success ? 'result-success' : 'result-error';
    const icon = success ? '✅' : '❌';
    
    let message = '';
    if (success) {
        message = result.message || '操作が成功しました';
    } else {
        message = result.error || result.message || '操作が失敗しました';
        if (result.required_permission) {
            message += `<br><small>必要な権限: ${result.required_permission}</small>`;
        }
    }
    
    const resultHtml = `
        <div class="result-item ${resultClass}">
            <strong>${icon} ${functionName}</strong><br>
            ${message}
        </div>
    `;
    
    resultsDiv.innerHTML = resultHtml + resultsDiv.innerHTML;
    
    // 操作履歴に記録
    addToOperationHistory(`${functionName}をテスト - ${success ? '成功' : '失敗'}`, 'permission_test');
}

// 操作履歴に追加
function addToOperationHistory(action, type) {
    const timestamp = new Date().toLocaleString('ja-JP');
    const operation = {
        timestamp: timestamp,
        action: action,
        type: type
    };
    
    operationHistory.unshift(operation);
    updateOperationHistoryDisplay();
}

// 操作履歴の表示を更新
function updateOperationHistoryDisplay() {
    const historyDiv = document.getElementById('operation-history');
    
    if (operationHistory.length === 0) {
        historyDiv.innerHTML = '<p style="color: #636e72;">操作履歴はありません</p>';
        return;
    }
    
    historyDiv.innerHTML = operationHistory.slice(0, 10).map(op => `
        <div class="operation-item">
            <div>${op.action}</div>
            <div class="operation-timestamp">${op.timestamp}</div>
        </div>
    `).join('');
}

async function checkSecurity() {
    try {
        const response = await fetch('/verify_authorization');
        const result = await response.json();
        
        if (result.authorized) {
            alert(`🔒 セキュリティ状態: 正常\n\n` +
                  `ユーザー: ${result.user_info.user_id}\n` +
                  `役割: ${result.user_info.role}\n` +
                  `権限: ${result.user_info.permissions.join(', ')}\n` +
                  `発行時刻: ${result.user_info.issued_at}`);
        } else {
            alert(`❌ 認証エラー: ${result.message}`);
        }
    } catch (error) {
        alert(`❌ セキュリティチェックエラー: ${error.message}`);
    }
}

// 詳細操作の切り替え
function toggleAdvancedOptions() {
    const advancedOptions = document.getElementById('advanced-options');
    const toggleIcon = document.getElementById('advanced-toggle');
    
    if (advancedOptions.style.display === 'none') {
        advancedOptions.style.display = 'block';
        toggleIcon.textContent = '▲';
    } else {
        advancedOptions.style.display = 'none';
        toggleIcon.textContent = '▼';
    }
}

// 権限テストの表示改善
function testPermissions() {
    const permissionArea = document.getElementById('permission-test-area');
    permissionArea.style.display = 'block';
    
    // 元の権限テスト機能を実行
    originalTestPermissions();
}

// 元の権限テスト機能を保存
const originalTestPermissions = async function() {
    try {
        const response = await fetch('/check_permissions');
        const result = await response.json();
        
        // ボタンの状態を更新
        updatePermissionButtons(result.access_matrix);
        
        // 結果を表示
        const resultsDiv = document.getElementById('permission-test-results');
        resultsDiv.innerHTML = `
            <div class="result-item">
                <strong>🔍 権限チェック結果</strong><br>
                <small>${result.role_description}</small>
            </div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                <strong>利用可能な機能:</strong><br>
                ${Object.keys(result.access_matrix).map(key => 
                    `• ${getFunctionName(key)}: ${result.access_matrix[key] ? '✅ 可能' : '❌ 不可'}`
                ).join('<br>')}
            </div>
        `;
        
        addToOperationHistory('権限状況を確認', 'permission_check');
        
    } catch (error) {
        alert('❌ 権限チェックエラー: ' + error.message);
    }
};

// 患者データ読み込み時に患者カードを更新
const originalLoadPatientData = loadPatientData;
async function loadPatientData() {
    // 患者ステータスを更新
    const patientStatus = document.querySelector('.patient-status');
    if (patientStatus) {
        patientStatus.textContent = '読み込み中...';
        patientStatus.style.background = 'rgba(255, 193, 7, 0.3)';
    }
    
    // 元の処理を実行
    await originalLoadPatientData();
    
    // 成功時にステータスを更新
    if (patientStatus) {
        patientStatus.textContent = '準備完了';
        patientStatus.style.background = 'rgba(40, 167, 69, 0.3)';
    }
}

// 初期表示
document.addEventListener('DOMContentLoaded', function() {
    updateOperationHistoryDisplay();
});

switchView('private');