#!/bin/bash

# ラズパイ4患者ビューディスプレイ セットアップスクリプト
# 使用方法: sudo bash raspberry_pi_setup.sh

echo "🍓 ラズパイ4患者ビューディスプレイ セットアップ開始"
echo "=================================================="

# 色付きメッセージ関数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

# rootユーザーチェック
if [ "$EUID" -ne 0 ]; then
    print_error "このスクリプトはsudo権限で実行してください"
    exit 1
fi

# Step 1: システム更新
print_info "システムを更新しています..."
apt update && apt upgrade -y
print_success "システム更新完了"

# Step 2: 必要なパッケージのインストール
print_info "必要なパッケージをインストールしています..."
apt install -y \
    chromium-browser \
    unclutter \
    xdotool \
    x11-xserver-utils \
    matchbox-window-manager \
    xautomation \
    sed

print_success "パッケージインストール完了"

# Step 3: 自動ログイン設定
print_info "自動ログイン設定を行っています..."

# 現在のユーザー名を取得（sudoで実行されている場合）
REAL_USER=${SUDO_USER:-pi}
print_info "設定対象ユーザー: $REAL_USER"

# 自動ログイン設定
raspi-config nonint do_boot_behaviour B4

print_success "自動ログイン設定完了"

# Step 4: フルスクリーンブラウザ起動スクリプト作成
print_info "フルスクリーンブラウザ起動スクリプトを作成しています..."

# 医療システムサーバーのIPアドレスを設定（デフォルト値）
read -p "医療システムサーバーのIPアドレスを入力してください (デフォルト: 192.168.1.100): " SERVER_IP
SERVER_IP=${SERVER_IP:-192.168.1.100}

# 起動スクリプト作成
cat > /home/$REAL_USER/start_patient_display.sh << EOF
#!/bin/bash

# 患者ビューディスプレイ起動スクリプト
echo "🍓 患者ビューディスプレイを起動しています..."

# 画面設定
export DISPLAY=:0
xset s off         # スクリーンセーバー無効
xset -dpms         # 電源管理無効
xset s noblank     # 画面ブランク無効

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
    "http://$SERVER_IP:5000/patient-display"

EOF

# スクリプトに実行権限を付与
chmod +x /home/$REAL_USER/start_patient_display.sh
chown $REAL_USER:$REAL_USER /home/$REAL_USER/start_patient_display.sh

print_success "起動スクリプト作成完了: /home/$REAL_USER/start_patient_display.sh"

# Step 5: 自動起動設定
print_info "自動起動設定を行っています..."

# .xinitrc作成
cat > /home/$REAL_USER/.xinitrc << EOF
#!/bin/bash
# 患者ビューディスプレイ自動起動設定

# 環境変数設定
export DISPLAY=:0

# 起動スクリプト実行
exec /home/$REAL_USER/start_patient_display.sh
EOF

chmod +x /home/$REAL_USER/.xinitrc
chown $REAL_USER:$REAL_USER /home/$REAL_USER/.xinitrc

# .bashrc に自動起動設定を追加
if ! grep -q "start_patient_display.sh" /home/$REAL_USER/.bashrc; then
    cat >> /home/$REAL_USER/.bashrc << EOF

# 患者ビューディスプレイ自動起動
if [ -z "\$SSH_CLIENT" ] && [ -z "\$SSH_TTY" ] && [ "\$(tty)" = "/dev/tty1" ]; then
    echo "🍓 患者ビューディスプレイを自動起動します..."
    startx
fi
EOF
fi

chown $REAL_USER:$REAL_USER /home/$REAL_USER/.bashrc

print_success "自動起動設定完了"

# Step 6: ネットワーク設定確認
print_info "ネットワーク設定を確認しています..."

# Wi-Fi設定の確認
if iwconfig 2>/dev/null | grep -q "ESSID"; then
    print_success "Wi-Fi接続が設定されています"
    iwconfig 2>/dev/null | grep "ESSID"
else
    print_warning "Wi-Fi設定が必要です"
    print_info "以下のコマンドでWi-Fi設定を行ってください:"
    echo "sudo raspi-config → Network Options → Wi-fi"
fi

# Step 7: 設定ファイル作成
print_info "設定ファイルを作成しています..."

cat > /home/$REAL_USER/patient_display_config.txt << EOF
# 患者ビューディスプレイ設定ファイル
# 作成日時: $(date)

# サーバー設定
SERVER_IP=$SERVER_IP
SERVER_PORT=5000
DISPLAY_URL=http://$SERVER_IP:5000/patient-display

# ディスプレイ設定
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
FULLSCREEN=true

# 自動更新設定
AUTO_REFRESH=true
REFRESH_INTERVAL=30

# アクセシビリティ設定
LARGE_TEXT=false
HIGH_CONTRAST=false
FURIGANA=false
SIMPLE_MODE=false

# デバッグ設定
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF

chown $REAL_USER:$REAL_USER /home/$REAL_USER/patient_display_config.txt

print_success "設定ファイル作成完了: /home/$REAL_USER/patient_display_config.txt"

# Step 8: 手動起動用スクリプト作成
print_info "手動起動用スクリプトを作成しています..."

cat > /home/$REAL_USER/manual_start.sh << EOF
#!/bin/bash

echo "🍓 患者ビューディスプレイを手動起動します"
echo "終了するには Ctrl+C を押してください"
echo ""

# 設定ファイル読み込み
if [ -f "/home/$REAL_USER/patient_display_config.txt" ]; then
    source /home/$REAL_USER/patient_display_config.txt
    echo "設定ファイルを読み込みました"
    echo "サーバー: \$DISPLAY_URL"
    echo ""
fi

# ブラウザ起動
export DISPLAY=:0
chromium-browser \\
    --kiosk \\
    --no-sandbox \\
    --disable-infobars \\
    --start-fullscreen \\
    "\$DISPLAY_URL" 2>/dev/null &

echo "ブラウザを起動しました"
echo "終了するには Ctrl+C を押してください"

# 終了待機
trap 'echo ""; echo "患者ビューディスプレイを終了します..."; pkill chromium; exit 0' INT
while true; do
    sleep 1
done
EOF

chmod +x /home/$REAL_USER/manual_start.sh
chown $REAL_USER:$REAL_USER /home/$REAL_USER/manual_start.sh

print_success "手動起動スクリプト作成完了: /home/$REAL_USER/manual_start.sh"

# Step 9: 完了メッセージ
echo ""
echo "=================================================="
print_success "🍓 ラズパイ4患者ビューディスプレイ セットアップ完了！"
echo "=================================================="
echo ""
print_info "📋 セットアップ内容:"
echo "   ✅ システム更新"
echo "   ✅ 必要パッケージインストール"
echo "   ✅ 自動ログイン設定"
echo "   ✅ フルスクリーンブラウザ設定"
echo "   ✅ 自動起動設定"
echo "   ✅ 設定ファイル作成"
echo ""
print_info "🔧 作成されたファイル:"
echo "   📄 /home/$REAL_USER/start_patient_display.sh (自動起動スクリプト)"
echo "   📄 /home/$REAL_USER/manual_start.sh (手動起動スクリプト)"
echo "   📄 /home/$REAL_USER/patient_display_config.txt (設定ファイル)"
echo "   📄 /home/$REAL_USER/.xinitrc (X起動設定)"
echo ""
print_info "🚀 次のステップ:"
echo "   1. 再起動してください: sudo reboot"
echo "   2. 医療システムサーバー($SERVER_IP:5000)が起動していることを確認"
echo "   3. PCから患者を選択して「ラズパイに表示」ボタンをクリック"
echo ""
print_info "🔧 手動起動する場合:"
echo "   ./manual_start.sh"
echo ""
print_info "⚙️  設定変更する場合:"
echo "   nano /home/$REAL_USER/patient_display_config.txt"
echo ""
print_warning "📝 注意事項:"
echo "   - Wi-Fi設定が完了していることを確認してください"
echo "   - 医療システムサーバーのIPアドレスが正しいことを確認してください"
echo "   - ファイアウォール設定でポート5000が開放されていることを確認してください"
echo ""

read -p "今すぐ再起動しますか？ (y/N): " REBOOT_NOW
if [[ $REBOOT_NOW =~ ^[Yy]$ ]]; then
    print_info "再起動しています..."
    reboot
else
    print_info "後で手動で再起動してください: sudo reboot"
fi
