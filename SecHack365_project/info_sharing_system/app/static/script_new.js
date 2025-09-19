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
    try {
        const response = await fetch('/patient_data');
        if (response.ok) {
            const data = await response.json();
            // 患者データを表示
            displayPatientData(data);
        } else if (response.status === 401) {
            // 認証が必要
            alert('この機能を使用するにはログインが必要です。');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('患者データの読み込みエラー:', error);
    }
}

// 患者データ表示
function displayPatientData(data) {
    if (data.patient_info) {
        document.getElementById('patient-name').textContent = data.patient_info.name || '患者名不明';
    }
    // その他の患者データ表示処理...
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

// 詳細データ読み込み関数（スタブ）
function loadConditionsDetail() {
    console.log('病気・症状の詳細を読み込み中...');
}

function loadMedicationsDetail() {
    console.log('処方薬の詳細を読み込み中...');
}

function loadTestsDetail() {
    console.log('検査結果の詳細を読み込み中...');
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
function showRawEHRData() {
    window.open('/raw_ehr_data', '_blank');
}
