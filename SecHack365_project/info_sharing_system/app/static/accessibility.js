// 患者向けアクセシビリティ機能

class PatientAccessibility {
    constructor() {
        this.isEnabled = false;
        this.currentLanguage = 'ja';
        this.furiganaEnabled = false;
        this.simpleModeEnabled = false;
        this.highContrastEnabled = false;
        
        // わかりやすい言葉の辞書（より自然で親しみやすい表現）
        this.medicalTerms = {
            // 長い語句を優先（部分置換を防ぐ）
            '診療情報': 'からだの記録',
            '現在の病気・症状': '今の病気',
            '診断された病気や症状': '今の病気',
            '処方されている薬': 'もらっている薬',
            '現在処方されている薬の情報': 'もらっている薬について',
            '最新の検査結果と数値': 'からだについて分かったこと',
            'この情報は暗号化により保護されています': 'この情報は安全に守られています',
            '診断された病気や症状を確認': '病気について知る',
            '現在処方されている薬の情報': 'もらっている薬について',
            '最新の検査結果と数値': 'からだについて分かったこと',
            
            // 個別の語句（短い語句は後に配置）
            '処方薬': 'もらった薬',
            '検査結果': 'しらべた結果',
            '診断': '病気を調べること',
            '処方': '薬をもらうこと',
            '症状': '体の調子',
            '治療': '治すこと',
            '検査': 'しらべること',
            '投薬': '薬を飲むこと',
            '血圧': '血の勢い',
            '体温': '体の熱さ',
            '脈拍': '心臓の動き',
            '貧血': '血が足りない',
            '鉄剤': '鉄の薬',
            '診察': '診てもらうこと',
            '注射': '注射',
            '手術': '手術',
            '入院': '病院に入ること',
            '退院': '病院から出ること',
            '外来': '病院に通うこと',
            '救急': '急ぎの治療',
            '暗号化': '安全な仕組み',
            '保護': '守ること',
            '情報': 'お知らせ',
            '確認': '知る'
        };
        
        // 基本的な漢字→ひらがなルビ辞書（画像に表示される全ての語句を網羅）
        this.kanjiRuby = {
            '診療情報': 'しんりょうじょうほう',      // 完全一致
            '山下真凜': 'やましたまりん',          // 完全一致
            '現在の病気・症状': 'げんざいのびょうき・しょうじょう', // 完全一致
            '処方薬': 'しょほうやく',             // 完全一致
            '検査結果': 'けんさけっか',            // 完全一致
            '画面に戻る': 'がめんにもどる',         // 完全一致
            '診療': 'しんりょう',
            '情報': 'じょうほう',
            '現在': 'げんざい',
            '病気': 'びょうき',
            '症状': 'しょうじょう',
            '診断': 'しんだん',
            '確認': 'かくにん',
            '処方': 'しょほう',
            '結果': 'けっか',
            '薬': 'くすり',
            '検査': 'けんさ',
            '最新': 'さいしん',
            '数値': 'すうち',
            '暗号化': 'あんごうか',
            '保護': 'ほご',
            '画面': 'がめん',
            '戻る': 'もどる'
        };
        
        // 多言語辞書（基本的な単語のみ）
        this.translations = {
            'en': {
                '診療情報': 'Medical Information',
                '現在の病気・症状': 'Current Conditions',
                '処方薬': 'Medications',
                '検査結果': 'Test Results',
                'この情報は暗号化により保護されています': 'This information is protected by encryption',
                'メニューに戻る': 'Back to Menu'
            },
            'zh': {
                '診療情報': '诊疗信息',
                '現在の病気・症状': '当前疾病・症状',
                '処方薬': '处方药',
                '検査結果': '检查结果',
                'この情報は暗号化により保護されています': '此信息受加密保护',
                'メニューに戻る': '返回菜单'
            },
            'ko': {
                '診療情報': '진료 정보',
                '現在の病気・症状': '현재 질병・증상',
                '処方薬': '처방약',
                '検査結果': '검사 결과',
                'この情報は暗号化により保護されています': '이 정보는 암호화로 보호됩니다',
                'メニューに戻る': '메뉴로 돌아가기'
            }
        };
        
        this.initializeAccessibility();
    }
    
    initializeAccessibility() {
        // アクセシビリティボタンを追加
        this.createAccessibilityButton();
        
        // 患者ビューが表示されたときの処理
        document.addEventListener('DOMContentLoaded', () => {
            this.checkPatientRole();
        });
    }
    
    createAccessibilityButton() {
        // 患者ロール以外は表示しない
        const userRole = this.getCurrentUserRole();
        console.log('現在のユーザーロール:', userRole);
        
        // 患者ビューが表示されている場合は表示（ロール取得に失敗した場合のフォールバック）
        const patientView = document.getElementById('patient-view');
        const isPatientViewVisible = patientView && patientView.style.display !== 'none';
        
        if (userRole !== 'patient' && !isPatientViewVisible) {
            console.log('患者ロールではないため、アクセシビリティボタンを非表示にします');
            return;
        }
        
        console.log('アクセシビリティボタンを作成します');
        
        // アクセシビリティ切り替えボタン
        const languageButton = document.createElement('button');
        languageButton.className = 'language-selector';
        languageButton.innerHTML = '🌐 変換';
        languageButton.onclick = () => this.toggleAccessibilityPanel();
        
        // アクセシビリティパネル
        const panel = document.createElement('div');
        panel.className = 'accessibility-panel';
        panel.id = 'accessibility-panel';
        panel.innerHTML = `
            <h4>📱 患者向け設定</h4>
            
            <div class="accessibility-option">
                <label>大きな文字</label>
                <div class="toggle-switch" id="large-text-toggle" onclick="accessibility.toggleLargeText()"></div>
            </div>
            
            <div class="accessibility-option">
                <label>ふりがな表示</label>
                <div class="toggle-switch" id="furigana-toggle" onclick="accessibility.toggleFurigana()"></div>
            </div>
            
            <div class="accessibility-option">
                <label>わかりやすい表示</label>
                <div class="toggle-switch" id="simple-mode-toggle" onclick="accessibility.toggleSimpleMode()"></div>
            </div>
            
            <div class="accessibility-option">
                <label>見やすい色</label>
                <div class="toggle-switch" id="high-contrast-toggle" onclick="accessibility.toggleHighContrast()"></div>
            </div>
            
            <hr>
            
            <div class="accessibility-option">
                <label>言語</label>
                <select id="language-select" onchange="accessibility.changeLanguage(this.value)">
                    <option value="ja">日本語</option>
                    <option value="en">English</option>
                    <option value="zh">中文</option>
                    <option value="ko">한국어</option>
                </select>
            </div>
        `;
        
        document.body.appendChild(languageButton);
        document.body.appendChild(panel);
    }
    
    checkPatientRole() {
        // 現在のユーザーが患者の場合、自動で基本的なアクセシビリティを有効化
        const userRole = this.getCurrentUserRole();
        console.log('checkPatientRole - 現在のユーザーロール:', userRole);
        
        if (userRole === 'patient') {
            this.createAccessibilityButton();
            this.enableBasicAccessibility();
        }
        
        // 患者ビューに切り替わったときもボタンを表示するためのリスナーを追加
        this.setupPatientViewListener();
    }
    
    setupPatientViewListener() {
        // switchView関数が呼ばれたときにボタンを作成
        const originalSwitchView = window.switchView;
        if (originalSwitchView) {
            window.switchView = (viewType) => {
                originalSwitchView(viewType);
                if (viewType === 'patient') {
                    console.log('患者ビューに切り替わりました - アクセシビリティボタンを作成');
                    // 既存のボタンがあれば削除
                    const existingButton = document.querySelector('.language-selector');
                    const existingPanel = document.getElementById('accessibility-panel');
                    if (existingButton) existingButton.remove();
                    if (existingPanel) existingPanel.remove();
                    
                    // 新しいボタンを作成
                    this.createAccessibilityButton();
                }
            };
        }
    }
    
    getCurrentUserRole() {
        // HTMLから現在のユーザーロールを取得
        const bodyElement = document.body;
        return bodyElement ? bodyElement.getAttribute('data-user-role') : null;
    }
    
    enableBasicAccessibility() {
        // 患者向けの基本設定を自動適用
        this.toggleLargeText();
        this.toggleSimpleMode();
    }
    
    toggleAccessibilityPanel() {
        const panel = document.getElementById('accessibility-panel');
        panel.classList.toggle('show');
        
        // デバッグ用：現在の状態を表示
        if (panel.classList.contains('show')) {
            this.debugCurrentState();
        }
    }
    
    debugCurrentState() {
        const patientView = document.getElementById('patient-view');
        if (patientView) {
            console.log('=== 現在の患者ビュー状態 ===');
            console.log('クラス一覧:', patientView.className);
            console.log('大きな文字:', this.isEnabled);
            console.log('ふりがな:', this.furiganaEnabled);
            console.log('わかりやすい表示:', this.simpleModeEnabled);
            console.log('高コントラスト:', this.highContrastEnabled);
            console.log('========================');
        }
    }
    
    toggleLargeText() {
        console.log('大きな文字切り替え:', this.isEnabled ? 'OFF' : 'ON');
        this.isEnabled = !this.isEnabled;
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        const toggle = document.getElementById('large-text-toggle');
        
        if (this.isEnabled) {
            patientView?.classList.add('patient-accessibility-mode');
            medicalDetailView?.classList.add('patient-accessibility-mode');
            toggle?.classList.add('active');
            console.log('大きな文字モードを有効化しました');
        } else {
            patientView?.classList.remove('patient-accessibility-mode');
            medicalDetailView?.classList.remove('patient-accessibility-mode');
            toggle?.classList.remove('active');
            console.log('大きな文字モードを無効化しました');
        }
    }
    
    toggleFurigana() {
        console.log('ふりがな切り替え:', this.furiganaEnabled ? 'OFF' : 'ON');
        this.furiganaEnabled = !this.furiganaEnabled;
        const toggle = document.getElementById('furigana-toggle');
        
        if (this.furiganaEnabled) {
            console.log('ふりがなを追加中...');
            this.addFurigana();
            toggle?.classList.add('active');
        } else {
            console.log('ふりがなを削除中...');
            this.removeFurigana();
            toggle?.classList.remove('active');
        }
    }
    
    addFurigana() {
        console.log('ふりがな追加処理開始...');
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        // まず既存のふりがなを全て削除
        this.removeFurigana();
        
        [patientView, medicalDetailView].forEach(view => {
            if (!view) {
                console.log('ビュー要素が見つかりません');
                return;
            }
            
            console.log('ふりがなを追加中...', view.id);
            
            // テキストのみの要素に限定し、一度に一つの要素のみ処理
            const textElements = view.querySelectorAll('h1, h2, h3, p');
            console.log('対象要素数:', textElements.length);
            
            textElements.forEach((element, index) => {
                // 子要素がある場合はスキップ
                if (element.children.length > 0) {
                    console.log(`要素 ${index} は子要素があるためスキップ`);
                    return;
                }
                
                const textContent = element.textContent.trim();
                if (!textContent) return;
                
                console.log(`要素 ${index} (${element.tagName}) のテキスト: "${textContent}"`);
                
                // 完全一致のみを優先的にチェック
                let matchFound = false;
                Object.keys(this.kanjiRuby).forEach(kanji => {
                    if (textContent === kanji && !matchFound) {
                        const ruby = this.kanjiRuby[kanji];
                        const rubyHTML = `<ruby class="furigana-ruby">${kanji}<rt>${ruby}</rt></ruby>`;
                        element.innerHTML = rubyHTML;
                        console.log(`完全一致で置換: "${kanji}" -> "${ruby}"`);
                        matchFound = true;
                    }
                });
                
                // 完全一致がなかった場合のみ部分一致を試行
                if (!matchFound) {
                    let html = element.innerHTML;
                    let originalHtml = html;
                    
                    // 長い語句から順に処理して、複数の語句にふりがなを振る
                    const sortedKanji = Object.keys(this.kanjiRuby).sort((a, b) => b.length - a.length);
                    sortedKanji.forEach(kanji => {
                        if (textContent.includes(kanji) && !html.includes(`<ruby class="furigana-ruby">${kanji}<rt>`)) {
                            const ruby = this.kanjiRuby[kanji];
                            const rubyHTML = `<ruby class="furigana-ruby">${kanji}<rt>${ruby}</rt></ruby>`;
                            // 正規表現を使って確実に置換
                            const regex = new RegExp(kanji.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                            html = html.replace(regex, rubyHTML);
                            console.log(`部分一致で置換: "${kanji}" -> "${ruby}"`);
                        }
                    });
                    
                    if (html !== originalHtml) {
                        element.innerHTML = html;
                        console.log(`要素更新: "${textContent}"`);
                    }
                }
            });
        });
        
        console.log('ふりがな追加処理完了');
    }
    
    removeFurigana() {
        console.log('ふりがな削除処理開始...');
        const rubyElements = document.querySelectorAll('.furigana-ruby');
        console.log('削除対象のルビ要素数:', rubyElements.length);
        
        rubyElements.forEach((ruby, index) => {
            // ルビ要素を漢字テキストのみに置き換え
            const kanjiText = ruby.firstChild ? ruby.firstChild.textContent : ruby.textContent.split('(')[0];
            console.log(`ルビ要素 ${index} を削除:`, ruby.outerHTML, '->', kanjiText);
            ruby.outerHTML = kanjiText;
        });
        
        console.log('ふりがな削除処理完了');
    }
    
    toggleSimpleMode() {
        console.log('わかりやすい表示切り替え:', this.simpleModeEnabled ? 'OFF' : 'ON');
        this.simpleModeEnabled = !this.simpleModeEnabled;
        const toggle = document.getElementById('simple-mode-toggle');
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        if (this.simpleModeEnabled) {
            // 医療用語をやさしい言葉に完全置き換え
            this.replaceWithSimpleLanguage();
            toggle?.classList.add('active');
            console.log('わかりやすい表示を有効化しました（医療用語を分かりやすい言葉に置き換え）');
        } else {
            // 元の言葉に戻す
            this.restoreOriginalLanguage();
            toggle?.classList.remove('active');
            console.log('わかりやすい表示を無効化しました');
        }
    }
    
    replaceWithSimpleLanguage() {
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        [patientView, medicalDetailView].forEach(view => {
            if (!view) return;
            
            // 各要素を個別に処理（重複を防ぐため）
            const textElements = view.querySelectorAll('h1, h2, h3, p, div, span');
            textElements.forEach(element => {
                // 子要素がある場合はスキップ（テキストのみの要素を対象）
                if (element.children.length > 0) return;
                
                let text = element.textContent.trim();
                if (!text) return;
                
                let originalText = text;
                
                // 医療用語を分かりやすい言葉に置き換え（長い語句から順に処理）
                const sortedTerms = Object.keys(this.medicalTerms).sort((a, b) => b.length - a.length);
                sortedTerms.forEach(term => {
                    const simple = this.medicalTerms[term];
                    // 完全一致で置き換え（1回のみ）
                    if (text === term) {
                        text = simple;
                    } else if (text.includes(term)) {
                        // 部分一致の場合は慎重に置換
                        const regex = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                        text = text.replace(regex, simple);
                    }
                });
                
                if (text !== originalText) {
                    element.textContent = text;
                    console.log(`わかりやすい言葉に変換: "${originalText}" -> "${text}"`);
                }
            });
        });
    }
    
    restoreOriginalLanguage() {
        // 元の言葉に戻す（ページリロードを避ける）
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        [patientView, medicalDetailView].forEach(view => {
            if (!view) return;
            
            // 各要素を個別に処理（重複を防ぐため）
            const textElements = view.querySelectorAll('h1, h2, h3, p, div, span');
            textElements.forEach(element => {
                // 子要素がある場合はスキップ（テキストのみの要素を対象）
                if (element.children.length > 0) return;
                
                let text = element.textContent.trim();
                if (!text) return;
                
                let originalText = text;
                
                // 分かりやすい言葉から医療用語に戻す（長い語句から順に処理）
                const sortedTerms = Object.keys(this.medicalTerms).sort((a, b) => b.length - a.length);
                sortedTerms.forEach(term => {
                    const simple = this.medicalTerms[term];
                    // 完全一致で置き換え（1回のみ）
                    if (text === simple) {
                        text = term;
                    } else if (text.includes(simple)) {
                        // 部分一致の場合は慎重に置換
                        const regex = new RegExp(simple.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                        text = text.replace(regex, term);
                    }
                });
                
                if (text !== originalText) {
                    element.textContent = text;
                    console.log(`元の言葉に復元: "${originalText}" -> "${text}"`);
                }
            });
        });
    }
    
    toggleHighContrast() {
        console.log('高コントラスト切り替え:', this.highContrastEnabled ? 'OFF' : 'ON');
        this.highContrastEnabled = !this.highContrastEnabled;
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        const toggle = document.getElementById('high-contrast-toggle');
        
        console.log('患者ビュー要素:', patientView ? '見つかりました' : '見つかりません');
        
        if (this.highContrastEnabled) {
            // 高コントラストクラスのみを追加（大きな文字クラスは追加しない）
            patientView?.classList.add('high-contrast');
            medicalDetailView?.classList.add('high-contrast');
            toggle?.classList.add('active');
            console.log('高コントラストモードを有効化しました');
        } else {
            patientView?.classList.remove('high-contrast');
            medicalDetailView?.classList.remove('high-contrast');
            toggle?.classList.remove('active');
            console.log('高コントラストモードを無効化しました');
        }
    }
    
    
    changeLanguage(lang) {
        console.log('言語変更:', this.currentLanguage, '->', lang);
        
        // 日本語に戻す場合は逆変換を実行（リロードしない）
        if (lang === 'ja' && this.currentLanguage !== 'ja') {
            this.restoreFromLanguageTranslation();
            this.currentLanguage = 'ja';
            // 言語クラスをクリア
            document.body.className = document.body.className.replace(/lang-\w+/g, '');
            console.log('日本語に復元完了');
            return;
        }
        
        // 既に同じ言語の場合は何もしない
        if (lang === this.currentLanguage) {
            return;
        }
        
        this.currentLanguage = lang;
        
        // 基本的な翻訳を適用
        const translations = this.translations[lang];
        if (!translations) return;
        
        Object.keys(translations).forEach(japanese => {
            const translated = translations[japanese];
            const elements = document.querySelectorAll('*');
            
            elements.forEach(el => {
                if (el.children.length === 0 && el.textContent.trim() === japanese) {
                    el.textContent = translated;
                    console.log(`言語変換: "${japanese}" -> "${translated}"`);
                }
            });
        });
        
        // 言語に応じたフォント適用
        document.body.className = document.body.className.replace(/lang-\w+/g, '');
        document.body.classList.add(`lang-${lang}`);
    }
    
    restoreFromLanguageTranslation() {
        console.log('言語翻訳から日本語に復元中...');
        
        // 現在の言語の翻訳辞書から日本語に戻す
        if (this.translations[this.currentLanguage]) {
            Object.keys(this.translations[this.currentLanguage]).forEach(japaneseText => {
                const translatedText = this.translations[this.currentLanguage][japaneseText];
                const elements = document.querySelectorAll('*');
                
                elements.forEach(el => {
                    if (el.children.length === 0 && el.textContent.trim() === translatedText) {
                        el.textContent = japaneseText;
                        console.log(`日本語に復元: "${translatedText}" -> "${japaneseText}"`);
                    }
                });
            });
        }
    }
    
    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                textNodes.push(node);
            }
        }
        
        return textNodes;
    }
    
    // 音声読み上げ（Web Speech API - 無料）
    speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = this.currentLanguage === 'ja' ? 'ja-JP' : 'en-US';
            utterance.rate = 0.8; // ゆっくり読む
            speechSynthesis.speak(utterance);
        }
    }
    
    // 読み上げボタンを追加
    addSpeakButton(element) {
        const speakBtn = document.createElement('button');
        speakBtn.innerHTML = '🔊';
        speakBtn.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
        `;
        speakBtn.onclick = () => this.speakText(element.textContent);
        
        element.style.position = 'relative';
        element.appendChild(speakBtn);
    }
}

// グローバルインスタンス
const accessibility = new PatientAccessibility();
