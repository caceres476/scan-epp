![Visitor Count](https://profile-counter.glitch.me/vyasdeepti/count.svg)

# Personal Protective Equipment (PPE) Object Detection using YOLOv11

This project provides an advanced Personal Protective Equipment (PPE) detection system using the YOLOv11 deep learning architecture. The objective is to automate the process of identifying whether individuals in images or video streams are wearing essential PPE items such as helmets, vests, gloves, and masks. The system is designed for real-time applications and can be deployed in industrial, construction, healthcare, or any environment where safety compliance is critical.

## Objectives

- **Automate PPE Monitoring:** Reduce manual supervision by automatically detecting PPE compliance in real-time.
- **Enhance Workplace Safety:** Improve safety standards by providing instant alerts when PPE is missing.
- **Flexible Integration:** Allow users to train or fine-tune on custom datasets and integrate the model into varied workflows.
- **Scalability:** Support for multiple input types (images, video files, live camera), making the solution adaptable to different environments.

Input image: 

![00020_jpg rf abe4d0d5d5829754ec268692af2e7307](https://github.com/user-attachments/assets/cd082164-684a-4d9a-8033-8f20bf70b652)

Output image: 

![00020_jpg rf abe4d0d5d5829754ec268692af2e7307](https://github.com/user-attachments/assets/ca4fd7e2-d4ca-406a-8ea8-097a1fffa67b)

 
## Key Features

- **YOLOv11 Model Integration:** Leverages the state-of-the-art YOLOv11 deep learning model for real-time object detection.
- **Custom PPE Dataset Support:** Easily train or fine-tune the model on your own annotated PPE dataset.
- **Multi-Class Detection:** Capable of detecting multiple PPE types simultaneously (helmets, vests, gloves, masks, etc.).
- **Real-Time Processing:** Optimized for fast inference on images, video files, or live camera streams.
- **Visualization:** Draws bounding boxes and labels on detected items in output images or video.
- **Configurable Thresholds:** Adjust detection confidence and non-max suppression thresholds for your application needs.

## Example Use Cases

- Monitoring compliance in construction sites.
- Automated safety checks in factories or warehouses.
- Ensuring mask/gear usage in healthcare facilities.
- Real-time alerts for missing PPE in hazardous zones.

## Requirements

- Python 3.x
- Jupyter Notebook
- Deep learning libraries (e.g., PyTorch or TensorFlow)
- OpenCV, NumPy, and other standard dependencies


The `dataset` folder in the repository is structured for training a YOLOv11 model for PPE (Personal Protective Equipment) detection. Here is an explanation of the dataset's organization and content:

### 1. Top-level Contents
- **README.dataset.txt:**  
  Contains basic info about the dataset, including the source (Roboflow), date, and license (CC BY 4.0).  
  Example:  
  ```
  # PPE DETECTION > 2024-04-22 2:49am
  https://universe.roboflow.com/sdp-lfigk/ppe-detection-ozhfb
  
  Provided by a Roboflow user
  License: CC BY 4.0
  ```

- **README.roboflow.txt:**  
  Provides detailed info about the dataset:
  - Exported via Roboflow, with 2,114 images.
  - Annotated for: Hard_hat, boots, gloves, goggles (in YOLOv11 format).
  - Images are resized to 640x640, no additional augmentation.
  - Useful Roboflow links and general guidance on usage.

- **data.yaml:**  
  The configuration file for YOLO training/validation:
  ```yaml
  train: ../train/images
  val: ../valid/images
  test: ../test/images

  nc: 6
  names: ['Gloves', 'Hard_hat', 'Mask', 'Person', 'Safety_boots', 'Vest']

  roboflow:
    workspace: sdp-lfigk
    project: ppe-detection-ozhfb
    version: 14
    license: CC BY 4.0
    url: https://universe.roboflow.com/sdp-lfigk/ppe-detection-ozhfb/dataset/14
  ```
  - `train`, `val`, `test`: relative paths to image datasets.
  - `nc`: number of classes (6).
  - `names`: class labels.
  - `roboflow`: dataset origin metadata.

### 2. Subdirectories
- **train/**  
  Contains training images and their annotation files (usually `.jpg`/`.png` and `.txt` pairs in YOLO format).

- **valid/**  
  Contains validation images and annotations.

- **test/**  
  Contains test images and annotations.

### 3. Overall Structure
```
dataset/
│
├── README.dataset.txt        # Dataset overview, source, license
├── README.roboflow.txt       # Detailed dataset description from Roboflow
├── data.yaml                 # Dataset config for YOLO training
├── train/                    # Training set (images + labels)
├── valid/                    # Validation set (images + labels)
└── test/                     # Test set (images + labels)
```

### 4. Purpose
This structure is standard for object detection tasks using YOLO, making it easy to configure and train models. The dataset is well-documented and ready for use in machine learning pipelines.







---

### Cell 1
```python
!pip install tensorflow
```
- This cell installs the TensorFlow library using pip. TensorFlow is a popular open-source library for machine learning and deep learning tasks. The exclamation mark allows you to run shell commands directly from a Jupyter Notebook.

---

### Cell 2
```python
pip install tensorflow-gpu
```
- This cell attempts to install the GPU-enabled version of TensorFlow. Note: The command should be prefixed with an exclamation mark (`!pip install tensorflow-gpu`) to work in a Jupyter notebook. This version leverages GPU hardware for faster computations.

---

### Cell 3
```python
pip install nvidia-cuda-runtime-cu12
```
- This cell installs the NVIDIA CUDA Runtime version 12, which is required for running GPU-accelerated TensorFlow operations. Again, it should be prefixed with `!` for notebook execution.

---

### Cell 4
```python
!pip install ultralytics
from ultralytics import YOLO
createdmodel=YOLO("yolo11n.pt")
results= createdmodel.train(data="D:/YOLO-PPE-OBJECT DETECTION/dataset/data.yaml",epochs=8,imgsz=640)
```
- Installs the `ultralytics` package, which provides easy access to the YOLO (You Only Look Once) family of object detection models.
- Imports the YOLO class.
- Loads a YOLOv11 nano (`yolo11n.pt`) model.
- Trains the model on a custom dataset described by `data.yaml` for 8 epochs with image size 640x640. The path provided is for a local Windows directory.

---

### Cell 5
```python
#USING PRETRAINED MODEL
model_test=YOLO("runs/detect/train2/weights/best.pt")
results=model_test("test/images", save=True, imgsz=320, conf=0.7)
results[0].show()
```
- Loads the best trained model from a previous training run.
- Runs inference (object detection) on all images in the `test/images` directory.
- Saves the results and sets the image size to 320 and confidence threshold to 0.7.
- Displays the first result.

---

### Cell 6
```python
#USING PRETRAINED MODEL
model_test=YOLO("runs/detect/train2/weights/best.pt")
results=model_test("A building site labourer - 20 years ago Vs Today.mp4", save=True, imgsz=320, conf=0.7)
results[0].show()
```
- Loads the same trained model as in the previous cell.
- Runs object detection on a video file: "A building site labourer - 20 years ago Vs Today.mp4".
- Saves the results, sets the image size to 320, and confidence threshold to 0.7.
- Displays the first frame's detection results.



## Output Matrix

![confusion_matrix_normalized](https://github.com/user-attachments/assets/6b256d9d-8de1-4ba7-bc4a-464d67062be5)
![labels](https://github.com/user-attachments/assets/8c630f00-33a1-48a7-8d70-6bf31d66107f)
![results](https://github.com/user-attachments/assets/3b3aebe7-eaba-4262-85c6-c7a250dac059)
![PR_curve](https://github.com/user-attachments/assets/e6f1837f-f00b-492b-bbaa-d37623bc9090)


## References

- [YOLOv11 Paper/Repository](https://github.com/ultralytics/yolov11)  
- [YOLO Format Annotation Guide](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
- [Open Images Dataset](https://storage.googleapis.com/openimages/web/index.html) for pre-annotated PPE samples


















              
         
   
