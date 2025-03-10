from flask import Flask, request, jsonify, render_template_string
from io import BytesIO
import speech_recognition as sr
import base64
import requests
import logging
import datetime
import os
from logging import Logger

import wave
import io
from text_to_speech import convert_tts_into_audio_file, convert_mp3_to_wav, read_speech_from_audio_file

from lm_studio_provider import LMStudioProvider
from ollama_provider import OllamaProvider

from modules.module_loader import load_modules, find_and_execute_module
import threading



app = Flask(__name__)

# Setup Logger

# Ensure the data directory exists
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Initialize provider and working memory
# provider = LMStudioProvider()
provider = OllamaProvider()


# Load profile and prompt data
profile_data = "be knowledgeable in all areas needed for providing the response, pulling from vast cross domain information if needed."
try:
    with open("profiles/default.txt", "r") as file:
        profile_data = file.read()
except FileNotFoundError as e:
    print("Error loading profile data:", e)

prompt_data = "do not meander in reply, giving only the relevant information in a concise form"
try:
    with open("prompts/default.txt", "r") as file:
        prompt_data = file.read()
except FileNotFoundError as e:
    print("Error loading prompt data:", e)

@app.route('/', methods=['GET'])
def home():
    template = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Flask Template as String</title>
      </head>
      <body>
        <div class="container">
          <h1>Welcome to Flask!</h1>
          <p>This is a simple template rendered from a string.</p>
        </div>
      </body>
    </html>
    """
    return render_template_string(template)

@app.route('/llm', methods=['POST'])
def process_request():
    print("Got in request")
    #check the status code if not 200 return error
    if request.method != 'POST':
        return jsonify({"error": "Invalid request"}), 200
    
    if 'audio' not in request.files or 'image' not in request.files:
        return jsonify({"error": "Missing audio or image file"}), 200
    if 'location' not in request.form or 'time' not in request.form or 'messages' not in request.form:
        return jsonify({"error": "Missing form data"}), 200

    # 1. Handle response from client
    # 2. Exchange communication with LLM
    # 3. Convert LLM response to Audio
    # 4. Prepare response for client
    # 5. Return JSON response to client
    
    # 1. HANDLE Response from Client

    # PARSE response FROM Client
    audio = request.files['audio']
    image = request.files['image']
    location = request.form['location']
    time = request.form['time']
    messages = request.form['messages']
    custom_prompt = request.form.get('custom_prompt', prompt_data)
    
    #_# `IF` Audio is present, TRANSCRIBE Input Audio from Client
    # Convert files to base64
    audio_base64 = base64.b64encode(audio.read()).decode('utf-8')
    image_base64 = base64.b64encode(image.read()).decode('utf-8')

    # Decode base64 audio and image
    audio_data = base64.b64decode(audio_base64)
    image_data = base64.b64decode(image_base64)

    # Process audio data (transcribe)
    audio_result = transcribe_audio(audio_data)
    print(audio_result)

    #--# Load and execute relevant modules
    modules = load_modules()
    module_data = find_and_execute_module(modules, audio_result, provider)
    #module_data = ingestToAllModules(audio_result, provider)
    
    #_# `IF` Video is present, GENERATE Context from scene
    # Send image data to LM Studio vision model, or don't because until the camera works better in lighting situations, this will clog up and muddy the results by giving false seeds to memories.
    vision_data = "" #get_vision_data(image_base64, "Extract relevant information from the image, describe the scene, elements within it, any text present, etc. The goal is to encode the scene in a narrative as though from memory. This should be a brief description of the image, not a lengthy one. Simple and sweet, under 200 words or less.")
    
    # PREPARE messages for LLM chat model inference
    chat_messages = [
        {"role": "system", "content": profile_data},
        {"role": "user", "content": custom_prompt},
        {"role": "user", "content": f"request from Audio transcription: {audio_result}"},
        #{"role": "user", "content": f"relevant image data, if any description: {vision_data}"}
        {"role": "user", "content": "shorten any replies to only a sentence or four long, so make sure to be quick and to the point, only giving the relevant information, this is for use on a small HUD display whatever response format is given."} #tune this to refine responses for the frame
    ]

    # Convert audio_result response from lm studio to audio and deliver it to the user
    # audio_base64 = get_audio_data(audio_result, "audio/wav")

    # Include module data if any
    if module_data:
        chat_messages.append({"role": "user", "content": f"Relevant data: {module_data}"})

    #### ------------------------ ####

    ## 2. EXCHANGE Communication with LLM

    # Send data to local LM Studio chat model
    try:
        lm_data = provider.send_request(chat_messages, 0.7)
    except Exception as err:
        return "Failed to communicate with model"

    #### ------------------------ ####

    ### 3. CONVERT LLM Response into Audio

    # Convert response from LLM text into audio wav file
    convert_tts_into_audio_file(lm_data)
    convert_mp3_to_wav('audio_response/last_response.mp3')

    # Read the audio file and convert it to base64 to be delivered in response
    base64str = read_speech_from_audio_file('audio_response/last_response.wav')

    ## UNUSED for now
    # base64str = read_wav_files_from_directory('audio_responses')

    #### ------------------------ ####

    #### 4. PREPARE Response to Client
    # Format the response
    response = {
        'user_prompt': audio_result,
        'message': lm_data,
        'image': image_base64, 
        # 'audio': audio_base64,
        'audio': base64str,
        'debug': {
            'topic_changed': False,
            'info': "response from NoaRouter request: " + audio_result + " response: " + lm_data
        }
    }
    
    # Log request to working memory
    request_data = {
        "audio_transcription": audio_result,
        "vision_transcription": vision_data,
        "location": location,
        "time": time,
        "messages": messages,
        "lm_data": "",
        "imgdata": image_base64,
        "audiodata": audio_base64
        
    }
    #mem.save_contextual_memory(request_data) #all memories available for contextual content pulling, a rolling window of relevancy, and a longer term memory to pull from later if needed. 

    return jsonify(response)

def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    audio_file = BytesIO(audio_data)
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        transcription = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        transcription = "Could not understand audio"
    except sr.RequestError as e:
        transcription = f"Could not request results; {e}"
    return transcription

    # Audio data is stored across multiple audio files in directory "audio_responses". Iterate over all files in target directory and return all audio as single base64 string
def read_wav_files_from_directory(directory):
    base64str = ""
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            with open(os.path.join(directory,filename), "rb") as f:
                base64str += base64.b64encode(f.read()).decode("utf-8") + ","
    print(f"Retrieved Audio files from directory: {directory})")
    return base64str

def get_vision_data(base64_image, query):
    vision_result = "Vision capability not supported"
    if not hasattr(provider, 'send_vision_request'):
        print("The current provider does not support vision requests.")
    else:
        print("The current provider supports vision requests.")
        vision_result = provider.send_vision_request(base64_image, query)
    return vision_result


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
