from openai import OpenAI
from openai import AzureOpenAI
from typing import Literal
import json

def enhance_prompt(service: Literal["openai", "azure_openai"], api_key: str, prompt: str, azure_config: dict = None, model: str = None):
    if service == "openai":
        try:
            return enhance_prompt_openai(api_key, prompt, model)
        except Exception as e:
            raise ValueError(f"Error enhancing prompt with OpenAI: {e}")
    elif service == "azure_openai":
        try:
            return enhance_prompt_azure(api_key, prompt, azure_config, model)
        except Exception as e:
            raise ValueError(f"Error enhancing prompt with Azure OpenAI: {e}")

def enhance_prompt_azure(api_key: str, prompt: str, azure_config: dict, model: str = "gpt-35-turbo"):
    client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_config["azure_endpoint"], azure_deployment=azure_config["azure_deployment"], azure_api_version=azure_config["azure_api_version"])
    system_prompt = enhance_system_prompt
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    )
    response_json = json.loads(response.choices[0].message.content)
    return response_json["image_prompt"]

def enhance_prompt_openai(api_key: str, prompt: str, model: str = "gpt-3.5-turbo"):
    client = OpenAI(api_key=api_key)
    system_prompt = enhance_system_prompt
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    )
    response_json = json.loads(response.choices[0].message.content)
    return response_json["image_prompt"]

enhance_system_prompt = """
    
    You are a specialized prompt generation system for video automation, 
    tasked with generating image prompts that are visually engaging and suited to the provided scene text. 
    Focus on capturing vibrant, lively details to make each image compelling and relatable.

    **Guidelines:**
    1. Write concise prompts that prioritize the details in the scene text, adding any vivid or relevant elements to enhance the scene.
    2. Use specific sensory details (like lighting, atmosphere, or motion) to bring each image to life, avoiding overly corporate or static imagery.
    3. Keep prompts engaging by emphasizing emotions, actions, or vivid backgrounds that match the scene.
    4. Avoid including any text within the image; focus solely on describing the visual content.

    **Example outputs:**
    - "Three friends laughing and dancing on a beach at sunset in California, waves in the background"
    - "Kids in fun Halloween costumes, smiling and posing excitedly at a colorful McDonald's"
    - "Friends chatting and laughing in a lively bar, while a dramatic argument unfolds nearby" 


    **Output Format:**
    Return the result as a JSON object structured as follows:
    {
        "image_prompt": "image prompt here"
    }

    """