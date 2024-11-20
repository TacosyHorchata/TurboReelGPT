import requests
from openai import OpenAI

def generate_with_dalle(api_key: str, prompt: str, height: int = 1024, width: int = 1024) -> str:
    """
    Generate an image using DALL·E API.
    Args:
        prompt (str): Text prompt for image generation.
        api_key (str): API key for DALL·E.

    Returns:
        str: URL of the generated image.
    """
    if not api_key:
        raise ValueError("DALL·E API key is required.")

    client = OpenAI(api_key=api_key)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=f"{width}x{height}",
        quality="standard",
        n=1
    )
    url = response.data[0].url
    return url
