from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
from pillow_heif import register_heif_opener
import io
import base64
import shutil
#import pyheif

app = FastAPI(title='Link API')


class ImgIn(BaseModel):
    img: bytes
    
class DictOut(BaseModel):
    clas: dict
    
@app.get("/")
def home():
    return{"Health Check": "OK", "Model_version": model_version}



@app.post("/predict", response_model= DictOut)
async def upload_image(file: UploadFile = File(...)):
    
    contents = await file.read()
    
    register_heif_opener()    
    
    try:
        img = Image.open(io.BytesIO(contents))
        
    except Exception as e:
          raise HTTPException(status_code=400, detail="The uploaded file is not an image. Please upload a valid image file.")


        
    predictions= predict_pipeline(img,contents)
    
        
    # image_path = "/Users/mubashirahmad/BDTI_Lab/Projects/LINK/ML_API/runs/detect/predict/image0.jpg"
    # image = Image.open(image_path)
    # image_base64 = base64.b64encode(image.tobytes()).decode("utf-8")
    # return DictOut(clas=predictions, image=image_base64) 
    
    return DictOut(clas=predictions) #, image=image_base64)  

