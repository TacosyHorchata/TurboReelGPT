from core.script.services.openai import generate_openai_script
from core.script.services.azure_openai import generate_azure_openai_script
from typing import Literal

azure_config_interface = {
    "azure_endpoint": str,
    "azure_deployment": str,
    "azure_api_version": str
}

def generate_script(service: Literal["openai", "azure_openai"], api_key: str, prompt: str, model, azure_config: dict = None) -> str:
    # Validate all required config fields are present and of correct type
    if service == "azure_openai":
        for key, expected_type in azure_config_interface.items():
            if key not in azure_config:
                raise ValueError(f"{key} is required")
            if not isinstance(azure_config[key], expected_type):
                raise ValueError(f"{key} must be of type {expected_type.__name__}")

    if service == "openai":
        try:
            return generate_openai_script(api_key, prompt, model)
        except Exception as e:
            raise ValueError(f"Error generating script with OpenAI: {e}")
    elif service == "azure_openai":
        try:
            return generate_azure_openai_script(api_key, prompt, model, azure_config)
        except Exception as e:
            raise ValueError(f"Error generating script with Azure OpenAI: {e}")