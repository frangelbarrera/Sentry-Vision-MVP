import cv2
import yaml
import argparse
import logging
import time
import os
import json
import threading
import psutil
import csv
from detector import Detector

def setup_logging(log_level, log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def draw_detections(frame, detections):
    for det in detections:
        if det['type'] == 'object':
            x1, y1, x2, y2 = det['bbox']
            tracked_id = det.get('tracked_id', 'N/A')
            label = f"ID:{tracked_id} {det['class']}: {det['confidence']:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif det['type'] == 'qr':
            points = det['polygon']
            cv2.polylines(frame, [points], True, (255, 0, 0), 2)
            cv2.putText(frame, det['data'], (points[0][0], points[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return frame

def update_dashboard_data(detections, fps):
    try:
        with open('data/dashboard_data.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"detections": [], "fps": 0, "last_update": ""}

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for det in detections:
        if det['type'] == 'object':
            x1, y1, x2, y2 = det['bbox']
            centroid_x = (x1 + x2) / 2
            centroid_y = (y1 + y2) / 2
            data['detections'].append({
                "timestamp": timestamp,
                "class": det['class'],
                "confidence": det['confidence'],
                "centroid": [centroid_x, centroid_y]
            })

    # Limit to last 100 detections
    data['detections'] = data['detections'][-100:]
    data['fps'] = fps
    data['last_update'] = timestamp

    with open('data/dashboard_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def audit_detection(frame, detection, config):
    if 'tracked_id' not in detection:
        return

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    class_name = detection['class']
    tracked_id = detection['tracked_id']
    confidence = detection['confidence']
    x1, y1, x2, y2 = detection['bbox']

    # Save crop
    crop = frame[y1:y2, x1:x2]
    crop_filename = f"{timestamp}_{class_name}_{tracked_id}.jpg"
    crop_path = os.path.join('data', 'events', crop_filename)
    cv2.imwrite(crop_path, crop)

    # Save to CSV
    csv_path = os.path.join('data', 'events', 'audit.csv')
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'class', 'confidence', 'bbox_coords', 'tracked_id', 'crop_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': timestamp.replace('_', ' '),
            'class': class_name,
            'confidence': confidence,
            'bbox_coords': f"{x1},{y1},{x2},{y2}",
            'tracked_id': tracked_id,
            'crop_path': crop_path
        })

def check_memory_usage(config, logger):
    memory = psutil.virtual_memory()
    usage_percent = memory.percent
    if usage_percent > config['performance']['ram_threshold']:
        logger.warning(f"High RAM usage: {usage_percent:.1f}% (threshold: {config['performance']['ram_threshold']}%)")

def main():
    parser = argparse.ArgumentParser(description="Sentry Vision MVP - Lightweight detection system.")
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to configuration file.')
    parser.add_argument('--source', type=int, default=None, help='Video source (overrides config).')
    parser.add_argument('--confidence', type=float, default=None, help='Confidence threshold (overrides config).')
    parser.add_argument('--log-level', type=str, default=None, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level.')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory for events (overrides default).')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    if args.source is not None:
        config['camera']['source'] = args.source
    if args.confidence is not None:
        config['detection']['confidence_threshold'] = args.confidence
    if args.log_level is not None:
        config['logging']['level'] = args.log_level
    if args.output_dir is not None:
        # Update paths if needed, but for simplicity, assume default

    setup_logging(config['logging']['level'], config['logging']['file'])
    logger = logging.getLogger(__name__)
    logger.info("Sentry Vision MVP started.")

    try:
        detector = Detector(config)
    except Exception as e:
        logger.critical(f"Could not initialize detector. Aborting. Error: {e}")
        return

    cap = cv2.VideoCapture(config['camera']['source'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])

    if not cap.isOpened():
        logger.error(f"Could not open camera with source: {config['camera']['source']}")
        return

    frame_count = 0
    start_time = time.time()
    last_log_time = start_time
    last_memory_check = start_time

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Could not read frame from camera. Attempting to reopen...")
            cap.release()
            time.sleep(2)
            cap = cv2.VideoCapture(config['camera']['source'])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
            if not cap.isOpened():
                logger.error("Failed to reopen camera. Continuing...")
            continue

        detections = detector.detect(frame)

        # Audit valid detections
        for det in detections:
            if det['type'] == 'object' and 'tracked_id' in det:
                audit_detection(frame, det, config)

        frame_with_detections = draw_detections(frame, detections)

        frame_count += 1
        current_time = time.time()
        fps = 0
        if (current_time - last_log_time) >= 1.0:
            fps = frame_count / (current_time - last_log_time)
            cv2.putText(frame_with_detections, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame_count = 0
            last_log_time = current_time

        # Check memory usage every 10 seconds
        if (current_time - last_memory_check) >= 10.0:
            check_memory_usage(config, logger)
            last_memory_check = current_time

        # Update dashboard data in separate thread to avoid blocking
        threading.Thread(target=update_dashboard_data, args=(detections, fps), daemon=True).start()

        cv2.imshow('Sentry Vision MVP', frame_with_detections)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    logger.info("Program ending.")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()