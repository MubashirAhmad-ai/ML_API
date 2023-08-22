
import openai
import os
from app.helper_functions import create_directory, process_audio_file



def speechToText_model(audio, audio_contents):
    create_directory('audio_files')
    current_dir = os.path.abspath(os.getcwd())
    audio_directory_path = current_dir+'/audio_files'
    audio_file_path = audio_directory_path+'/'+audio.filename  
    
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_contents)
    
    # model = whisper.load_model("base")

    # result = whisper.transcribe(audio_file_path)
    audio_file= open(audio_file_path, "rb")
    # result = openai.Audio.transcribe("whisper-1", audio_file)
    result= process_audio_file(0.7, audio_file)
    return result

