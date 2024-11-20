from openai import AzureOpenAI
from core.audio.speech_to_text.utils.words_parser import parse_stt_azure_openai_words

azure_config_interface = {
    "endpoint": str,
    "api_version": str,
    "deployment": str
}

def generate_azure_openai_speech_to_text(api_key: str, audio_file: str, azure_config: dict) -> list[dict]:
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

    # Use context manager for file handling
    with open(audio_file, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            file=audio,
            response_format="verbose_json",
            timestamp_granularities=["word"]    
        ) 

    return parse_stt_azure_openai_words(transcript.words)
