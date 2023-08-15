import os
import shutil
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict
from itertools import repeat


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


def delete_directory(directory_to_delete):
    if os.path.exists(directory_to_delete):
        shutil.rmtree(directory_to_delete)
        
        
def load_creation_times(creation_times_file):
    try:
        with open(creation_times_file, "r") as file:
            creation_times_serializable = json.load(file)
            return {key: datetime.strptime(value, "%Y-%m-%d %H:%M:%S") for key, value in creation_times_serializable.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
    
def save_creation_times(creation_times_file,creation_times):
    creation_times_serializable = {key: value.strftime("%Y-%m-%d %H:%M:%S") for key, value in creation_times.items()}
    with open(creation_times_file, "w") as file:
        json.dump(creation_times_serializable, file)


def delete_old_subdirectories(creation_times_file, creation_times):
    current_time = datetime.now()
    for subdirectory, creation_time in list(creation_times.items()):
        time_difference = current_time - creation_time
        if time_difference >= timedelta(hours=24):
            if os.path.exists(os.path.abspath(os.getcwd())+'/'+subdirectory):
                os.remove(os.path.abspath(os.getcwd())+'/'+subdirectory)
                del creation_times[subdirectory] 
                save_creation_times(creation_times_file,creation_times) 
                     
                
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
        
        
def copy_unique_file(source_file, destination_dir):
    base_filename = os.path.basename(source_file)
    unique_filename = str(uuid.uuid4()) + os.path.splitext(base_filename)[1]
    current_dir = os.path.abspath(os.getcwd())
    join_path = current_dir+'/'+destination_dir
    target_file = os.path.join(join_path, unique_filename)
    shutil.copy(source_file, target_file)
    relative_url = destination_dir+unique_filename
    return target_file, relative_url


def image_preprocessing(img):
    resized_image = img.resize((640, 640))
    return resized_image



def loging_prediction(results, creation_times_file, creation_times):
    initial_path = results[0].save_dir+'/' + results[0].path
    absolute_path,relative_path  = copy_unique_file(initial_path, "predicted_images/")
    
    creation_times[relative_path] = datetime.now()
    save_creation_times(creation_times_file,creation_times)
    delete_directory('runs')
    return relative_path


# def formating_api_response(results,relative_path):
#     final_path = 'http://localhost:8080/'+relative_path
#     boxes = results[0].boxes
#     print('boxes[0] >>>>', boxes)
#     class_dict = defaultdict(lambda: {'count': 0, 'confidence': [], 'image_url':''})
#     for class_num, confidence, image_url in zip(boxes.cls, boxes.conf,repeat(final_path, len(boxes))):
#         class_num = int(class_num.item())
#         class_dict[classes[class_num]]['count'] += 1
#         class_dict[classes[class_num]]['confidence'].append(confidence.item())
#         class_dict[classes[class_num]]['image_url'] = image_url
#         class_dict = dict(class_dict)
#     return class_dict


def formating_api_response(results, relative_path):
    final_path = 'http://localhost:8080/' + relative_path
    boxes = results[0].boxes
    class_dict = defaultdict(lambda: {'count': 0, 'confidence': [], 'image_url': ''})

    for class_num, confidence in zip(boxes.cls, boxes.conf):
        class_num = int(class_num.item())
       
        class_dict[classes[class_num]]['count'] += 1
        class_dict[classes[class_num]]['confidence'].append(confidence.item())
        class_dict[classes[class_num]]['image_url'] = final_path

    class_dict = dict(class_dict)  #
    return class_dict