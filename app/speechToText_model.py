
import os
from app.helper_functions import create_directory, process_audio_file
from fastapi import HTTPException
import uuid


def speechToText_model(audio, audio_contents):
    create_directory('audio_files')
    current_dir = os.path.abspath(os.getcwd())
    audio_directory_path = current_dir+'/audio_files'
    #audio_file_path = audio_directory_path+'/'+audio.filename  
    
    file_extension = os.path.splitext(audio.filename)[1]  
    unique_filename = str(uuid.uuid4()) + file_extension
    audio_file_path = os.path.join(audio_directory_path, unique_filename)
    
    
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_contents)
    
    # model = whisper.load_model("base")

    # result = whisper.transcribe(audio_file_path)
    audio_file= open(audio_file_path, "rb")
    # result = openai.Audio.transcribe("whisper-1", audio_file)
    try:
        result= process_audio_file(0.7, audio_file)
    except:
        os.remove(audio_file_path)
        raise HTTPException(status_code=400, detail="Audio processing engine is not responding")

    return result

