from openai import OpenAI
from core.script.utils.script_utils import load_yaml_file
import json

def generate_openai_script(api_key: str, prompt: str, model: str = "gpt-3.5-turbo-0125") -> str:
    """
    Generate a script using OpenAI
    """
    system_prompt = load_yaml_file("script.yaml")["system_prompt"]
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    )
    response_json = json.loads(response.choices[0].message.content)
    return response_json["script"]