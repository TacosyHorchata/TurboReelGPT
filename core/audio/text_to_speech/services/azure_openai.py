from openai import AzureOpenAI
import os
import uuid
from pathlib import Path

azure_config_interface = {
    "endpoint": str,
    "api_version": str,
    "deployment": str
}

def generate_azure_openai_text_to_speech(api_key: str, text: str, azure_config: dict, voice: str = "echo") -> str:
    # Validate config values exist
    required_keys = ["endpoint", "api_version", "deployment"]
    if not all(key in azure_config for key in required_keys):
        raise ValueError("Missing required Azure configuration keys")

    # Create client with proper parameter names
    client = AzureOpenAI(
        azure_endpoint=azure_config["endpoint"], # make sure the endpoint ends with /transcription and not /translation
        api_key=api_key,
        api_version=azure_config["api_version"],
        deployment=azure_config["deployment"]
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