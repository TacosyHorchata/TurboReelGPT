import requests
import logging

async def generate_with_pollinations(prompt: str, height: int = 1024, width: int = 1024, not_logo: bool = False) -> str:
    """
    Generate an image using Pollinations API. (https://pollinations.ai/)
    Args:
        prompt (str): Text prompt for image generation.
        api_key (str): API key for Pollinations.
        height (int): Height of the generated image.
        width (int): Width of the generated image.
        not_logo (bool): Whether to hide the Pollinations logo(Add credits in case of set to True).
    
    Returns:
        str: URL or path of the generated image.
    """

    logging.info(f"Calling Pollinations API with prompt: {prompt}")
    
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"      
        payload = {
            "prompt": prompt, 
            "height": height or 1024, 
            "width": width or 1024, 
            "no_logo": not_logo
        }

        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return url
        else:
            raise RuntimeError(f"Pollinations API error: {response.text}")
            
    except Exception as e:
        logging.error(f"Error in generate_with_pollinations: {str(e)}")
        raise