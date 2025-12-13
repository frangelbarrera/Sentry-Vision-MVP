import cv2
import numpy as np
from ultralytics import YOLO
import logging
from collections import defaultdict
import math
import os
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

class CentroidTracker:
    def __init__(self, max_disappeared=30, max_distance=50):
        self.next_object_id = 0
        self.objects = {}  # ID -> centroid
        self.disappeared = {}  # ID -> frames disappeared
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, centroids):
        if len(centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        if len(self.objects) == 0:
            for centroid in centroids:
                self.register(centroid)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Compute distance matrix
            D = np.zeros((len(object_centroids), len(centroids)))
            for i, object_centroid in enumerate(object_centroids):
                for j, centroid in enumerate(centroids):
                    D[i, j] = math.dist(object_centroid, centroid)

            # Find best matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > self.max_distance:
                    continue
                object_id = object_ids[row]
                self.objects[object_id] = centroids[col]
                self.disappeared[object_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            # Register new centroids
            unused_cols = set(range(len(centroids))) - used_cols
            for col in unused_cols:
                self.register(centroids[col])

            # Mark disappeared
            unused_rows = set(range(len(object_centroids))) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

        return self.objects

class Detector:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Check for ONNX model first
        onnx_path = os.path.join('models', 'yolov8n.onnx')
        if ONNX_AVAILABLE and os.path.exists(onnx_path):
            self.logger.info("Loading ONNX model for optimized inference.")
            self.ort_session = ort.InferenceSession(onnx_path)
            self.yolo_model = None  # Not using YOLO object
            self.use_onnx = True
        else:
            try:
                self.yolo_model = YOLO(self.config['detection']['model'])
                self.logger.info(f"YOLO model loaded: {self.config['detection']['model']}")
                self.use_onnx = False
            except Exception as e:
                self.logger.error(f"Error loading YOLO model: {e}")
                raise

        self.qr_detector = cv2.QRCodeDetector()
        self.logger.info("QR code detector initialized.")

        # Initialize tracker
        self.tracker = CentroidTracker(max_distance=self.config['detection']['tracking_threshold'])

        # Debounce counters: key -> (count, last_bbox)
        self.debounce_counters = defaultdict(lambda: [0, None])

    def detect(self, frame):
        results = []

        yolo_results = self.yolo_model.predict(
            frame,
            conf=self.config['detection']['confidence_threshold'],
            iou=self.config['detection']['iou_threshold'],
            verbose=False
        )

        current_centroids = []
        raw_detections = []

        for result in yolo_results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls)
                if cls in self.config['detection']['target_classes']:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf)
                    class_name = self.yolo_model.names[cls]
                    centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
                    current_centroids.append(centroid)
                    raw_detections.append({
                        'type': 'object',
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': (x1, y1, x2, y2),
                        'centroid': centroid
                    })

        # Update tracker
        tracked_objects = self.tracker.update(current_centroids)

        # Apply debounce and assign tracked IDs
        for det in raw_detections:
            key = tuple(det['bbox'])  # Approximate key
            count, last_bbox = self.debounce_counters[key]
            if count < self.config['detection']['debounce_frames'] - 1:
                self.debounce_counters[key][0] += 1
                continue  # Not yet valid
            else:
                # Find closest tracked ID
                min_dist = float('inf')
                tracked_id = None
                for obj_id, centroid in tracked_objects.items():
                    dist = math.dist(det['centroid'], centroid)
                    if dist < min_dist:
                        min_dist = dist
                        tracked_id = obj_id
                if tracked_id is not None:
                    det['tracked_id'] = tracked_id
                    results.append(det)
                    self.debounce_counters[key] = [0, det['bbox']]  # Reset for valid detection

        # Clean old debounce counters
        to_remove = [k for k, (c, _) in self.debounce_counters.items() if c == 0]
        for k in to_remove:
            del self.debounce_counters[k]

        if self.config['qr_detection']['enabled']:
            data, points, _ = self.qr_detector.detectAndDecode(frame)
            if data:
                points = points[0].astype(int)
                results.append({
                    'type': 'qr',
                    'data': data,
                    'polygon': points
                })

        return results