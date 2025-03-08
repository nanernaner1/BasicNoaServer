import wave
import io
import base64

from pydub import AudioSegment
from gtts import gTTS
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]

def convert_tts_into_audio_file(text: str) -> str:
    text_to_convert = text
    # 4️⃣ Generate, display, and save audio files in a loop.
    tts = gTTS(text_to_convert)
    tts.save('audio_response/last_response.mp3')
    return 'audio_response/last_response.mp3'

def convert_mp3_to_wav(filename: str):
    input_file = filename
    output_file = 'audio_response/last_response.wav'

    try:
        sound = AudioSegment.from_mp3(input_file)
        sound.export(output_file, format='wav')
    except Exception as err:
        return 'failed to convert'
    return 'File converted successfully!'

def read_speech_from_audio_file(wav_filename: str):
    with io.BytesIO() as output:
        with wave.open(output, "wb") as wav:
            wav.setparams((1, 2, 24000, 0, 'NONE', 'NONE'))

            with open(wav_filename, 'rb') as input_file:
                wav.writeframes(input_file.read())
        
        output.seek(0)
        base64str = base64.b64encode(output.getvalue()).decode('utf-8')
    return base64str
