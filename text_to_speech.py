from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]

def tts(text: str) -> None:
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
        sf.write(f'{i}.wav', audio, 24000) # save each audio file