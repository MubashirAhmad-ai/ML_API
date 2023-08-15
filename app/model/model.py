from pathlib import Path
from ultralytics import YOLO
import shutil
from itertools import repeat
from PIL import Image
from collections import defaultdict


__version__ = "0.1.0"

BASE_DIR = Path(__file__).resolve(strict=True).parent

model = YOLO(f'{BASE_DIR}/yolov8n-{__version__}.pt')


classes = [
    'Ceiling_Panel',
    'Door',
    'Floor_Tiles',
    'Sink',
    'Ceramic Urinal',
    'Stainless Urinal',
    'water_closet',
    'Window',
    'Partition'
    ]

def predict_pipeline(img,contents):

    resized_image = img.resize((640, 640))
    # results = model(resized_image)
    results = model.predict(resized_image, save=True,save_txt=True)
    
    initial_path = results[0].save_dir+'/' + results[0].path
    start_index = initial_path.find("/detect/predict")
    intermediate_path = initial_path[start_index:]
    final_path = 'http://localhost:8080'+intermediate_path 
    
    boxes = results[0].boxes
    class_dict = defaultdict(lambda: {'count': 0, 'confidence': [], 'image_url':''})
    
    for class_num, confidence, image_url in zip(boxes.cls, boxes.conf,repeat(final_path, len(boxes))):
        class_num = int(class_num.item())
        class_dict[classes[class_num]]['count'] += 1
        class_dict[classes[class_num]]['confidence'].append(confidence.item())
        class_dict[classes[class_num]]['image_url'] = image_url
    class_dict = dict(class_dict)
    
    return class_dict, initial_path 

