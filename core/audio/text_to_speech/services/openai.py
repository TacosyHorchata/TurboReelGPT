from openai import OpenAI
import uuid
from pathlib import Path

def generate_openai_text_to_speech(api_key: str, text: str, voice: str = "echo") -> str:
    if not api_key:
        raise ValueError("Missing OpenAI API key")

    # Create client with proper parameter names
    client = OpenAI(
        api_key=api_key
    )

    # Create tmp directory if it doesn't exist
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)

    # Generate unique filename
    output_file = tmp_dir / f"tts_audio_{uuid.uuid4()}.mp3"
    
    # Use streaming response
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3"
    )

    # Save the audio content
    response.stream_to_file(output_file)
    
    return str(output_file)