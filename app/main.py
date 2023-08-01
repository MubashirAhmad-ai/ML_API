from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from app.model.model import predict_pipeline
from app.model.model import __version__ as model_version
from PIL import Image,UnidentifiedImageError
from pillow_heif import register_heif_opener
import io
import os
#import pyheif

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
    
    register_heif_opener()    
    # jpg_file = os.path.basename(file.filename).replace(".HEIC", ".jpg")    
    # print('*********************',jpg_file,'***********************')

    # img = Image.open(io.BytesIO(contents))
    # img.save(jpg_file)
    
    try:
        img = Image.open(io.BytesIO(contents))
        
    except Exception as e:
          raise HTTPException(status_code=400, detail="The uploaded file is not an image. Please upload a valid image file.")

    

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
        
    predictions= predict_pipeline(img,contents)
    
    # img_bytes = io.BytesIO()
    # processed_img.save(img_bytes, format="JPEG")
    # img_bytes.seek(0)
    
    
    
    
    
    return DictOut(clas=predictions) #, img=img_bytes.getvalue()
        
    

