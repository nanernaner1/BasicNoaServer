# 2024 Curiosiate. 



from flask import Flask, request, jsonify
from io import BytesIO
import speech_recognition as sr
import base64
import requests
import logging
import datetime
import os

from lm_studio_provider import LMStudioProvider



from modules.module_loader import load_modules, find_and_execute_module
import threading



app = Flask(__name__)

# Ensure the data directory exists
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Initialize provider and working memory
provider = LMStudioProvider()


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

@app.route('/', methods=['POST'])
def process_request():
    print("Got in request")
    #check the status code if not 200 return error
    if request.method != 'POST':
        return jsonify({"error": "Invalid request"}), 200
    
    if 'audio' not in request.files or 'image' not in request.files:
        return jsonify({"error": "Missing audio or image file"}), 200
    if 'location' not in request.form or 'time' not in request.form or 'messages' not in request.form:
        return jsonify({"error": "Missing form data"}), 200

    
    audio = request.files['audio']
    image = request.files['image']
    location = request.form['location']
    time = request.form['time']
    messages = request.form['messages']
    custom_prompt = request.form.get('custom_prompt', prompt_data)

    # Convert files to base64
    audio_base64 = base64.b64encode(audio.read()).decode('utf-8')
    image_base64 = base64.b64encode(image.read()).decode('utf-8')

    # Decode base64 audio and image
    audio_data = base64.b64decode(audio_base64)
    image_data = base64.b64decode(image_base64)

    # Process audio data (transcribe)
    audio_result = transcribe_audio(audio_data)
    print(audio_result)

    # Load and execute relevant modules
    modules = load_modules()
    module_data = find_and_execute_module(modules, audio_result, provider)
    #module_data = ingestToAllModules(audio_result, provider)
    

    # Send image data to LM Studio vision model, or don't because until the camera works better in lighting situations, this will clog up and muddy the results by giving false seeds to memories.
    vision_data = "" #get_vision_data(image_base64, "Extract relevant information from the image, describe the scene, elements within it, any text present, etc. The goal is to encode the scene in a narrative as though from memory. This should be a brief description of the image, not a lengty one. Simple and sweet, under 200 words or less.")
    
    # Prepare messages for LM Studio chat model
    chat_messages = [
        {"role": "system", "content": profile_data},
        {"role": "user", "content": custom_prompt},
        {"role": "user", "content": f"request from Audio transcription: {audio_result}"},
        #{"role": "user", "content": f"relevant image data, if any description: {vision_data}"}
        {"role": "user", "content": "shorten any replies to only a sentence or four long, so make sure to be quick and to the point, only giving the relevant information, this is for use on a small HUD display whatever response format is given."} #tune this to refine responses for the frame
    ]

    # Include module data if any
    if module_data:
        chat_messages.append({"role": "user", "content": f"Relevant data: {module_data}"})
    # Send data to local LM Studio chat model
    lm_data = provider.send_request(chat_messages, 0.7)

    # Format the response
    response = {
        'user_prompt': audio_result,
        'message': lm_data,
        'image': image_base64, 
        'audio': audio_base64,
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

def get_vision_data(base64_image, query):
    vision_result = "Vision capability not supported"
    if not hasattr(provider, 'send_vision_request'):
        print("The current provider does not support vision requests.")
    else:
        print("The current provider supports vision requests.")
        vision_result = provider.send_vision_request(base64_image, query)
    return vision_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)