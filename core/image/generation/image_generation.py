from core.image.generation.services.dalle.dalle_generation import generate_with_dalle
from core.image.generation.services.leonardo.leonardo_generation import generate_with_leonardo
from core.image.generation.services.pollinations.pollinations_generation import generate_with_pollinations

import os
from typing import Literal

def generate_image(service: Literal["dalle", "pollinations", "leonardo"], api_key: str, prompt: str, width: int = 1024, height: int = 1024) -> str:

    if service == "dalle":
        try:
            return generate_with_dalle(api_key, prompt, width, height)
        except Exception as e:
            raise ValueError(f"Error generating image with DALL·E: {e}")
    elif service == "pollinations":
        try:
            return generate_with_pollinations(api_key, prompt, width, height)
        except Exception as e:
            raise ValueError(f"Error generating image with Pollinations: {e}")
    elif service == "leonardo":
        try:
            return generate_with_leonardo(api_key, prompt, width, height)
        except Exception as e:
            raise ValueError(f"Error generating image with Leonardo: {e}")
