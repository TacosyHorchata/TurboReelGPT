import core.audio.speech_to_text.services.openai as openai
import core.audio.speech_to_text.services.azure_openai as azure_openai
from typing import Literal

def generate_speech_to_text(service: Literal["openai", "azure_openai"], api_key: str, audio_file: str, azure_config: dict = None) -> list[dict]:
    if service == "openai":
        try:
            return openai.generate_openai_speech_to_text(api_key, audio_file)
        except Exception as e:
            raise ValueError(f"Error generating speech-to-text with OpenAI: {e}")
    elif service == "azure_openai":
        try:
            return azure_openai.generate_azure_openai_speech_to_text(api_key, audio_file, azure_config)
        except Exception as e:
            raise ValueError(f"Error generating speech-to-text with Azure OpenAI: {e}")
    else:
        raise ValueError(f"Invalid service: {service}")