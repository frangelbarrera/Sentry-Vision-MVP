# Fine-Tuning Guide for Sentry Vision MVP

This guide explains how to fine-tune the YOLOv8n model for custom object detection, specializing it for your specific surveillance needs.

## Prerequisites
- Google Colab account (free GPU access)
- Roboflow account (for dataset annotation)
- Basic Python knowledge

## Step 1: Prepare Your Dataset

### Using Roboflow
1. Go to [Roboflow](https://roboflow.com/) and create an account.
2. Create a new project: "Sentry Custom Objects"
3. Upload images of your custom objects (e.g., specific tools, vehicles, etc.)
4. Annotate objects using Roboflow's annotation tool.
5. Generate dataset in YOLOv8 format.
6. Export as "YOLOv8 PyTorch" format.

### Alternative: Manual Annotation
Use tools like LabelImg to annotate images in YOLO format.

## Step 2: Fine-Tune in Google Colab

### Open Colab Notebook
1. Go to [Google Colab](https://colab.research.google.com/)
2. Create new notebook: "Sentry_Fine_Tuning.ipynb"

### Install Dependencies
```python
!pip install ultralytics roboflow
```

### Download Dataset
```python
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY")
project = rf.workspace("YOUR_WORKSPACE").project("sentry-custom-objects")
dataset = project.version(1).download("yolov8")
```

### Fine-Tune Model
```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('yolov8n.pt')

# Train on custom dataset
results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    name='sentry_custom'
)

# Validate
model.val()

# Export trained model
model.export(format='onnx')
```

### Download Trained Model
```python
from google.colab import files
files.download('runs/detect/sentry_custom/weights/best.pt')
files.download('runs/detect/sentry_custom/weights/best.onnx')
```

## Step 3: Integrate Custom Model

1. Place `best.pt` or `best.onnx` in the `models/` folder.
2. Update `config/config.yaml`:
   ```yaml
   detection:
     model: "models/best.pt"  # or best.onnx
   ```
3. Run Sentry Vision MVP as usual.

## Tips for Better Results

- **Dataset Size**: Aim for 100-500 images per class.
- **Annotation Quality**: Precise bounding boxes are crucial.
- **Augmentation**: Use Roboflow's built-in augmentations.
- **Training Time**: 50-100 epochs, monitor validation loss.
- **Hardware**: Use Colab's GPU for faster training.

## Example Use Cases

- **Retail**: Detect specific products or suspicious behavior.
- **Industrial**: Monitor machinery or safety equipment.
- **Home Security**: Recognize family members vs. intruders.

## Troubleshooting

- **Low Accuracy**: Increase dataset size or epochs.
- **Overfitting**: Add more augmentation or regularization.
- **Slow Inference**: Use ONNX export for optimization.

For more details, check [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/).