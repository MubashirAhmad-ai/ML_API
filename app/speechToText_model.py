import whisper
import openai
import os
from helper_functions import create_directory




def get_completion(prompt, model="gpt-3.5-turbo"): 
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def extract_info(text):
    # Set up API credentials
    openai.api_key = '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'

    # Define the prompt
    prompt = f"""Your task is to correct the text delimited in three backticks first and then extract the following from the corrected text\
            -Item \
            -Type \
            -Measurement \
            -Price \
            -Description \
            convert the Price to numeric and provide your response in JSON format. \
            text: ```{text}``` """

    response = get_completion(prompt)
    return response


def speechToText_model(audio, audio_contents):
    create_directory('audio_files')
    current_dir = os.path.abspath(os.getcwd())
    audio_directory_path = current_dir+'/audio_files'
    audio_file_path = audio_directory_path+audio.filename  # Construct the path
    print('audio_directory_path >>>>', audio_directory_path)
    print('audio_file_path >>>>', audio_file_path)
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_contents)
    model = whisper.load_model("base")

    result = model.transcribe("/Users/mubashirahmad/BDTI_Lab/Projects/LINK/LinkScripts/speechToText/door.wav")

    info = extract_info(result['text'])
    print('Detected Audio')
    print(result['text'])
    print(info)
    return info