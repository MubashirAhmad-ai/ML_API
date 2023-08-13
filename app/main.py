from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline, creation_times_file, creation_times
from app.helper_functions import  delete_old_subdirectories
from app.speechToText_model import speechToText_model
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
from pillow_heif import register_heif_opener
import io, os

from fastapi.responses import FileResponse
import base64
import shutil


app = FastAPI(title ='Link API')


class ImgIn(BaseModel):
    img: bytes
    
class DictOut(BaseModel):
    clas: dict
    

@app.get("/")
def home():
    return{"Health Check": "OK", "Model_version": model_version}


@app.post("/predict", response_model= DictOut)
async def upload_image(file: UploadFile = File(...), audio: UploadFile = File(...)):
    global stored_image_path 
    contents = await file.read()
    register_heif_opener()    
    try:
        img = Image.open(io.BytesIO(contents)) 
    except Exception as e:
        raise HTTPException(status_code=400, detail="The uploaded file is not an image. Please upload a valid image file.")
    predictions, stored_image_path = predict_pipeline(img,contents)
    delete_old_subdirectories(creation_times_file, creation_times)
    if not predictions:
        raise HTTPException(status_code=400, detail="No Object Found, Please take a better photo.")

    if audio is not None:
        audio_contents = await audio.read()
        audio_predictions = speechToText_model(audio_contents)
        
    
    response_data = {
        "clas": predictions,
        "Item": audio_predictions.get("item", ""),
        "Type": audio_predictions.get("type", ""),
        "Measurement": audio_predictions.get("measurement", ""),
        "Price": audio_predictions.get("price", ""),
        "Description": audio_predictions.get("description", "")
    }
    
    
    #image = Image.open(stored_image_path)
    #image_base64 = base64.b64encode(image.tobytes()).decode("utf-8")
    return DictOut(**response_data) #DictOut(clas=predictions)#, image=image_base64) 
    
    
# @app.get("/image")
# async def get_image():
#     if not os.path.exists(stored_image_path):
#         raise HTTPException(status_code=404, detail="Image not found")

#     return FileResponse(stored_image_path)
