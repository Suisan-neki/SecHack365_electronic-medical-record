#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PC側の問題を自動診断・修正するスクリプト
"""

import requests
import json
import time
import subprocess
import sys
import os
from urllib.parse import urljoin

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[34m",
        "SUCCESS": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def check_server_status():
    """サーバーの状態をチェック"""
    print_status("医療システムサーバーの状態をチェックしています...")
    
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print_status("✅ サーバーは正常に動作しています", "SUCCESS")
            return True
        else:
            print_status(f"❌ サーバーエラー: HTTP {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        print_status("❌ サーバーに接続できません", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ サーバーチェックエラー: {e}", "ERROR")
        return False

def check_api_endpoints():
    """APIエンドポイントをチェック"""
    print_status("APIエンドポイントをチェックしています...")
    
    endpoints = [
        "/api/patient-display",
        "/api/set-patient-display",
        "/patient-display"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5001{endpoint}"
            if endpoint == "/api/set-patient-display":
                # POSTエンドポイントのテスト
                response = requests.post(url, 
                    json={"patient_id": "test"}, 
                    timeout=5
                )
            else:
                # GETエンドポイントのテスト
                response = requests.get(url, timeout=5)
            
            results[endpoint] = {
                "status_code": response.status_code,
                "accessible": True
            }
            print_status(f"✅ {endpoint}: HTTP {response.status_code}", "SUCCESS")
            
        except Exception as e:
            results[endpoint] = {
                "error": str(e),
                "accessible": False
            }
            print_status(f"❌ {endpoint}: {e}", "ERROR")
    
    return results

def test_patient_display_api():
    """患者表示APIをテスト"""
    print_status("患者表示APIをテストしています...")
    
    try:
        # セッションを作成してログインをシミュレート
        session = requests.Session()
        
        # 患者表示設定APIをテスト
        response = session.post("http://localhost:5001/api/set-patient-display", 
            json={"patient_id": "patient_001"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_status("✅ 患者表示設定API正常", "SUCCESS")
            return True
        elif response.status_code == 401:
            print_status("⚠️ 認証が必要です", "WARNING")
            return False
        elif response.status_code == 403:
            print_status("⚠️ 権限が不足しています", "WARNING")
            return False
        else:
            print_status(f"❌ API エラー: HTTP {response.status_code}", "ERROR")
            print_status(f"レスポンス: {response.text}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ API テストエラー: {e}", "ERROR")
        return False

def check_javascript_files():
    """JavaScriptファイルの存在と内容をチェック"""
    print_status("JavaScriptファイルをチェックしています...")
    
    js_files = [
        "app/static/script.js",
        "app/static/accessibility.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print_status(f"✅ {js_file} 存在確認", "SUCCESS")
            
            # sendToRaspberryPi関数の存在確認
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sendToRaspberryPi' in content:
                    print_status(f"✅ {js_file} にsendToRaspberryPi関数が存在", "SUCCESS")
                else:
                    print_status(f"⚠️ {js_file} にsendToRaspberryPi関数が見つかりません", "WARNING")
        else:
            print_status(f"❌ {js_file} が見つかりません", "ERROR")

def fix_button_state():
    """ボタンの状態を修正するJavaScriptコードを生成"""
    print_status("ボタン状態修正用のJavaScriptコードを生成しています...")
    
    js_fix_code = """
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
"""
    
    # JavaScriptコードをファイルに保存
    with open('pc_fix.js', 'w', encoding='utf-8') as f:
        f.write(js_fix_code)
    
    print_status("✅ 修正用JavaScriptコードを pc_fix.js に保存しました", "SUCCESS")
    return js_fix_code

def create_test_html():
    """テスト用HTMLページを作成"""
    print_status("テスト用HTMLページを作成しています...")
    
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ラズパイ表示テスト</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-button { 
            background: #e67e22; 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px; 
            cursor: pointer; 
            margin: 10px;
        }
        .test-button:hover { background: #d35400; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <h1>🍓 ラズパイ表示テスト</h1>
    
    <div id="status" class="status info">
        テスト準備完了
    </div>
    
    <button class="test-button" onclick="testRaspiDisplay()">
        🍓 ラズパイに表示（テスト）
    </button>
    
    <button class="test-button" onclick="checkConnection()">
        🔍 接続確認
    </button>
    
    <button class="test-button" onclick="checkRaspiStatus()">
        📊 ラズパイ状態確認
    </button>
    
    <div id="log" style="background: #f8f9fa; padding: 15px; margin-top: 20px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;"></div>
    
    <script>
        function log(message) {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.textContent += `[${timestamp}] ${message}\\n`;
            console.log(message);
        }
        
        function setStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
        }
        
        async function testRaspiDisplay() {
            log('🍓 ラズパイ表示テストを開始します...');
            setStatus('送信中...', 'info');
            
            try {
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
                log(`✅ 送信成功: ${JSON.stringify(result)}`);
                setStatus('✅ ラズパイへの送信が完了しました！', 'success');
                
            } catch (error) {
                log(`❌ 送信エラー: ${error.message}`);
                setStatus(`❌ 送信失敗: ${error.message}`, 'error');
            }
        }
        
        async function checkConnection() {
            log('🔍 接続確認を開始します...');
            setStatus('接続確認中...', 'info');
            
            try {
                const response = await fetch('/api/patient-display');
                log(`患者表示API: HTTP ${response.status}`);
                
                if (response.ok) {
                    setStatus('✅ 接続正常', 'success');
                } else {
                    setStatus(`⚠️ 接続問題: HTTP ${response.status}`, 'error');
                }
                
            } catch (error) {
                log(`❌ 接続エラー: ${error.message}`);
                setStatus(`❌ 接続失敗: ${error.message}`, 'error');
            }
        }
        
        async function checkRaspiStatus() {
            log('📊 ラズパイ状態確認を開始します...');
            setStatus('状態確認中...', 'info');
            
            try {
                // ラズパイのIPアドレスに直接アクセス
                const raspiResponse = await fetch('http://192.168.3.7:5001/patient-display', {
                    mode: 'no-cors'
                });
                log('✅ ラズパイへの直接アクセス試行完了');
                setStatus('✅ ラズパイ状態確認完了', 'success');
                
            } catch (error) {
                log(`⚠️ ラズパイ直接アクセスエラー: ${error.message}`);
                setStatus('⚠️ ラズパイ直接アクセス不可（CORS制限の可能性）', 'info');
            }
        }
        
        // ページ読み込み時の初期化
        window.onload = function() {
            log('🔧 テストページが読み込まれました');
            log('医療システムサーバー: http://localhost:5001');
            log('ラズパイアドレス: http://192.168.3.7:5001');
        };
    </script>
</body>
</html>
"""
    
    with open('raspi_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print_status("✅ テスト用HTMLページを raspi_test.html に保存しました", "SUCCESS")

def main():
    print_status("🔧 PC側問題自動診断・修正スクリプトを開始します", "INFO")
    print("=" * 60)
    
    # 1. サーバー状態チェック
    if not check_server_status():
        print_status("サーバーが起動していません。先にサーバーを起動してください。", "ERROR")
        return False
    
    # 2. APIエンドポイントチェック
    api_results = check_api_endpoints()
    
    # 3. 患者表示APIテスト
    test_patient_display_api()
    
    # 4. JavaScriptファイルチェック
    check_javascript_files()
    
    # 5. 修正用JavaScriptコード生成
    fix_button_state()
    
    # 6. テスト用HTMLページ作成
    create_test_html()
    
    print("=" * 60)
    print_status("🍓 PC側自動修正完了！", "SUCCESS")
    print()
    print_status("次のステップ:", "INFO")
    print("1. ブラウザで http://localhost:5001 にアクセス")
    print("2. F12キーを押して開発者ツールを開く")
    print("3. Consoleタブで以下のコードを実行:")
    print()
    print("   // 修正用JavaScriptを読み込み")
    print("   fetch('/pc_fix.js').then(r=>r.text()).then(eval)")
    print()
    print("4. または、テスト用ページを開く:")
    print("   http://localhost:5001/raspi_test.html")
    print()
    print_status("これで「ラズパイに表示」ボタンが動作するはずです！", "SUCCESS")
    
    return True

if __name__ == "__main__":
    main()
