// 患者向けアクセシビリティ機能（シンプル版）

class PatientAccessibility {
    constructor() {
        this.isEnabled = false;
        this.furiganaEnabled = false;
        this.largeTextEnabled = false;
        this.simpleModeEnabled = false;
        this.languageEnabled = false;
        
        // 振り仮名辞書（シンプル版）
        this.kanjiRuby = {
            '山下真凜': 'やましたまりん',
            '現在の病気・症状': 'げんざいのびょうき・しょうじょう',
            '処方薬': 'しょほうやく',
            '検査結果': 'けんさけっか',
            '画面に戻る': 'がめんにもどる',
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
        // 既にボタンが存在する場合は作成しない
        if (document.querySelector('.language-selector')) {
            console.log('アクセシビリティボタンは既に存在します');
            return;
        }
        
        // 患者ビューが表示されている場合のみ作成
        const patientView = document.getElementById('patient-view');
        const isPatientViewVisible = patientView && patientView.style.display !== 'none';
        
        if (!isPatientViewVisible) {
            console.log('患者ビューが表示されていないため、アクセシビリティボタンを非表示にします');
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
                <label>多言語表記</label>
                <div class="toggle-switch" id="language-toggle" onclick="accessibility.toggleLanguage()"></div>
            </div>
        `;
        
        document.body.appendChild(languageButton);
        document.body.appendChild(panel);
    }
    
    getCurrentUserRole() {
        // HTMLから現在のユーザーロールを取得
        const bodyElement = document.body;
        return bodyElement ? bodyElement.getAttribute('data-user-role') : null;
    }
    
    enableBasicAccessibility() {
        // 患者向けの基本設定を自動適用
        this.toggleLargeText();
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
        console.log('=== アクセシビリティ状態 ===');
        console.log('大きな文字:', this.largeTextEnabled ? 'ON' : 'OFF');
        console.log('ふりがな:', this.furiganaEnabled ? 'ON' : 'OFF');
        console.log('========================');
    }
    
    checkPatientRole() {
        const userRole = this.getCurrentUserRole();
        console.log('checkPatientRole - 現在のユーザーロール:', userRole);
        
        if (userRole === 'patient') {
            console.log('患者ロールを検出しました。アクセシビリティ機能を有効化します。');
            this.enableBasicAccessibility();
        } else {
            console.log('患者ロールではないため、アクセシビリティ機能は無効です。');
        }
    }
    
    toggleLargeText() {
        console.log('大きな文字切り替え:', this.largeTextEnabled ? 'OFF' : 'ON');
        this.largeTextEnabled = !this.largeTextEnabled;
        const toggle = document.getElementById('large-text-toggle');
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        if (this.largeTextEnabled) {
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
            console.log('ふりがな機能は一時的に無効化されています');
            alert('ふりがな機能は現在調整中です。しばらくお待ちください。');
            this.furiganaEnabled = false;
            toggle?.classList.remove('active');
        } else {
            console.log('ふりがな機能は既に無効です');
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
                if (element.children.length > 0) return;
                
                const text = element.textContent.trim();
                if (!text) return;
                
                // 既に振り仮名が含まれている場合はスキップ
                if (element.innerHTML.includes('<ruby>') || element.innerHTML.includes('<rt>')) {
                    return;
                }
                
                // 完全一致で置換
                if (this.kanjiRuby[text]) {
                    const ruby = this.createRubyElement(text, this.kanjiRuby[text]);
                    element.innerHTML = ruby.outerHTML;
                    console.log(`完全一致で置換: "${text}" -> "${this.kanjiRuby[text]}"`);
                    return;
                }
                
                // 部分一致で置換
                let newText = text;
                Object.keys(this.kanjiRuby).forEach(kanji => {
                    const furigana = this.kanjiRuby[kanji];
                    if (newText.includes(kanji)) {
                        const ruby = this.createRubyElement(kanji, furigana);
                        newText = newText.replace(kanji, ruby.outerHTML);
                        console.log(`部分一致で置換: "${kanji}" -> "${furigana}"`);
                    }
                });
                
                if (newText !== text) {
                    element.innerHTML = newText;
                }
            });
        });
        
        console.log('ふりがな追加処理完了');
    }
    
    createRubyElement(kanji, furigana) {
        const ruby = document.createElement('ruby');
        ruby.textContent = kanji;
        const rt = document.createElement('rt');
        rt.textContent = furigana;
        ruby.appendChild(rt);
        return ruby;
    }
    
    removeFurigana() {
        console.log('ふりがな削除処理開始...');
        
        // 患者ビューと詳細ビューの両方で処理
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        [patientView, medicalDetailView].forEach(view => {
            if (!view) return;
            
            // 全てのruby要素を削除
            const rubyElements = view.querySelectorAll('ruby');
            rubyElements.forEach(ruby => {
                const parent = ruby.parentNode;
                if (parent) {
                    // ruby要素をテキストノードに置き換え
                    parent.replaceChild(document.createTextNode(ruby.textContent), ruby);
                    parent.normalize();
                }
            });
            
            // 重複した振り仮名テキストを削除（rt要素が残っている場合）
            const rtElements = view.querySelectorAll('rt');
            rtElements.forEach(rt => {
                const parent = rt.parentNode;
                if (parent && parent.tagName === 'RUBY') {
                    parent.replaceChild(document.createTextNode(parent.textContent), parent);
                }
            });
            
            // 重複した振り仮名テキストを手動で削除
            const textElements = view.querySelectorAll('h1, h2, h3, p, div, span');
            textElements.forEach(element => {
                if (element.children.length === 0) {
                    let text = element.textContent;
                    // 重複した振り仮名パターンを削除
                    text = text.replace(/([あ-ん]+)\1+/g, '$1'); // ひらがなの重複を削除
                    text = text.replace(/([あ-ん]+)([あ-ん]+)\1\2/g, '$1$2'); // パターンの重複を削除
                    element.textContent = text;
                }
            });
        });
        
        console.log('ふりがな削除処理完了');
    }
    
    // アクセシビリティ設定をリセット
    resetAccessibility() {
        console.log('🔄 アクセシビリティ設定をリセット中...');
        
        // 設定を無効化
        this.isEnabled = false;
        this.furiganaEnabled = false;
        this.largeTextEnabled = false;
        this.simpleModeEnabled = false;
        this.languageEnabled = false;
        
        // 振り仮名を完全にクリア
        this.clearAllFurigana();
        
        // 大きな文字を無効化
        this.disableLargeText();
        
        // トグルスイッチの状態をリセット
        const largeTextToggle = document.getElementById('large-text-toggle');
        const furiganaToggle = document.getElementById('furigana-toggle');
        const simpleModeToggle = document.getElementById('simple-mode-toggle');
        const languageToggle = document.getElementById('language-toggle');
        
        if (largeTextToggle) {
            largeTextToggle.classList.remove('active');
        }
        if (furiganaToggle) {
            furiganaToggle.classList.remove('active');
        }
        if (simpleModeToggle) {
            simpleModeToggle.classList.remove('active');
        }
        if (languageToggle) {
            languageToggle.classList.remove('active');
        }
        
        console.log('✅ アクセシビリティ設定をリセットしました');
    }
    
    // 全ての振り仮名を完全にクリア
    clearAllFurigana() {
        console.log('🧹 全ての振り仮名をクリア中...');
        
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        [patientView, medicalDetailView].forEach(view => {
            if (!view) return;
            
            // 全てのruby要素を削除
            const rubyElements = view.querySelectorAll('ruby');
            rubyElements.forEach(ruby => {
                const parent = ruby.parentNode;
                if (parent) {
                    parent.replaceChild(document.createTextNode(ruby.textContent), ruby);
                    parent.normalize();
                }
            });
            
            // 全てのrt要素を削除
            const rtElements = view.querySelectorAll('rt');
            rtElements.forEach(rt => {
                const parent = rt.parentNode;
                if (parent) {
                    parent.replaceChild(document.createTextNode(parent.textContent), parent);
                    parent.normalize();
                }
            });
            
            // テキスト要素の重複をクリア
            const textElements = view.querySelectorAll('h1, h2, h3, p, div, span');
            textElements.forEach(element => {
                if (element.children.length === 0) {
                    let text = element.textContent;
                    // 重複したひらがなを削除
                    text = text.replace(/([あ-ん]+)\1+/g, '$1');
                    // 重複した漢字を削除
                    text = text.replace(/([一-龯]+)\1+/g, '$1');
                    element.textContent = text;
                }
            });
        });
        
        console.log('✅ 振り仮名クリア完了');
    }
    
    // 振り仮名の重複を検出
    hasFuriganaDuplication() {
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        const checkView = (view) => {
            if (!view) return false;
            const textElements = view.querySelectorAll('h1, h2, h3, p, div, span');
            for (let element of textElements) {
                if (element.children.length === 0) {
                    const text = element.textContent;
                    // 重複パターンを検出
                    if (/([あ-ん]+)\1{2,}/.test(text)) {
                        return true;
                    }
                }
            }
            return false;
        };
        
        return checkView(patientView) || checkView(medicalDetailView);
    }
    
    // 大きな文字を無効化
    disableLargeText() {
        const patientView = document.getElementById('patient-view');
        const medicalDetailView = document.getElementById('medical-detail-view');
        
        patientView?.classList.remove('patient-accessibility-mode');
        medicalDetailView?.classList.remove('patient-accessibility-mode');
    }
    
    // わかりやすい表示の切り替え
    toggleSimpleMode() {
        console.log('わかりやすい表示切り替え:', this.simpleModeEnabled ? 'OFF' : 'ON');
        this.simpleModeEnabled = !this.simpleModeEnabled;
        const toggle = document.getElementById('simple-mode-toggle');
        
        if (this.simpleModeEnabled) {
            console.log('わかりやすい表示機能は一時的に無効化されています');
            alert('わかりやすい表示機能は現在調整中です。しばらくお待ちください。');
            this.simpleModeEnabled = false;
            toggle?.classList.remove('active');
        } else {
            console.log('わかりやすい表示機能は既に無効です');
            toggle?.classList.remove('active');
        }
    }
    
    // 多言語表記の切り替え
    toggleLanguage() {
        console.log('多言語表記切り替え:', this.languageEnabled ? 'OFF' : 'ON');
        this.languageEnabled = !this.languageEnabled;
        const toggle = document.getElementById('language-toggle');
        
        if (this.languageEnabled) {
            console.log('多言語表記機能は一時的に無効化されています');
            alert('多言語表記機能は現在調整中です。しばらくお待ちください。');
            this.languageEnabled = false;
            toggle?.classList.remove('active');
        } else {
            console.log('多言語表記機能は既に無効です');
            toggle?.classList.remove('active');
        }
    }
}

// グローバルインスタンス
const accessibility = new PatientAccessibility();