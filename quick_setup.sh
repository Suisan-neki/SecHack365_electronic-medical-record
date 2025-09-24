#!/bin/bash

# ラズパイ4患者ビュー クイックセットアップスクリプト
echo "🍓 ラズパイ4患者ビュー クイックセットアップ"
echo "============================================"

# 色付きメッセージ関数
print_success() { echo -e "\033[32m✅ $1\033[0m"; }
print_info() { echo -e "\033[34mℹ️  $1\033[0m"; }
print_warning() { echo -e "\033[33m⚠️  $1\033[0m"; }
print_error() { echo -e "\033[31m❌ $1\033[0m"; }

# 設定値入力
print_info "設定値を入力してください："
read -p "医療システムサーバーのIPアドレス (例: 192.168.1.100): " SERVER_IP
read -p "ポート番号 (デフォルト: 5000): " SERVER_PORT
SERVER_PORT=${SERVER_PORT:-5000}

print_info "設定値："
echo "  サーバー: $SERVER_IP:$SERVER_PORT"
echo "  URL: http://$SERVER_IP:$SERVER_PORT/patient-display"

read -p "この設定で続行しますか？ (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    print_error "セットアップを中止しました"
    exit 1
fi

# 1. 必要パッケージインストール
print_info "必要なパッケージをインストールしています..."
sudo apt update
sudo apt install -y chromium-browser unclutter xdotool x11-xserver-utils matchbox-window-manager

# 2. 起動スクリプト作成
print_info "起動スクリプトを作成しています..."
cat > ~/start_patient_display.sh << EOF
#!/bin/bash

# 患者ビューディスプレイ起動スクリプト
echo "🍓 患者ビューディスプレイを起動しています..."

# サーバー設定
SERVER_IP="$SERVER_IP"
SERVER_PORT="$SERVER_PORT"

# 画面設定
export DISPLAY=:0
xset s off
xset -dpms
xset s noblank

# マウスカーソルを非表示
unclutter -idle 0.5 -root &

# ウィンドウマネージャー起動
matchbox-window-manager -use_cursor no &

# 少し待機
sleep 3

# フルスクリーンでChromiumを起動
chromium-browser \\
    --kiosk \\
    --no-sandbox \\
    --disable-infobars \\
    --disable-session-crashed-bubble \\
    --disable-component-extensions-with-background-pages \\
    --disable-background-networking \\
    --disable-background-timer-throttling \\
    --disable-renderer-backgrounding \\
    --disable-backgrounding-occluded-windows \\
    --disable-features=TranslateUI \\
    --disable-ipc-flooding-protection \\
    --autoplay-policy=no-user-gesture-required \\
    --start-fullscreen \\
    --window-position=0,0 \\
    --window-size=1920,1080 \\
    "http://\$SERVER_IP:\$SERVER_PORT/patient-display"
EOF

chmod +x ~/start_patient_display.sh

# 3. 手動起動スクリプト作成
print_info "手動起動スクリプトを作成しています..."
cat > ~/manual_start.sh << EOF
#!/bin/bash

echo "🍓 患者ビューディスプレイを手動起動します"
echo "終了するには Ctrl+C を押してください"

export DISPLAY=:0
chromium-browser \\
    --kiosk \\
    --no-sandbox \\
    --disable-infobars \\
    --start-fullscreen \\
    "http://$SERVER_IP:$SERVER_PORT/patient-display" 2>/dev/null &

echo "ブラウザを起動しました"
echo "終了するには Ctrl+C を押してください"

trap 'echo ""; echo "患者ビューディスプレイを終了します..."; pkill chromium; exit 0' INT
while true; do
    sleep 1
done
EOF

chmod +x ~/manual_start.sh

# 4. テストスクリプト作成
print_info "テストスクリプトを作成しています..."
cat > ~/test_connection.sh << EOF
#!/bin/bash

echo "🔍 患者ビューディスプレイ接続テスト"
echo "=================================="

SERVER_IP="$SERVER_IP"
SERVER_PORT="$SERVER_PORT"

echo "サーバー: \$SERVER_IP:\$SERVER_PORT"
echo ""

# ネットワーク接続テスト
echo "📡 ネットワーク接続テスト..."
if ping -c 3 \$SERVER_IP > /dev/null 2>&1; then
    echo "✅ サーバーへのping成功"
else
    echo "❌ サーバーへのping失敗"
fi

# HTTP接続テスト
echo ""
echo "🌐 HTTP接続テスト..."
if curl -s "http://\$SERVER_IP:\$SERVER_PORT/patient-display" > /dev/null; then
    echo "✅ 患者ビューページへの接続成功"
else
    echo "❌ 患者ビューページへの接続失敗"
fi

echo ""
echo "=================================="
echo "テスト完了"
EOF

chmod +x ~/test_connection.sh

# 5. 設定ファイル作成
print_info "設定ファイルを作成しています..."
cat > ~/patient_display_config.txt << EOF
# 患者ビューディスプレイ設定ファイル
SERVER_IP=$SERVER_IP
SERVER_PORT=$SERVER_PORT
DISPLAY_URL=http://$SERVER_IP:$SERVER_PORT/patient-display

SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
FULLSCREEN=true

AUTO_REFRESH=true
REFRESH_INTERVAL=30
EOF

# 6. 自動起動設定
print_info "自動起動設定を行っています..."

# .xinitrc作成
cat > ~/.xinitrc << EOF
#!/bin/bash
export DISPLAY=:0
exec /home/\$(whoami)/start_patient_display.sh
EOF

chmod +x ~/.xinitrc

# .bashrcに自動起動設定追加
if ! grep -q "start_patient_display.sh" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# 患者ビューディスプレイ自動起動
if [ -z "\$SSH_CLIENT" ] && [ -z "\$SSH_TTY" ] && [ "\$(tty)" = "/dev/tty1" ]; then
    echo "🍓 患者ビューディスプレイを自動起動します..."
    startx
fi
EOF
fi

# 7. 完了メッセージ
print_success "🍓 セットアップ完了！"
echo ""
print_info "作成されたファイル："
echo "  📄 ~/start_patient_display.sh (自動起動スクリプト)"
echo "  📄 ~/manual_start.sh (手動起動スクリプト)"
echo "  📄 ~/test_connection.sh (接続テストスクリプト)"
echo "  📄 ~/patient_display_config.txt (設定ファイル)"
echo ""
print_info "次のステップ："
echo "  1. 接続テスト: ./test_connection.sh"
echo "  2. 手動起動テスト: ./manual_start.sh"
echo "  3. 自動起動テスト: sudo reboot"
echo ""
print_warning "注意："
echo "  - 医療システムサーバー($SERVER_IP:$SERVER_PORT)が起動していることを確認してください"
echo "  - Wi-Fi接続が正常であることを確認してください"
