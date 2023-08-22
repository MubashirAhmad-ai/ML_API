import os
import shutil
import openai
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
    #delete_directory('runs')
    os.remove(initial_path)
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
    class_info = defaultdict(lambda: {'Count': 0, 'Specific_code': ''})
    from app.main import class_counts
    

    for class_num, confidence in zip(boxes.cls, boxes.conf, ):
        class_num = int(class_num.item())
        class_info[classes[class_num]]['Count'] += 1
        class_info[classes[class_num]]['Specific_code'] = 'abc_123'
        item_name = classes[class_num]
        class_counts[item_name] += 1
        #class_info[classes[class_num]]['Confidence'].append(confidence.item())
    
    #item_descriptions={}

    # for item_name, count in class_counts.items():
    #     description = generate_item_description(item_name, count)
    #     class_info[item_name]['Description'] = description
    #     #item_descriptions[item_name] = description

    class_info = dict(class_info)  
    response = {
        'Image_URL': final_path,
        'Detected_items': class_info
    }
    return response



openai.api_key = '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'

def process_audio_file(temperature, audio_file):
    system_prompt =  """You have been tasked with refining the accuracy of transcribed text related to a list of items and their details. Your primary responsibilities include:\
                    Rectifying any spelling errors in specific terms such as "Door," "Water Closet," "Partitions," "Window," "Urinal," "Ceiling Panels," "Floor Tiles," and "Pounds."\
                    Identifying and extract the following attributes from the corrected text: \
                    Item \
                    Type \
                    Measurement \
                    Price \
                    Available From \
                    Available To \
                    Location \
                    Summary \
                    Your process should follow these guidelines:\
                    Correct any spelling discrepancies in the text.\
                    Extract the aforementioned attributes from the text keeping the attributes exact as above.\
                    If the Price is mentioned, convert it to numeric; otherwise, label it as "not mentioned."\
                    If a Measurement is specified, convert it to numeric with suitable units; otherwise, mark it as "not mentioned."\
                    If 'Available From' date is specified in the text, convert it to DD/MM/YYYY format; otherwise, mark the 'Available From' attribute as "not mentioned."\
                    If 'Available To' date is specified in the text, convert it to DD/MM/YYYY format; otherwise, mark the 'Available To' attribute as "not mentioned."\
                    If the Location is mentioned, convert it to suitable UK address format; otherwise, mark the 'Location' attribute as "not mentioned."\
                    Provide a concise two-line summary for Summary attribute\
                    The final output should be formatted in JSON format."""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": openai.Audio.transcribe("whisper-1", audio_file).text
            }
        ]
    )
    return response['choices'][0]['message']['content']



def generate_item_description(class_counts):
    # prompt = f"Create a description for {count} {item_name}(s) to be listed for sale:"
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=prompt,
    #     max_tokens=20,  
    #     temperature=0.7,  
    #     stop=None  
    # )
    # description = response.choices[0].text.strip()
    description_parts = []
    for item_name, count in class_counts.items():
        description_parts.append(f"{count} {item_name}(s)")
    if len(description_parts) > 1:
        description_parts[-1] = 'and ' + description_parts[-1]

    description = f"For sale: {', '.join(description_parts)}, in excellent condition"
    
    return description

