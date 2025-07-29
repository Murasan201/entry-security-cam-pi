# 玄関セキュリティシステム

Raspberry PiとUSBカメラを用いた玄関監視システムです。YOLOによる人物検出で自動録画を行い、検出前後の映像をUSBメモリに保存します。

## 📋 概要

このプロジェクトは **Python初学者向けの実践的な学習教材** として設計されています。AI・IoT・画像処理の基礎を1つのアプリケーションで体験できます。

### 主な機能
- 🎥 USBカメラによるリアルタイム映像監視
- 🤖 YOLOv5による人物検出
- 📹 検出前後5秒を含む自動録画
- 💾 USBメモリへの動画保存
- 📊 リアルタイムステータス表示

## 🛠️ システム要件

### ハードウェア
- Raspberry Pi 4 または 5
- USBカメラ（UVC対応）
- USBメモリ（FAT32またはexFAT形式）

### ソフトウェア
- Python 3.7以上
- Raspberry Pi OS（推奨）

## 📦 インストール

### 1. 必要なライブラリのインストール

```bash
# 基本ライブラリ
pip install opencv-python

# AI機能（YOLOv5）用ライブラリ
pip install torch torchvision ultralytics
```

### 2. プロジェクトのダウンロード

```bash
git clone <このリポジトリのURL>
cd entry-security-cam-pi
```

### 3. USBメモリの準備

USBメモリをFAT32またはexFAT形式でフォーマットし、Raspberry Piに接続してください。

## 🚀 使用方法

### 基本的な実行

```bash
python main.py
```

### カメラインデックスを指定して実行

```bash
# カメラが複数接続されている場合
python main.py 1
```

### 実行中の操作

- **Ctrl+C**: システム停止
- ターミナルにリアルタイムステータスが表示されます

## 📁 ファイル構成

```
entry-security-cam-pi/
├── main.py                 # メインスクリプト（全機能を含む）
├── models/                 # YOLOモデル格納ディレクトリ（オプション）
│   └── yolov5n.pt         # カスタムモデル（ある場合）
├── recordings/             # ローカル保存ディレクトリ（USBなし時）
├── README.md              # このファイル
├── 要件定義書.md           # 詳細仕様書
└── LICENSE                # ライセンス
```

## ⚙️ 設定

`main.py`内の`SecurityCamera`クラスで以下の設定を変更できます：

```python
camera = SecurityCamera(
    camera_index=0,              # USBカメラのインデックス
    buffer_seconds=5,            # 検出前の録画秒数
    recording_after_seconds=5,   # 検出後の録画秒数
    usb_mount_path="/media/pi"   # USBドライブのマウントパス
)
```

## 🎬 録画ファイル

### 保存場所
1. **USBメモリ**: `/media/pi/[USB名]/security_recordings/`
2. **ローカル**: `./recordings/`（USBが見つからない場合）

### ファイル名形式
```
security_YYYY-MM-DD_HH-MM-SS.mp4
例: security_2025-07-29_15-30-45.mp4
```

## 🔧 トラブルシューティング

### カメラが認識されない

```bash
# 接続されているカメラの確認
ls /dev/video*

# 権限の確認
sudo usermod -a -G video $USER
```

### YOLOライブラリのインストールエラー

```bash
# PyTorchの軽量版をインストール
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# または、YOLOなしで実行（すべてのフレームを録画）
python main.py  # YOLOなしでも動作します
```

### USBメモリが認識されない

```bash
# マウント状況の確認
df -h

# 手動マウント
sudo mkdir /media/usb
sudo mount /dev/sda1 /media/usb
```

## 📚 学習ポイント

このプロジェクトを通して以下を学習できます：

1. **Python基礎**
   - クラス設計
   - マルチスレッド処理
   - 例外処理

2. **画像処理**
   - OpenCVによるカメラ制御
   - 動画ファイルの作成・保存

3. **AI活用**
   - YOLOv5による物体検出
   - 事前学習済みモデルの利用

4. **IoT開発**
   - Raspberry Piでのリアルタイム処理
   - 外部ストレージとの連携

## 🔄 拡張案

- **GUI化**: tkinterやPyQt5での操作画面
- **Web UI**: Flaskによるブラウザ操作
- **通知機能**: Slack/LINE通知
- **クラウド連携**: AWS S3への自動アップロード

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🤝 貢献

バグ報告や機能提案はIssueでお願いします。プルリクエストも歓迎です。

## 📞 サポート

技術的な質問やトラブルについては、Issueでお気軽にお聞きください。

---

**🎓 Python学習教材として作成されています**  
初学者の方は、コード内のコメントを参考に、少しずつ理解を深めていってください。