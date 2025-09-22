// Google Translate Widget（完全無料）

function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'ja',
        includedLanguages: 'en,zh,ko,vi,th,pt,es,fr',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// 患者ビュー用の翻訳ボタンを追加
function addGoogleTranslateButton() {
    const patientView = document.getElementById('patient-view');
    if (!patientView) return;
    
    // Google翻訳ウィジェット用のdivを追加
    const translateDiv = document.createElement('div');
    translateDiv.id = 'google_translate_element';
    translateDiv.style.cssText = `
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 1000;
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(translateDiv);
    
    // Google翻訳スクリプトを動的に読み込み
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    document.getElementsByTagName('head')[0].appendChild(script);
}

// 患者ビューが表示されたときに翻訳ボタンを追加
document.addEventListener('DOMContentLoaded', function() {
    // 患者ロールの場合のみGoogle翻訳を有効化
    const userRole = document.body.getAttribute('data-user-role');
    if (userRole === 'patient') {
        setTimeout(addGoogleTranslateButton, 1000);
    }
});
