# 🍓 ラズパイ4患者ビューディスプレイ セットアップガイド

## 📋 概要

このガイドでは、ラズパイ4とモニターを使用して患者用ビューを表示するシステムの構築方法を説明します。

### システム構成
```
[PC (医療従事者)] ←→ [Wi-Fi Router] ←→ [ラズパイ4 + モニター (患者用)]
        ↓                                      ↓
   患者選択・操作                        患者情報表示
   「ラズパイに表示」                    フルスクリーン表示
```

## 🛠️ 必要な機材

### ハードウェア
- **Raspberry Pi 4** (4GB RAM以上推奨)
- **microSDカード** (32GB以上、Class 10)
- **HDMIモニター** (患者用表示)
- **HDMIケーブル**
- **電源アダプター** (USB-C、5V 3A)
- **Wi-Fi環境** (医療システムサーバーと同一ネットワーク)

### ソフトウェア
- **Raspberry Pi OS** (Desktop版)
- **Chromium Browser** (フルスクリーン表示用)

## 🚀 セットアップ手順

### Step 1: Raspberry Pi OSの書き込み

1. **Raspberry Pi Imager**をダウンロード
   ```
   https://www.raspberrypi.com/software/
   ```

2. **microSDカード**をPCに挿入

3. **Raspberry Pi Imager**で以下を設定：
   - **OS**: Raspberry Pi OS (Desktop版)
   - **詳細設定** (歯車アイコン):
     - ✅ SSH有効化
     - ✅ Wi-Fi設定 (SSID/パスワード)
     - ✅ ユーザー名/パスワード設定
     - ✅ 地域設定 (日本/Tokyo)

4. **書き込み実行**

### Step 2: ラズパイ4の初期起動

1. **microSDカード**をラズパイ4に挿入
2. **HDMIモニター**を接続
3. **電源**を接続して起動
4. **Wi-Fi接続**を確認

### Step 3: 自動セットアップスクリプト実行

1. **セットアップスクリプト**をダウンロード：
   ```bash
   wget https://raw.githubusercontent.com/your-repo/raspberry_pi_setup.sh
   ```

2. **実行権限**を付与：
   ```bash
   chmod +x raspberry_pi_setup.sh
   ```

3. **スクリプト実行**：
   ```bash
   sudo bash raspberry_pi_setup.sh
   ```

4. **医療システムサーバーのIPアドレス**を入力
   - 例: `192.168.1.100`

5. **再起動**：
   ```bash
   sudo reboot
   ```

### Step 4: 医療システムサーバー設定

1. **PCで医療システム**を起動：
   ```bash
   cd SecHack365_project/info_sharing_system
   python run_app.py
   ```

2. **ファイアウォール設定**（必要に応じて）：
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="Medical System" dir=in action=allow protocol=TCP localport=5000
   
   # Linux
   sudo ufw allow 5000
   ```

## 🎯 使用方法

### 基本的な流れ

1. **医療システムにログイン** (PC)
2. **患者を選択** (電子カルテから抽出)
3. **「🍓 ラズパイに表示」ボタン**をクリック
4. **ラズパイのモニター**に患者情報が表示される

### 患者ビューの機能

- **基本情報**: 年齢、性別、血液型、アレルギー
- **現在の診断**: 病気・症状の情報
- **処方薬**: 現在服用中の薬
- **バイタルサイン**: 血圧、心拍数、体温など
- **検査結果**: 最新の検査データ
- **アクセシビリティ機能**: 大きな文字、ふりがな、簡単な言葉

### アクセシビリティ機能

患者ビューには以下の機能が含まれています：

- **🔤 大きな文字**: 文字サイズを拡大
- **🌈 見やすい色**: 高コントラスト表示
- **あ ふりがな**: 漢字にふりがなを追加
- **😊 わかりやすい表示**: 医療用語を簡単な言葉に変換
- **🌐 言語切り替え**: 多言語対応

## 🔧 設定とカスタマイズ

### 設定ファイル

設定は `/home/pi/patient_display_config.txt` で管理されます：

```bash
# サーバー設定
SERVER_IP=192.168.1.100
SERVER_PORT=5000

# ディスプレイ設定
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
FULLSCREEN=true

# 自動更新設定
AUTO_REFRESH=true
REFRESH_INTERVAL=30
```

### 手動起動

自動起動が失敗した場合の手動起動：

```bash
./manual_start.sh
```

### デバッグモード

問題が発生した場合：

```bash
# ブラウザのデバッグ情報を表示
chromium-browser --enable-logging --log-level=0 http://192.168.1.100:5000/patient-display
```

## 🛡️ セキュリティ考慮事項

### ネットワークセキュリティ
- **専用ネットワーク**: 医療システム専用のWi-Fiネットワークを使用
- **ファイアウォール**: 不要なポートを閉鎖
- **VPN**: 可能であればVPN経由でアクセス

### デバイスセキュリティ
- **自動ロック**: 一定時間後の自動画面ロック
- **物理セキュリティ**: ラズパイの物理的な保護
- **定期更新**: OSとソフトウェアの定期更新

### データ保護
- **一時データ**: ブラウザキャッシュの定期削除
- **ログ管理**: アクセスログの適切な管理
- **暗号化通信**: HTTPS通信の使用（本番環境）

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. ラズパイが起動しない
```bash
# SDカードの確認
sudo fdisk -l

# 電源供給の確認
vcgencmd get_throttled
```

#### 2. Wi-Fi接続できない
```bash
# Wi-Fi設定の確認
sudo raspi-config
# → Network Options → Wi-fi

# 接続状況確認
iwconfig
ping 8.8.8.8
```

#### 3. ブラウザが起動しない
```bash
# X11の確認
echo $DISPLAY
xset q

# Chromiumの手動起動
chromium-browser --version
```

#### 4. 患者情報が表示されない
```bash
# サーバー接続確認
curl http://192.168.1.100:5000/patient-display

# ネットワーク確認
ping 192.168.1.100
```

#### 5. 画面が真っ黒
```bash
# 画面設定確認
tvservice -s
vcgencmd display_power

# 解像度設定
sudo raspi-config
# → Advanced Options → Resolution
```

### ログ確認

```bash
# システムログ
sudo journalctl -f

# Xorgログ
cat ~/.local/share/xorg/Xorg.0.log

# Chromiumログ
ls ~/.config/chromium/
```

## 📊 パフォーマンス最適化

### メモリ使用量削減
```bash
# GPU メモリ分割
sudo raspi-config
# → Advanced Options → Memory Split → 128

# 不要サービス停止
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### 起動時間短縮
```bash
# 起動時間測定
systemd-analyze

# 起動プロセス確認
systemd-analyze blame
```

## 🔄 メンテナンス

### 定期メンテナンス

#### 毎日
- **動作確認**: 正常に表示されているか確認
- **ネットワーク確認**: Wi-Fi接続状況確認

#### 毎週
- **システム更新**: 
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- **ディスク容量確認**:
  ```bash
  df -h
  ```

#### 毎月
- **ログクリーンアップ**:
  ```bash
  sudo journalctl --vacuum-time=30d
  ```
- **キャッシュクリア**:
  ```bash
  rm -rf ~/.cache/chromium
  ```

### バックアップ

重要な設定ファイルのバックアップ：

```bash
# 設定ファイルバックアップ
cp /home/pi/patient_display_config.txt /home/pi/config_backup_$(date +%Y%m%d).txt

# 起動スクリプトバックアップ
cp /home/pi/start_patient_display.sh /home/pi/script_backup_$(date +%Y%m%d).sh
```

## 📞 サポート

### 問題報告時の情報

問題が発生した場合、以下の情報を収集してください：

```bash
# システム情報
uname -a
cat /etc/os-release

# ハードウェア情報
cat /proc/cpuinfo | grep Model
vcgencmd measure_temp
vcgencmd get_mem arm && vcgencmd get_mem gpu

# ネットワーク情報
ip addr show
iwconfig

# ログ情報
sudo journalctl -n 50
```

### 連絡先

- **技術サポート**: [サポートメールアドレス]
- **緊急時**: [緊急連絡先]
- **ドキュメント**: [オンラインドキュメントURL]

---

## 📝 更新履歴

- **v1.0.0** (2024-09-23): 初版リリース
  - 基本セットアップ機能
  - 自動起動設定
  - アクセシビリティ機能

---

**🍓 Happy Raspberry Pi Computing! 🍓**
