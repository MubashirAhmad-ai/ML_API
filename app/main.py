from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
import io
import os
import imghdr

app = FastAPI()


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
    
    # image_format = imghdr.what(None, h=contents)
    # if image_format is None:
    #      raise HTTPException(status_code=400, detail='Invalid file format.')
    
    img = Image.open(io.BytesIO(contents))
    
    

    # if image_format not in ["jpeg", "png", "bmp", "tiff", "gif", "webp"]:
    #     image_format = "jpeg"
    #     image = Image.open(io.BytesIO(contents))
    #     image = image.convert("RGB")
    #     converted_image = io.BytesIO()
    #     image.save(converted_image, format="JPEG")
    #     converted_image.seek(0)
    #     image = Image.open(converted_image)
    #     predictions = predict_pipeline(image) 
        
    # else:
        
    predictions = predict_pipeline(img)
    
    return DictOut(clas=predictions)
        
    

