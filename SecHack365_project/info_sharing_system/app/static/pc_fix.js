
// ラズパイ表示ボタンの強制有効化
function forceEnableRaspiButton() {
    const raspiBtn = document.getElementById('raspi-display-btn');
    if (raspiBtn) {
        raspiBtn.disabled = false;
        raspiBtn.classList.remove('disabled');
        raspiBtn.style.background = '#e67e22';
        raspiBtn.style.opacity = '1';
        raspiBtn.style.cursor = 'pointer';
        console.log('✅ ラズパイ表示ボタンを強制有効化しました');
        return true;
    } else {
        console.log('❌ ラズパイ表示ボタンが見つかりません');
        return false;
    }
}

// 患者IDを強制設定
function forceSetPatientId() {
    // 簡易的に患者IDを設定
    window.currentPatientId = 'patient_001';
    console.log('✅ 患者IDを強制設定しました: patient_001');
}

// sendToRaspberryPi関数の修正版
async function fixedSendToRaspberryPi() {
    console.log('🍓 修正版ラズパイ送信関数を実行します');
    
    const raspiBtn = document.getElementById('raspi-display-btn');
    if (!raspiBtn) {
        alert('ラズパイ表示ボタンが見つかりません');
        return;
    }
    
    const originalHTML = raspiBtn.innerHTML;
    
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
                patient_id: 'patient_001'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('✅ API送信成功:', result);
        
        // 成功時の表示
        raspiBtn.innerHTML = `
            <span class="button-icon">✅</span>
            <span class="button-text">
                <strong>送信完了</strong>
                <small>ラズパイで表示中</small>
            </span>
        `;
        
        alert('✅ ラズパイへの送信が完了しました！');
        
        // 3秒後にボタンを元に戻す
        setTimeout(() => {
            raspiBtn.innerHTML = originalHTML;
            raspiBtn.disabled = false;
        }, 3000);
        
    } catch (error) {
        console.error('❌ ラズパイ送信エラー:', error);
        
        // エラー時の表示
        raspiBtn.innerHTML = `
            <span class="button-icon">❌</span>
            <span class="button-text">
                <strong>送信失敗</strong>
                <small>エラーが発生しました</small>
            </span>
        `;
        
        alert('❌ ラズパイへの送信に失敗しました: ' + error.message);
        
        // 3秒後にボタンを元に戻す
        setTimeout(() => {
            raspiBtn.innerHTML = originalHTML;
            raspiBtn.disabled = false;
        }, 3000);
    }
}

// 自動修正実行
console.log('🔧 PC側自動修正スクリプトを実行中...');
forceSetPatientId();
forceEnableRaspiButton();

// ボタンクリックイベントを再設定
const raspiBtn = document.getElementById('raspi-display-btn');
if (raspiBtn) {
    raspiBtn.onclick = fixedSendToRaspberryPi;
    console.log('✅ ボタンクリックイベントを修正版に変更しました');
}

console.log('🍓 PC側修正完了！「ラズパイに表示」ボタンをクリックしてください。');
