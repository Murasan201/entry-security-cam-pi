#!/usr/bin/env python3
"""
玄関セキュリティシステム - メインスクリプト
Raspberry PiとUSBカメラを用いた人物検出・録画システム

必要なライブラリ:
pip install opencv-python torch torchvision ultralytics

使用方法:
python main.py
"""

import cv2
import time
import threading
import datetime
import os
from collections import deque
import sys

# YOLOv5のインポート（オプション）
try:
    import torch
    YOLO_AVAILABLE = True
    print("✓ YOLOライブラリが利用可能です")
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLOライブラリが見つかりません。人物検出機能は無効になります。")
    print("  pip install torch torchvision ultralytics でインストールしてください")


class SecurityCamera:
    """玄関セキュリティカメラシステム"""
    
    def __init__(self, 
                 camera_index=0,
                 buffer_seconds=5,
                 recording_after_seconds=5,
                 usb_mount_path="/media/pi"):
        """
        初期化
        
        Args:
            camera_index: USBカメラのインデックス番号
            buffer_seconds: 検出前に録画する秒数
            recording_after_seconds: 検出後に録画する秒数
            usb_mount_path: USBメモリのマウントパス
        """
        self.camera_index = camera_index
        self.buffer_seconds = buffer_seconds
        self.recording_after_seconds = recording_after_seconds
        self.usb_mount_path = usb_mount_path
        
        # カメラとYOLOモデルの初期化
        self.cap = None
        self.model = None
        
        # 設定値
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        
        # フレームバッファ（過去数秒分の映像保存用）
        buffer_size = self.fps * self.buffer_seconds
        self.frame_buffer = deque(maxlen=buffer_size)
        
        # 録画制御フラグ
        self.is_recording = False
        self.recording_start_time = None
        self.person_detected = False
        self.last_detection_time = 0
        
        # スレッド制御
        self.running = False
        
        # ログ出力制御
        self.last_status_time = 0
        
    def initialize_camera(self):
        """USBカメラの初期化"""
        print("カメラを初期化中...")
        
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception(f"カメラ(index: {self.camera_index})が開けません")
        
        # カメラ設定
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # 実際の設定値を取得
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"✓ カメラ初期化完了: {actual_width}x{actual_height}, {actual_fps}fps")
        
        # 実際の値で更新
        self.frame_width = actual_width
        self.frame_height = actual_height
        if actual_fps > 0:
            self.fps = actual_fps
            # バッファサイズを再計算
            buffer_size = self.fps * self.buffer_seconds
            self.frame_buffer = deque(maxlen=buffer_size)
    
    def initialize_yolo(self):
        """YOLOモデルの初期化"""
        if not YOLO_AVAILABLE:
            print("YOLOライブラリが利用できません")
            return False
        
        print("YOLOモデルを初期化中...")
        
        # モデルファイルの確認
        model_path = os.path.join("models", "yolov5n.pt")
        
        if os.path.exists(model_path):
            # ローカルモデルを使用
            try:
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
                print(f"✓ ローカルYOLOモデルをロード: {model_path}")
            except Exception as e:
                print(f"❌ ローカルモデルのロードエラー: {e}")
                return self._load_pretrained_model()
        else:
            # 事前学習済みモデルを使用
            return self._load_pretrained_model()
        
        # モデル設定
        self.model.conf = 0.5  # 信頼度閾値
        self.model.iou = 0.45  # IoU閾値
        
        print("✓ YOLOモデル初期化完了")
        return True
    
    def _load_pretrained_model(self):
        """事前学習済みモデルのロード"""
        try:
            print("事前学習済みYOLOv5nモデルをダウンロード中...")
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
            print("✓ 事前学習済みYOLOモデルをロード")
            return True
        except Exception as e:
            print(f"❌ YOLOモデルの初期化エラー: {e}")
            return False
    
    def detect_person(self, frame):
        """フレーム内の人物検出"""
        if self.model is None:
            return False
        
        try:
            # YOLOで推論実行
            results = self.model(frame)
            
            # 結果をパース
            detections = results.pandas().xyxy[0]
            
            # 'person'クラス（class=0）の検出があるかチェック
            person_detections = detections[detections['class'] == 0]
            
            return len(person_detections) > 0
        
        except Exception as e:
            print(f"検出エラー: {e}")
            return False
    
    def find_usb_drive(self):
        """USBドライブの検索"""
        # 一般的なマウントポイントをチェック
        possible_paths = [
            "/media/pi",
            "/mnt",
            "/media",
            "/Volumes"  # macOS
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                try:
                    # マウントされたデバイスを探す
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path) and os.access(item_path, os.W_OK):
                            return item_path
                except PermissionError:
                    continue
        
        # USBドライブが見つからない場合はローカルディレクトリを使用
        local_path = os.path.join(os.path.dirname(__file__), "recordings")
        return local_path
    
    def save_video(self, frames, filename):
        """フレームリストを動画ファイルとして保存"""
        if not frames:
            print("保存するフレームがありません")
            return False
        
        # 保存先ディレクトリの確認・作成
        usb_path = self.find_usb_drive()
        save_dir = os.path.join(usb_path, "security_recordings")
        
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception as e:
            print(f"❌ 保存ディレクトリ作成エラー: {e}")
            return False
        
        # 動画ファイルの作成
        video_path = os.path.join(save_dir, filename)
        
        # フレームサイズを最初のフレームから取得
        height, width = frames[0].shape[:2]
        
        # 動画コーデック設定
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, float(self.fps), (width, height))
        
        if not out.isOpened():
            print(f"❌ 動画ファイルを開けません: {video_path}")
            return False
        
        try:
            # 全フレームを書き込み
            for frame in frames:
                out.write(frame)
            
            out.release()
            
            # ファイルサイズを確認
            file_size = os.path.getsize(video_path)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✓ 動画保存完了: {filename} ({file_size_mb:.1f}MB)")
            print(f"  保存先: {save_dir}")
            return True
        
        except Exception as e:
            print(f"❌ 動画保存エラー: {e}")
            out.release()
            # エラー時はファイルを削除
            try:
                os.remove(video_path)
            except:
                pass
            return False
    
    def monitoring_loop(self):
        """メイン監視ループ"""
        detection_interval = 0.5  # 0.5秒間隔で検出
        last_detection_time = 0
        frame_count = 0
        
        print("監視ループを開始します...")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ フレーム取得エラー")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # フレームバッファに追加
            self.frame_buffer.append(frame.copy())
            
            # 人物検出（指定間隔で実行）
            current_time = time.time()
            if current_time - last_detection_time >= detection_interval:
                person_detected = self.detect_person(frame)
                last_detection_time = current_time
                
                if person_detected:
                    self.person_detected = True
                    self.last_detection_time = current_time
                    
                    if not self.is_recording:
                        # 録画開始
                        self.start_recording()
                
                # 録画中で人物が一定時間検出されない場合は録画停止
                elif self.is_recording and not person_detected:
                    time_since_detection = current_time - self.last_detection_time
                    if time_since_detection >= self.recording_after_seconds:
                        self.stop_recording()
            
            # ステータス表示（1秒間隔）
            if current_time - self.last_status_time >= 1.0:
                self.display_status(frame_count)
                self.last_status_time = current_time
                frame_count = 0
            
            # フレームレート制御
            time.sleep(1.0 / self.fps)
    
    def display_status(self, frame_count):
        """ステータス表示"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        if self.is_recording:
            recording_duration = time.time() - self.recording_start_time
            status = f"🔴 [{current_time}] 録画中 ({recording_duration:.1f}s) - FPS: {frame_count}"
        else:
            status = f"👁️  [{current_time}] 監視中 - FPS: {frame_count}"
        
        print(f"\r{status}", end="", flush=True)
    
    def start_recording(self):
        """録画開始"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recording_start_time = time.time()
        
        print(f"\n🔴 人物検出！録画開始 ({datetime.datetime.now().strftime('%H:%M:%S')})")
    
    def stop_recording(self):
        """録画停止と動画保存"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.person_detected = False
        
        # バッファ内の全フレームを取得
        frames_to_save = list(self.frame_buffer)
        
        # ファイル名生成（日時ベース）
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"security_{timestamp}.mp4"
        
        print(f"\n⏹️  録画停止 - 保存中...")
        
        # 別スレッドで動画保存（メインループをブロックしないため）
        save_thread = threading.Thread(
            target=self.save_video,
            args=(frames_to_save, filename),
            daemon=True
        )
        save_thread.start()
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
    
    def start(self):
        """システム開始"""
        print("=" * 50)
        print("🏠 玄関セキュリティシステム 開始")
        print("=" * 50)
        
        try:
            # カメラ初期化
            self.initialize_camera()
            
            # YOLO初期化
            yolo_success = self.initialize_yolo()
            if not yolo_success:
                print("⚠️  人物検出機能なしで続行します")
                print("   すべてのフレームが録画対象になります")
            
            # USBドライブ確認
            usb_path = self.find_usb_drive()
            print(f"💾 保存先: {usb_path}")
            
            # 監視開始
            self.running = True
            monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            monitoring_thread.start()
            
            print("\n✅ システム開始完了")
            print("📝 設定:")
            print(f"   - 検出前録画: {self.buffer_seconds}秒")
            print(f"   - 検出後録画: {self.recording_after_seconds}秒")
            print(f"   - フレームレート: {self.fps}fps")
            print(f"   - 解像度: {self.frame_width}x{self.frame_height}")
            print("\n🛑 終了するには Ctrl+C を押してください\n")
            
            # メインスレッドは待機
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 システム停止中...")
                self.cleanup()
                print("✅ システム停止完了")
        
        except Exception as e:
            print(f"\n❌ システムエラー: {e}")
            self.cleanup()
            return 1
        
        return 0


def main():
    """メイン関数"""
    # コマンドライン引数のチェック（簡易版）
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print("使用方法: python main.py [カメラインデックス]")
            return 1
    
    # セキュリティカメラシステムの開始
    camera = SecurityCamera(
        camera_index=camera_index,           # USBカメラのインデックス
        buffer_seconds=5,                    # 検出前の録画秒数
        recording_after_seconds=5,           # 検出後の録画秒数
        usb_mount_path="/media/pi"          # USBドライブのマウントパス
    )
    
    return camera.start()


if __name__ == "__main__":
    sys.exit(main())