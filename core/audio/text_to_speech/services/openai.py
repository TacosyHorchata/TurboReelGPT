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

    # Generate unique filename
    output_file = Path("tmp") / f"tts_audio_{uuid.uuid4()}.mp3"
    
    # Use streaming response
    with client.audio.speech.create(
        input=text,
        voice=voice,
        model="tts"
    ).with_streaming_response() as response:
        with open(output_file, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    
    return str(output_file)