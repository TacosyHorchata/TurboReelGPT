from openai import OpenAI
from openai import AzureOpenAI
from typing import Literal
import json
azure_config_interface = {
    "azure_endpoint": str,
    "azure_deployment": str,
    "azure_api_version": str
}

def generate_image_timestamps(service: Literal['openai', 'azure_openai'], api_key: str, script: str, model: str, azure_config: dict = None):
    # Validate all required config fields are present and of correct type
    if azure_config is not None:
        for key, expected_type in azure_config_interface.items():
            if key not in azure_config:
                raise ValueError(f"{key} is required")
            if not isinstance(azure_config[key], expected_type):
                raise ValueError(f"{key} must be of type {expected_type.__name__}")

    if service == 'openai':
        try:
            return generate_image_timestamps_openai(api_key, script, model)
        except Exception as e:
            raise ValueError(f"Error syncing with script using OpenAI: {e}")
    elif service == 'azure_openai':
        try:
            return generate_image_timestamps_azure(api_key, script, azure_config, model)
        except Exception as e:
            raise ValueError(f"Error syncing with script using Azure OpenAI: {e}")

def generate_image_timestamps_azure(api_key: str, script_with_timestamps: str, azure_config: dict, model: str = "gpt-35-turbo"):
    client = AzureOpenAI(api_key=api_key, 
                        azure_endpoint=azure_config["azure_endpoint"], 
                        azure_deployment=azure_config["azure_deployment"], 
                        azure_api_version=azure_config["azure_api_version"])
    system_prompt = images_timestamps_in_stt_system_prompt
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": script_with_timestamps}]
    )   
    response_json = json.loads(response.choices[0].message.content)
    return response_json["images"]

def generate_image_timestamps_openai(api_key: str, script_with_timestamps: str, model: str = "gpt-3.5-turbo"):
    client = OpenAI(api_key=api_key)
    system_prompt = images_timestamps_in_stt_system_prompt
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": script_with_timestamps}]
    )
    response_json = json.loads(response.choices[0].message.content)
    return response_json["images"]

images_timestamps_in_stt_system_prompt = """

You are a specialized video editing assistant tasked with associating images to timestamps in a given script. 
    Your role is to identify key phrases from the script where images should be added, following specific guidelines.

    **Guidelines:**
    1. Identify the key timestamps where an image should be added.  
    2. Always include timestamp (0.00), since will be used as a starting point.
    3. Output the identified timestamps in JSON format.
    4. Add 5 images to the video.
    5. Make sure to space them evenly according to the video duration.
    - Example: If the video duration is 10 seconds, the images should be spaced 2 seconds apart.

    **Guidelines for Images:**
    - Create highly visual, cinematic scenes
    - Keep prompts concise (5-10 words)
    - Avoid text, interfaces, UIs, logos, or technical elements
    - Keep the prompt relevant to the scene's meaning

    **Example Input:**
    
    Script: 
    
    "In(0.00) March(0.60) 2024(1.20), the(1.80) world(2.40) was(3.00) shocked(3.60) to(4.20) 
    learn(4.80) that(5.40) the(6.00) legendary(6.60) explorer(7.20), Sir(7.80) Edmund(8.40) Hillary(9.00), had(9.60) 
    passed(10.20) away(10.80) at(11.40) the(12.00) age(12.60) of(13.20) 93(13.80). A(14.40) lot(15.00) of(15.60) 
    people(16.20) are(16.80) wondering(17.40) what(18.00) happened(18.60) to(19.20) him(19.80)."

    **Example JSON Output:**
    {
      "images": [
        { "timestamp": "0.00", "prompt": "People shocked staring at a coffin" },
        { "timestamp": "3.80", "prompt": "People mourning at a funeral" },
        { "timestamp": "7.70", "prompt": "People celebrating the life of Sir Edmund Hillary" },
        { "timestamp": "11.50", "prompt": "Aerial view of Mount Everest" },
        { "timestamp": "15.30", "prompt": "Close up of a golden trophy" }
      ]
    }

"""