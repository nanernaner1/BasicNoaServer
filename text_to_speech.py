from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import wave
import io
import base64
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]

def convert_tts_into_audio_file(text: str):
    pipeline = KPipeline(lang_code='a') # <= make sure lang_code matches voice

    text_to_convert = text
    # 4️⃣ Generate, display, and save audio files in a loop.
    generator = pipeline(
        text_to_convert, voice='af_heart', # <= change voice here
        speed=1, split_pattern=r'\n+'
    )
    for i, (gs, ps, audio) in enumerate(generator):
        print(i)  # i => index
        print(gs) # gs => graphemes/text
        print(ps) # ps => phonemes
        sf.write(f'audio_responses/{i}-last_response.wav', audio, 24000) # save each audio file

def read_speech_from_audio_file(wav_filename: str):
    with io.BytesIO() as output:
        with wave.open(output, "wb") as wav:
            wav.setparams((1, 2, 24000, 0, 'NONE', 'NONE'))

            with open(wav_filename, 'rb') as input_file:
                wav.writeframes(input_file.read())
        
        output.seek(0)
        base64str = base64.b64encode(output.getvalue()).decode('utf-8')
    return base64str