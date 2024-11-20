from openai import OpenAI

def get_caption_styles() -> dict:
    """
    Returns a dictionary of caption styles with their visual properties.
    Each style includes color (in hex), font family, and size multiplier.
    """
    return {
        "calm": {
            "color": "#FFFFFF",  # White
            "font": "Arial",
            "size": 1.0  # Base size
        },
        "suspense": {
            "color": "#FFD700",  # Gold
            "font": "Georgia",
            "size": 1.1
        },
        "panic": {
            "color": "#FF0000",  # Red
            "font": "Impact",
            "size": 1.3
        },
        "alert": {
            "color": "#FFA500",  # Orange
            "font": "Helvetica Bold",
            "size": 1.2
        },
        "surprise": {
            "color": "#FF1493",  # Deep Pink
            "font": "Verdana",
            "size": 1.2
        },
        "sad": {
            "color": "#4169E1",  # Royal Blue
            "font": "Times New Roman",
            "size": 0.9
        },
        "happy": {
            "color": "#32CD32",  # Lime Green
            "font": "Comic Sans MS",
            "size": 1.1
        },
        "angry": {
            "color": "#8B0000",  # Dark Red
            "font": "Impact",
            "size": 1.25
        },
        "excited": {
            "color": "#FF69B4",  # Hot Pink
            "font": "Trebuchet MS",
            "size": 1.2
        },
        "disappointed": {
            "color": "#808080",  # Gray
            "font": "Garamond",
            "size": 0.9
        },
        "confused": {
            "color": "#9370DB",  # Medium Purple
            "font": "Courier New",
            "size": 1.0
        }
    }

def generate_captions_style(openai_api_key: str, video_path: str, model: str = "gpt-3.5-turbo") -> dict:
    client = OpenAI(api_key=openai_api_key)
    
    # Read the video captions/script
    with open(video_path, 'r') as file:
        script = file.read()

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": """
                You are a helpful assistant that generates captions for a video based on the script mood. You will be given a script and you should assign a style to the captions based on the script mood.
                
                Rules:
                1. Analyze each sentence for its emotional context
                2. Add appropriate style tag at the end of each meaningful phrase
                3. Use the following style tags based on the emotional context:
                   $#calm - for neutral or peaceful moments (white color, normal size)
                   $#suspense - for tense or uncertain moments (gold color, slightly larger)
                   $#panic - for frightening or urgent situations (red color, much larger)
                   $#alert - for warning or cautionary moments (orange color, larger)
                   $#surprise - for unexpected events or revelations (pink color, larger)
                   $#sad - for sorrowful or melancholic moments (blue color, slightly smaller)
                   $#happy - for joyful or positive situations (green color, slightly larger)
                   $#angry - for moments of rage or frustration (dark red color, larger)
                   $#excited - for enthusiastic or energetic moments (hot pink color, larger)
                   $#disappointed - for letdown or unfulfilled expectations (gray color, slightly smaller)
                   $#confused - for puzzling or unclear situations (purple color, normal size)

                Example:
                Input: "A man is walking down the street. When someone attacked him, he defended himself. It was a giant bear."
                Output: "A man is walking down the street($#calm). When someone($#suspense) attacked him($#panic), he defended himself($#alert). It was a giant bear($#surprise)."
            """},
            {"role": "user", "content": script}
        ],
        temperature=0.7,
        max_tokens=1500
    )

    # Extract the styled captions from the response
    styled_captions = chat_completion.choices[0].message.content
    
    return {
        "styled_captions": styled_captions,
        "style_properties": get_caption_styles()
    }
