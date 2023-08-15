from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline, creation_times_file, creation_times
from app.helper_functions import  delete_old_subdirectories
from app.speechToText_model import speechToText_model
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
from pillow_heif import register_heif_opener
import io, json
import librosa
from fastapi.responses import FileResponse
import base64
import shutil


app = FastAPI(title='Link API')


class ImgIn(BaseModel):
    img: bytes
    
class DictOut(BaseModel):
    Result: dict
    

@app.get("/")
def home():
    return{"Health Check": "OK", "Model_version": model_version}

def is_audio_file(filename):
    audio_extensions = ['mp3', 'wav', 'flac', 'ogg'] 
    file_extension = filename.split('.')[-1].lower()
    return file_extension in audio_extensions

    
@app.post("/predict", response_model=DictOut)
async def upload_image(image_file: UploadFile = File(...), audio_file: UploadFile = File(None)):
    global stored_image_path 
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
        if not image_predictions:
            image_prediction_empty = True
        else:
            image_prediction_empty = False
    
    if audio_file is not None:
        try:
            audio_contents = await audio_file.read()

            if is_audio_file(audio_file.filename):
                audio_predictions = speechToText_model(audio_file, audio_contents)
                print(audio_predictions)
                #audio_predictions = '{"Item":"test item"}'
                audio_file_error = False
            else:
                audio_file_error = True
        except Exception as e:
            audio_file_error = True
    else:
        audio_file_error = False
        audio_predictions = None
        

    if image_file_error:
        raise HTTPException(status_code=400, detail="Image error: The uploaded file is not a valid image file")
    if image_prediction_empty:
        raise HTTPException(status_code=400, detail="No object detected, Please take a better photo.")
    if audio_file_error:
        raise HTTPException(status_code=400, detail="Audio error: The uploaded file is not a valid audio file.")

    
    response_data = {
        'Result':{
            "Image": image_predictions,
            "Audio":"No",
            "Item": "",
            "Type": "",
            "Measurement": "",
            "Price": "",
            "Description": ""
        }
    }
    if audio_predictions:
        audio_predictions = json.loads(audio_predictions) 
        print(audio_predictions)
        if audio_file is None:
            response_data['Result']["Audio"] = 'No'
        else:
            response_data['Result']["Audio"] = 'Yes'
        response_data['Result']["Item"] = audio_predictions.get("Item","")
        response_data['Result']["Type"] = audio_predictions.get("Type", "")
        response_data['Result']["Measurement"] = audio_predictions.get("Measurement", "")
        response_data['Result']["Price"] = audio_predictions.get("Price", "")
        response_data['Result']["Description"] = audio_predictions.get("Description", "")
    
    return DictOut(**response_data)





