
import openai
import os
from app.helper_functions import create_directory, delete_directory


openai.api_key = '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'

def process_audio_file(temperature, audio_file):
    system_prompt =  """You have been tasked with refining the accuracy of transcribed text related to a list of items and their details. Your primary responsibilities include:\
                    Rectifying any spelling errors in specific terms such as "Door," "Water Closet," "Partitions," "Window," "Urinal," "Ceiling Panels," "Floor Tiles," and "Pounds."\
                    Identifying and extract the following attributes from the corrected text: \
                    Item \
                    Type \
                    Measurement \
                    Price\
                    Description\
                    Your process should follow these guidelines:\
                    Correct any spelling discrepancies in the text.\
                    Extract the aforementioned attributes from the text keeping the attributes exact as above.\
                    If the Price is mentioned, convert it to numeric; otherwise, label it as "not mentioned."\
                    If a Measurement is specified, convert it to numeric with suitable units; otherwise, mark it as "not mentioned."\
                    Provide a concise two-line description for Description attribute\
                    The final output should be formatted in JSON format."""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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
    delete_directory('audio_files')
    return result

