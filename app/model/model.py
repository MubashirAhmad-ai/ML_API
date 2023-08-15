from pathlib import Path
from ultralytics import YOLO
from app.helper_functions import formating_api_response, load_creation_times, save_creation_times
from app.helper_functions import create_directory, loging_prediction, image_preprocessing


__version__ = "0.1.0"

BASE_DIR = Path(__file__).resolve(strict=True).parent

model = YOLO(f'{BASE_DIR}/yolov8n-{__version__}.pt')

creation_times_file = "creation_times.json" 

creation_times = load_creation_times(creation_times_file)

save_creation_times(creation_times_file,creation_times)


def predict_pipeline(img,contents):
    create_directory('predicted_images') 
    processed_image = image_preprocessing(img)
    # results = model(resized_image)
    print('printing results before >>>>',results )
    results = model.predict(processed_image, save=True,save_txt=True)
    print('printing results >>>>>', results)
    print(results)
    image_relative_path = loging_prediction(results,creation_times_file, creation_times)
    response_dict = formating_api_response(results,image_relative_path)
    return response_dict, image_relative_path

