from pathlib import Path
from ultralytics import YOLO

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
    results = model(resized_image)
    model.predict(resized_image, save=True,save_txt=True)
    print('******************************************** the LATEST UPDATE NOW************** ')
    
    boxes = results[0].boxes
    class_dict = defaultdict(lambda: {'count': 0, 'confidence': []})
    
    for class_num, confidence in zip(boxes.cls, boxes.conf):
        class_num = int(class_num.item())
        class_dict[classes[class_num]]['count'] += 1
        class_dict[classes[class_num]]['confidence'].append(confidence.item())

    class_dict = dict(class_dict)
    
    # for class_name, class_data in class_dict.items():
    #     for confidence in class_data['confidence']:
    #         box = boxes[class_data['count']]
    #         img = Image.open(img)
    #         img.draw_bounding_box(box.tolist(), class_name, confidence)

    
    
    return class_dict #, img

