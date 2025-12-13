#!/usr/bin/env python3
"""
Export YOLO model to ONNX format for optimized inference.
Usage: python src/export_model.py
"""

from ultralytics import YOLO
import logging
import os

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    model_path = 'models/yolov8n.pt'
    if not os.path.exists(model_path):
        logger.info("Downloading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        model.save(model_path)
    else:
        model = YOLO(model_path)

    logger.info("Exporting model to ONNX...")
    onnx_path = 'models/yolov8n.onnx'
    model.export(format='onnx', dynamic=True)
    logger.info(f"Model exported to {onnx_path}")

    # Verify
    if os.path.exists(onnx_path):
        logger.info("Export successful!")
    else:
        logger.error("Export failed.")

if __name__ == "__main__":
    main()