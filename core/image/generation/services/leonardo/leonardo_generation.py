from leonardo_api import Leonardo

def generate_with_leonardo(api_key: str, prompt: str, height: int = 1024, width: int = 1024) -> str:
    """
    Generate an image using Leonardo API. (https://leonardo.ai/)
    Args:
        prompt (str): Text prompt for image generation.
        api_key (str): API key for Leonardo.
        height (int): Height of the generated image.
        width (int): Width of the generated image.

    Returns:
        str: URL or path of the generated image.
    """
    if not api_key:
        raise ValueError("Leonardo API key is required.")

    # Initialize Leonardo client
    leonardo = Leonardo(auth_token=api_key)
    
    # Generate image
    response = leonardo.post_generations(
        prompt=prompt,
        num_images=1,
        width=width or 1024,
        height=height or 1024,
        model_id="6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"
    )
    
    generation_id = response['sdGenerationJob']['generationId']
    
    # Wait for generation to complete and get results
    result = leonardo.wait_for_image_generation(generation_id=generation_id)
    
    # Return the first generated image URL
    return result[0]['url']
