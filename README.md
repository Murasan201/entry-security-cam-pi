# Entry Security Camera System

A doorstep monitoring system using Raspberry Pi and USB camera. Features automatic recording with YOLO person detection, saving video clips before and after detection to USB storage.

## 📋 Overview

This project is designed as a **practical learning material for Python beginners**. Experience the fundamentals of AI, IoT, and image processing in a single application.

### Key Features
- 🎥 Real-time video monitoring with USB camera
- 🤖 Person detection using YOLOv5
- 📹 Automatic recording (5 seconds before/after detection)
- 💾 Video storage to USB drive
- 📊 Real-time status display

## 🛠️ System Requirements

### Hardware
- Raspberry Pi 4 or 5
- USB Camera (UVC compatible)
- USB Drive (FAT32 or exFAT format)

### Software
- Python 3.7+
- Raspberry Pi OS (recommended)

## 📦 Installation

### 1. Install Required Libraries

```bash
# Basic libraries
pip install opencv-python

# AI functionality (YOLOv5) libraries
pip install torch torchvision ultralytics
```

### 2. Clone the Project

```bash
git clone https://github.com/Murasan201/entry-security-cam-pi.git
cd entry-security-cam-pi
```

### 3. Prepare USB Drive

Format your USB drive to FAT32 or exFAT and connect it to the Raspberry Pi.

## 🚀 Usage

### Basic Execution

```bash
python main.py
```

### Specify Camera Index

```bash
# When multiple cameras are connected
python main.py 1
```

### Runtime Controls

- **Ctrl+C**: Stop system
- Real-time status is displayed in terminal

## 📁 File Structure

```
entry-security-cam-pi/
├── main.py                 # Main script (contains all functionality)
├── models/                 # YOLO model directory (optional)
│   └── yolov5n.pt         # Custom model (if available)
├── recordings/             # Local storage directory (when USB unavailable)
├── README.md              # This file
├── 要件定義書.md           # Detailed specifications (Japanese)
└── LICENSE                # License file
```

## ⚙️ Configuration

You can modify settings in the `SecurityCamera` class within `main.py`:

```python
camera = SecurityCamera(
    camera_index=0,              # USB camera index
    buffer_seconds=5,            # Recording seconds before detection
    recording_after_seconds=5,   # Recording seconds after detection
    usb_mount_path="/media/pi"   # USB drive mount path
)
```

## 🎬 Recording Files

### Storage Location
1. **USB Drive**: `/media/pi/[USB_NAME]/security_recordings/`
2. **Local**: `./recordings/` (fallback when USB not found)

### File Naming Format
```
security_YYYY-MM-DD_HH-MM-SS.mp4
Example: security_2025-07-29_15-30-45.mp4
```

## 🔧 Troubleshooting

### Camera Not Recognized

```bash
# Check connected cameras
ls /dev/video*

# Check permissions
sudo usermod -a -G video $USER
```

### YOLO Library Installation Error

```bash
# Install lightweight PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Or run without YOLO (records all frames)
python main.py  # Works without YOLO
```

### USB Drive Not Recognized

```bash
# Check mount status
df -h

# Manual mount
sudo mkdir /media/usb
sudo mount /dev/sda1 /media/usb
```

## 📚 Learning Points

This project helps you learn:

1. **Python Fundamentals**
   - Class design
   - Multi-threading
   - Exception handling

2. **Image Processing**
   - Camera control with OpenCV
   - Video file creation and saving

3. **AI Implementation**
   - Object detection with YOLOv5
   - Using pre-trained models

4. **IoT Development**
   - Real-time processing on Raspberry Pi
   - External storage integration

## 🔄 Extension Ideas

- **GUI**: User interface with tkinter or PyQt5
- **Web UI**: Browser-based control with Flask
- **Notifications**: Slack/LINE integration
- **Cloud Storage**: Automatic upload to AWS S3

## 👨‍💻 Developer

**Murasan** - [https://murasan-net.com/](https://murasan-net.com/)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Bug reports and feature requests are welcome through Issues. Pull requests are also appreciated.

## 📞 Support

For technical questions or troubleshooting, feel free to ask through Issues.

---

**🎓 Created as Python Learning Material**  
Beginners should refer to the comments in the code to gradually deepen their understanding.