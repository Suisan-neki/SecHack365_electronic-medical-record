// ========================================
// 患者ポータル用JavaScript
// ========================================

// グローバル変数
let currentLanguage = 'ja';
let currentInfoLevel = 'simple';

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('患者ポータルが読み込まれました');
    initializePatientPortal();
});

// 患者ポータルの初期化
function initializePatientPortal() {
    // 言語設定の復元
    const savedLanguage = localStorage.getItem('patient_portal_language');
    if (savedLanguage) {
        changeLanguage(savedLanguage);
    }
    
    // 表示レベル設定の復元
    const savedInfoLevel = localStorage.getItem('patient_portal_info_level');
    if (savedInfoLevel) {
        changeInfoLevel(savedInfoLevel);
    }
    
    // 同意設定の変更イベントリスナーを設定
    setupConsentListeners();
    
    // 質問フォームのバリデーション設定
    setupQuestionFormValidation();
}

// 言語変更機能
function changeLanguage(language) {
    currentLanguage = language;
    localStorage.setItem('patient_portal_language', language);
    
    // 言語に応じたテキストの変更
    const translations = {
        'ja': {
            'title': '患者ポータル',
            'consent_title': '情報共有の同意設定',
            'medical_info_title': 'あなたの医療情報',
            'questions_title': '医師への質問・相談',
            'simple_view': 'わかりやすい表示',
            'detailed_view': '詳細表示',
            'ask_question': '質問する',
            'download_record': '記録をダウンロード',
            'submit_question': '質問を送信',
            'question_placeholder': '気になることや質問があれば、お気軽にお書きください...',
            'urgent_question': '緊急を要する質問',
            'family_notification': '家族にも回答を共有する'
        },
        'en': {
            'title': 'Patient Portal',
            'consent_title': 'Information Sharing Consent',
            'medical_info_title': 'Your Medical Information',
            'questions_title': 'Questions & Consultations',
            'simple_view': 'Simple View',
            'detailed_view': 'Detailed View',
            'ask_question': 'Ask Question',
            'download_record': 'Download Record',
            'submit_question': 'Submit Question',
            'question_placeholder': 'Please feel free to write any questions or concerns...',
            'urgent_question': 'Urgent Question',
            'family_notification': 'Share response with family'
        }
    };
    
    const t = translations[language] || translations['ja'];
    
    // テキストの更新
    document.querySelector('h1').textContent = t.title;
    document.querySelector('.consent-section h3').textContent = t.consent_title;
    document.querySelector('.medical-info-section h3').textContent = t.medical_info_title;
    document.querySelector('.questions-section h3').textContent = t.questions_title;
    
    // ラジオボタンのラベル更新
    const simpleLabel = document.querySelector('input[value="simple"]').nextSibling;
    const detailedLabel = document.querySelector('input[value="detailed"]').nextSibling;
    if (simpleLabel) simpleLabel.textContent = t.simple_view;
    if (detailedLabel) detailedLabel.textContent = t.detailed_view;
    
    // テキストエリアのプレースホルダー更新
    const questionTextarea = document.getElementById('question-text');
    if (questionTextarea) {
        questionTextarea.placeholder = t.question_placeholder;
    }
    
    console.log(`言語を ${language} に変更しました`);
}

// 情報表示レベルの変更
function changeInfoLevel(level) {
    currentInfoLevel = level;
    localStorage.setItem('patient_portal_info_level', level);
    
    // ラジオボタンの状態を更新
    document.querySelector(`input[value="${level}"]`).checked = true;
    
    // 表示/非表示の切り替え
    const simpleElements = document.querySelectorAll('.simple-text');
    const detailedElements = document.querySelectorAll('.detailed-text');
    
    if (level === 'simple') {
        simpleElements.forEach(el => el.style.display = 'block');
        detailedElements.forEach(el => el.style.display = 'none');
    } else {
        simpleElements.forEach(el => el.style.display = 'none');
        detailedElements.forEach(el => el.style.display = 'block');
    }
    
    console.log(`表示レベルを ${level} に変更しました`);
}

// 同意設定の更新
function updateConsent(consentType, isGranted) {
    console.log(`同意設定を更新: ${consentType} = ${isGranted}`);
    
    // サーバーに同意設定を送信
    fetch('/api/patient/consent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            consent_type: consentType,
            consent_given: isGranted,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('同意設定が正常に更新されました');
            
            // 詳細情報の表示/非表示を切り替え
            if (consentType === 'family_sharing') {
                const details = document.getElementById('family-details');
                if (details) {
                    details.style.display = isGranted ? 'block' : 'none';
                }
            }
            
            // 成功メッセージを表示
            showNotification('同意設定が更新されました', 'success');
        } else {
            console.error('同意設定の更新に失敗しました:', data.error);
            showNotification('同意設定の更新に失敗しました', 'error');
        }
    })
    .catch(error => {
        console.error('同意設定の更新中にエラーが発生しました:', error);
        showNotification('エラーが発生しました。もう一度お試しください。', 'error');
    });
}

// 同意設定のイベントリスナー設定
function setupConsentListeners() {
    const consentToggles = document.querySelectorAll('.consent-toggle input[type="checkbox"]');
    consentToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const consentType = this.id.replace('-sharing', '_sharing');
            updateConsent(consentType, this.checked);
        });
    });
}

// 質問フォームのバリデーション設定
function setupQuestionFormValidation() {
    const questionTextarea = document.getElementById('question-text');
    const submitBtn = document.querySelector('.submit-question-btn');
    
    if (questionTextarea && submitBtn) {
        questionTextarea.addEventListener('input', function() {
            const hasText = this.value.trim().length > 0;
            submitBtn.disabled = !hasText;
            submitBtn.style.opacity = hasText ? '1' : '0.6';
        });
    }
}

// 質問の送信
function submitQuestion() {
    const questionText = document.getElementById('question-text').value.trim();
    const isUrgent = document.getElementById('urgent-question').checked;
    const shareWithFamily = document.getElementById('family-notification').checked;
    
    if (!questionText) {
        showNotification('質問内容を入力してください', 'warning');
        return;
    }
    
    console.log('質問を送信中...', {
        question: questionText,
        urgent: isUrgent,
        shareWithFamily: shareWithFamily
    });
    
    // サーバーに質問を送信
    fetch('/api/patient/question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: questionText,
            urgent: isUrgent,
            share_with_family: shareWithFamily,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('質問が正常に送信されました');
            showNotification('質問が送信されました。回答をお待ちください。', 'success');
            
            // フォームをリセット
            document.getElementById('question-text').value = '';
            document.getElementById('urgent-question').checked = false;
            document.getElementById('family-notification').checked = false;
        } else {
            console.error('質問の送信に失敗しました:', data.error);
            showNotification('質問の送信に失敗しました', 'error');
        }
    })
    .catch(error => {
        console.error('質問の送信中にエラーが発生しました:', error);
        showNotification('エラーが発生しました。もう一度お試しください。', 'error');
    });
}

// 質問ボタンのクリック
function askQuestion(recordId) {
    console.log(`記録 ${recordId} について質問します`);
    
    // 質問フォームにスクロール
    const questionSection = document.querySelector('.questions-section');
    if (questionSection) {
        questionSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 質問テキストエリアにフォーカス
    const questionTextarea = document.getElementById('question-text');
    if (questionTextarea) {
        questionTextarea.focus();
        questionTextarea.value = `記録ID ${recordId} について質問があります。`;
    }
}

// 記録のダウンロード
function downloadRecord(recordId) {
    console.log(`記録 ${recordId} をダウンロードします`);
    
    // サーバーから記録をダウンロード
    fetch(`/api/patient/record/${recordId}/download`, {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('ダウンロードに失敗しました');
        }
    })
    .then(blob => {
        // ダウンロードリンクを作成
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medical_record_${recordId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('記録をダウンロードしました', 'success');
    })
    .catch(error => {
        console.error('ダウンロード中にエラーが発生しました:', error);
        showNotification('ダウンロードに失敗しました', 'error');
    });
}

// 通知の表示
function showNotification(message, type = 'info') {
    // 既存の通知を削除
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 通知要素を作成
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // スタイルを設定
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        max-width: 300px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        animation: slideIn 0.3s ease;
    `;
    
    // タイプに応じた色を設定
    const colors = {
        'success': '#48bb78',
        'error': '#f56565',
        'warning': '#ed8936',
        'info': '#667eea'
    };
    notification.style.backgroundColor = colors[type] || colors['info'];
    
    // アニメーション用のCSSを追加
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // 通知を表示
    document.body.appendChild(notification);
    
    // 3秒後に自動削除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 3000);
}

// エラーハンドリング
window.addEventListener('error', function(event) {
    console.error('JavaScript エラー:', event.error);
    showNotification('システムエラーが発生しました。ページを再読み込みしてください。', 'error');
});

// 未処理のPromise拒否をキャッチ
window.addEventListener('unhandledrejection', function(event) {
    console.error('未処理のPromise拒否:', event.reason);
    showNotification('通信エラーが発生しました。', 'error');
});
