""" 
This ensures that the words are parsed in the same way for all Speech-to-Text services.
"""

# In case OpenAI is used as STT service
def parse_stt_openai_words(words: list[dict]) -> list[dict]:
    """
    Parse the words from the OpenAI response.
    """

    return [{"start": word["start"], "end": word["end"], "text": word["text"]} for word in words]

# In case Azure OpenAI is used as STT service
def parse_stt_azure_openai_words(words: list[dict]) -> list[dict]:
    """
    Parse the words from the Azure OpenAI response.
    """

    return [{"start": word["start"], "end": word["end"], "text": word["text"]} for word in words]

# In case ElevenLabs is used as STT service
def parse_stt_elevenlabs_words(words: list[dict]) -> list[dict]:
    """
    Parse the words from the ElevenLabs response.
    """
    # todo: test this
    return [{"start": word["start"], "end": word["end"], "text": word["text"]} for word in words]
