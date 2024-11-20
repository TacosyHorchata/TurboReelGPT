from openai import OpenAI
from core.audio.speech_to_text.utils.words_parser import parse_stt_openai_words

def generate_openai_speech_to_text(api_key: str, audio_file: str) -> list[dict]:
    client = OpenAI(api_key=api_key)
    audio_file = open(audio_file, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["word"]    
    )
    
    return parse_stt_openai_words(transcript.words)
