from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline, creation_times_file, creation_times
from app.helper_functions import  delete_old_subdirectories, generate_item_description, delete_directory
from app.speechToText_model import speechToText_model
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
from pillow_heif import register_heif_opener
import io, json
import librosa
from fastapi.responses import FileResponse
import base64
import shutil
from collections import defaultdict


app = FastAPI(title='Link API')


class_counts = defaultdict(int)
class ImgIn(BaseModel):
    img: bytes
    
class DictOut(BaseModel):
    Result: dict
    

@app.get("/api_check")
def home():
    return{"Health Check": "OK", "Model_version": model_version}

def is_audio_file(filename):
    
    audio_extensions = ['mp3', 'wav', 'ogg'] 
    file_extension = filename.split('.')[-1].lower()
    return file_extension in audio_extensions

    
# @app.post("/predict", response_model=DictOut)
# async def upload_image(image_file: UploadFile = File(...), audio_file: UploadFile = File(None)):
#     global stored_image_path 
#     contents = await image_file.read()
#     register_heif_opener()    

#     try:
#         img = Image.open(io.BytesIO(contents)) 
#     except Exception as e:
#         image_file_error = True
#     else:
#         image_file_error = False

    
#     if not image_file_error:
#         image_predictions, image_relative_path = predict_pipeline(img, contents)
#         delete_old_subdirectories(creation_times_file, creation_times)
#         if not image_predictions['Detected_items']:
#             image_prediction_empty = True
#         else:
#             image_prediction_empty = False
    
#     if audio_file is not None:
        
#         try:
#             audio_contents = await audio_file.read()

#             if is_audio_file(audio_file.filename):
#                 audio_predictions = speechToText_model(audio_file, audio_contents)
                
#                 #audio_predictions = '{"Item":"test item"}'
#                 audio_file_error = False
#             else:
#                 audio_file_error = True
#         except Exception as e:
#             audio_file_error = True
#     else:
#         audio_file_error = False
#         audio_predictions = None
        

#     if image_file_error:
#         raise HTTPException(status_code=400, detail="Image file error: The supported image file formats are '.JPEG', '.PNG', '.HEIC' and 'WebP'. ")
#     if image_prediction_empty:
#         raise HTTPException(status_code=200, detail="No valid object detected: Please ensure a valid item is present in the image. Valid items include 'Doors', 'Windows', 'Sinks', 'Urinals', 'Ceiling Panals','Floor Tiles', 'Water Closets' and 'Partitions'.")
#     if audio_file_error:
#         raise HTTPException(status_code=400, detail="Audio file error: The supported audio file formats are '.mp3', '.wav' and '.ogg'.")

    
#     response_data = {
#         'Result':{
#             "Image": image_predictions,
#             "Audio": {  "Audio_available":"No",
#                         "Item": "",
#                         "Type": "",
#                         "Measurement": "",
#                         "Price": "",
#                         "Description": ""
#             }
#         }
#     }
#     if audio_predictions:
#         audio_predictions = json.loads(audio_predictions) 
        
#         if audio_file is None:
#             response_data['Result']['Audio']["Audio_available"] = 'No'
#         else:
#             response_data['Result']['Audio']["Audio_available"] = 'Yes'
#         response_data['Result']['Audio']["Item"] = audio_predictions.get("Item","")
#         response_data['Result']['Audio']["Type"] = audio_predictions.get("Type", "")
#         response_data['Result']['Audio']["Measurement"] = audio_predictions.get("Measurement", "")
#         response_data['Result']['Audio']["Price"] = audio_predictions.get("Price", "")
#         response_data['Result']['Audio']["Description"] = audio_predictions.get("Description", "")
    
#     return DictOut(**response_data)


from typing import List

@app.post("/predict", summary="Upload Image(s) and Audio File", response_model=DictOut)
async def upload_images_and_audio(images: List[UploadFile] = File(...), audio_file: UploadFile = File(None)):
    if len(images) > 10:
        raise HTTPException(status_code=400, detail=f"You have uploaded {len(images)} images. The limit is 10.")
    image_results = []
    
    for idx, image_file in enumerate(images):
        contents = await image_file.read()
        register_heif_opener()

        try:
            img = Image.open(io.BytesIO(contents))
        except Exception as e:
            image_file_error = True
        else:
            image_file_error = False

        if not image_file_error:
            image_predictions, image_relative_path = predict_pipeline(img, contents)
            delete_old_subdirectories(creation_times_file, creation_times)
            if not image_predictions['Detected_items']:
                image_prediction_empty = True
            else:
                image_prediction_empty = False

            # Append the image results to the list
            image_results.append({
                f"Image_{idx+1}": image_predictions
            })

    if image_file_error:
        raise HTTPException(status_code=400, detail="Image file error: The supported image file formats are '.JPEG', '.PNG', '.HEIC' and 'WebP'. ")
    if image_prediction_empty:
        raise HTTPException(status_code=200, detail="No valid object detected: Please ensure a valid item is present in the image. Valid items include 'Doors', 'Windows', 'Sinks', 'Urinals', 'Ceiling Panals','Floor Tiles', 'Water Closets' and 'Partitions'.")
    
    response_data = {
            'Result':{
                "Image": image_results,
                "Description": generate_item_description(class_counts),
                "Audio": {  "Audio_available":"No",
                            "Item": "",
                            "Type": "",
                            "Measurement": "",
                            "Price": "",
                            "Available From": "",
                            "Available To": "",
                            "Location": "",
                            "Summary": ""
                }
            }
        }
    
    

    if audio_file is not None:
    
       # try:
        audio_contents = await audio_file.read()

        if is_audio_file(audio_file.filename):
            audio_predictions = speechToText_model(audio_file, audio_contents)
            
            #audio_predictions = '{"Item":"test item"}'
            audio_file_error = False
        else:
            audio_file_error = True
        # except Exception as e:
        #     print('Masla yahan ha 2')
        #     audio_file_error = True
    else:
        
        audio_file_error = False
        audio_predictions = None
        

    if audio_file_error:
        raise HTTPException(status_code=400, detail="Audio file error: The supported audio file formats are '.mp3', '.wav' and '.ogg'.")

    
    
    if audio_predictions:
        audio_predictions = json.loads(audio_predictions) 
        
        if audio_file is None:
            response_data['Result']['Audio']["Audio_available"] = 'No'
        else:
            response_data['Result']['Audio']["Audio_available"] = 'Yes'
        response_data['Result']['Audio']["Item"] = audio_predictions.get("Item","")
        response_data['Result']['Audio']["Type"] = audio_predictions.get("Type", "")
        response_data['Result']['Audio']["Measurement"] = audio_predictions.get("Measurement", "")
        response_data['Result']['Audio']["Price"] = audio_predictions.get("Price", "")
        response_data['Result']['Audio']["Available From"] = audio_predictions.get("Available From", "")
        response_data['Result']['Audio']["Available To"] = audio_predictions.get("Available To", "")
        response_data['Result']['Audio']["Location"] = audio_predictions.get("Location", "")
        response_data['Result']['Audio']["Summary"] = audio_predictions.get("Summary", "")
    
    return DictOut(**response_data)






