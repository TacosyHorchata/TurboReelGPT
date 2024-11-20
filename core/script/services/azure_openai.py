from openai import AzureOpenAI
from core.script.utils.script_utils import load_yaml_file
import json
azure_config_interface = {
    "azure_endpoint": str,
    "azure_deployment": str,
    "azure_api_version": str
}

def generate_azure_openai_script(api_key: str, prompt: str, model: str = "gpt-35-turbo", azure_config: dict = None) -> str:
    """
    Generate a script using Azure OpenAI
    """
    # Validate all required config fields are present and of correct type
    for key, expected_type in azure_config_interface.items():
        if key not in azure_config:
            raise ValueError(f"{key} is required")
        if not isinstance(azure_config[key], expected_type):
            raise ValueError(f"{key} must be of type {expected_type.__name__}")

    system_prompt = load_yaml_file("script.yaml")["system_prompt"]
    client = AzureOpenAI(api_key=api_key, 
                         azure_endpoint=azure_config["azure_endpoint"], 
                         azure_deployment=azure_config["azure_deployment"], 
                         azure_api_version=azure_config["azure_api_version"])
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    )
    response_json = json.loads(response.choices[0].message.content)
    return response_json["script"]