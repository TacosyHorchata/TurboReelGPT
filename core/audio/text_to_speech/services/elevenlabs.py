from elevenlabs import ElevenLabs
from pathlib import Path
import uuid

def generate_elevenlabs_text_to_speech(api_key: str, text: str, voice: str = "Brian", model_id: str = "eleven_multilingual_v2") -> str:
    """
    Generate text-to-speech audio using ElevenLabs API
    
    Args:
        api_key (str): ElevenLabs API key
        text (str): Text to convert to speech
        voice (str): Name or ID of the voice to use
        model_id (str): ID of the model to use, defaults to eleven_multilingual_v2
    
    Returns:
        str: Path to the generated audio file
    """
    client = ElevenLabs(api_key=api_key)
    
    audio = client.generate(
        text=text,
        voice=voice,
        model=model_id
    )

    # Generate unique filename
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    output_file = tmp_dir / f"tts_audio_{uuid.uuid4()}.mp3"
    
    # Save the audio content
    with open(output_file, "wb") as f:
        f.write(audio)
    
    return str(output_file)