# Sentry Vision MVP

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12+-green.svg)](https://opencv.org/)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLOv8-orange.svg)](https://ultralytics.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

A lightweight, real-time surveillance system designed for resource-constrained hardware. Perfect for security cameras, detecting people, cell phones, laptops, and QR codes with minimal latency and power consumption.

## 🚀 Key Features

- **Real-Time Detection**: Instant identification of people, objects, and QR codes using YOLOv8/ONNX.
- **Object Tracking**: Centroid-based tracking with unique IDs for consistent monitoring.
- **Debounce Logic**: Temporal filtering to reduce false positives.
- **Audit System**: Automatic saving of detection crops and CSV logs for forensics.
- **Low Resource Usage**: Optimized for CPUs with < 1GB RAM and 10-20 FPS on modest hardware.
- **Analytics Dashboard**: Web-based interface for real-time monitoring and data analysis.
- **Configurable**: YAML-based configuration with CLI overrides.
- **Security Focused**: Designed for surveillance with error handling and memory monitoring.
- **Optimization**: ONNX support for 20-30% performance boost.
- **Packaging**: Standalone executable with PyInstaller.
- **Fine-Tuning Ready**: Guide for custom model training.
- **Cross-Platform**: Windows/Linux compatible with automated setup.

## 📊 Performance Metrics

| Metric | PyTorch Model | ONNX Model | Notes |
|--------|---------------|------------|-------|
| **FPS** | 10-15 | 15-20 | Real-time performance |
| **RAM Usage** | 500-800 MB | 400-700 MB | Peak during inference |
| **Latency** | < 100ms | < 80ms | Per frame |
| **Startup Time** | 5-10 seconds | 3-8 seconds | Model loading |
| **Accuracy** | 85-95% | 85-95% | Target classes |
| **CPU Load** | 20-40% | 15-35% | Quad-core systems |

**Minimum Requirements:** Python 3.10+, 4GB RAM, CPU with AVX support. No GPU required.


**Why It Excels for Security Cameras:**
- **Efficiency**: Runs 24/7 on low-power devices without overheating.
- **Reliability**: Robust error handling for camera failures and network issues.
- **Scalability**: Easy to deploy on multiple cameras with centralized logging.
- **Cost-Effective**: No GPU required, works on affordable hardware.
- **Optimization**: ONNX support for 20-30% performance boost.

## 🎥 Demo

Soon

## 🛠 Installation

### Prerequisites
- Python 3.10 or higher
- Webcam or IP camera
- Internet connection for initial model download

### Quick Setup (Windows)
1. Clone or download the repository.
2. Run the automated setup script:
   ```bash
   run_sentry.bat
   ```
   This will install dependencies and start the system.

### Manual Installation
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the detection system:
   ```bash
   python src/vision_mvp.py
   ```

## 🎯 Usage

### Basic Operation
1. Execute `python src/vision_mvp.py` or `run_sentry.bat`.
2. Point your camera at areas to monitor.
3. View real-time detections in the video window.
4. Press 'q' to exit.

### Command Line Options
```bash
python src/vision_mvp.py --config config/config.yaml --source 1
```
- `--config`: Path to configuration file
- `--source`: Camera source index (0 for default webcam)

### Analytics Dashboard
Run the dashboard for detailed insights:
```bash
streamlit run src/dashboard.py
```
Access at `http://localhost:8501` to view:
- Live FPS and detection counts
- Class-wise detection statistics
- Movement pattern visualizations
- Recent detection logs

## 🏗 Architecture

```
sentry_vision_mvp/
├── src/
│   ├── detector.py          # YOLO and QR detection logic
│   ├── vision_mvp.py        # Main application loop
│   └── dashboard.py         # Streamlit analytics interface
├── config/
│   └── config.yaml          # Configuration settings
├── models/                  # Downloaded YOLO models
├── logs/                    # Application logs
├── data/
│   ├── dashboard_data.json  # Real-time analytics data
│   └── events/              # Future event storage
├── requirements.txt         # Python dependencies
├── run_sentry.bat           # Windows setup script
└── run_dashboard.bat        # Dashboard launcher
```

### Core Components
- **Detector Class**: Handles YOLO inference and QR scanning.
- **Main Loop**: Captures video, processes frames, updates dashboard.
- **Configuration**: Centralized YAML for thresholds and settings.
- **Dashboard**: Web app for monitoring and analysis.

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
camera:
  source: 0          # Camera index
  width: 640         # Resolution
  height: 480

detection:
  model: "yolov8n.pt"  # YOLO model
  confidence_threshold: 0.5
  target_classes: [0, 67, 73]  # person, cell phone, laptop

qr_detection:
  enabled: true

performance:
  target_fps: 15
```

## 📈 Analytics & Insights

The dashboard provides:
- **Real-Time Metrics**: FPS, detection counts, timestamps.
- **Movement Tracking**: Centroid plots for object trajectories.
- **Historical Data**: Last 100 detections with confidence scores.
- **Export Ready**: Data stored in JSON for further analysis.

Perfect for security analysis, identifying patterns, and generating reports.

## 📋 Project Phases Completed

This project was developed in three phases:

### Phase 1: Foundations
- Basic YOLO detection, configuration, logging, FPS display.
- Baseline performance metrics.

### Phase 2: Robustness & Tracking
- Debounce logic, centroid tracking, audit system.
- Advanced error handling and memory monitoring.

### Phase 3: Optimization & Packaging
- ONNX support, CLI enhancements, executable building.
- Fine-tuning guide and professional documentation.

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m 'Add feature'`.
4. Push to branch: `git push origin feature-name`.
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com/) for YOLOv8
- [OpenCV](https://opencv.org/) for computer vision
- [Streamlit](https://streamlit.io/) for the dashboard

---


**Built for efficient, reliable surveillance on a budget.** 🚀


## 👤 Author
[Frangel Barrera](https://github.com/frangelbarrera)
