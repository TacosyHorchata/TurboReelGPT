import cv2
import base64
from openai import OpenAI
import os
from typing import List, Dict

def _extract_frames(video_path: str) -> List[str]:
    """Extract and encode frames from video"""
    video = cv2.VideoCapture(video_path)
    base64_frames = []
    
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
    
    video.release()
    return base64_frames

def summarize_video(api_key: str, video_path: str, frame_interval: int = 60) -> Dict[str, str]:
    """
    Analyze video frames using GPT-4o's 128k context window

    (https://cookbook.openai.com/examples/gpt_with_vision_for_video_understanding)
    
    Args:
        video_path: Path to video file
        frame_interval: Number of frames to skip between analyses
    """
    client = OpenAI(api_key=api_key)

    # Extract frames
    frames = _extract_frames(video_path)
    print(f"Extracted {len(frames)} frames")
    
    # Prepare messages with all frames at once
    messages = [
        {
            "role": "user",
            "content": [
                "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
                *map(lambda x: {"image": x, "resize": 768}, frames[0::frame_interval]),
            ],
        }
    ]
    
    # Get analysis from GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=200
    )
    
    return {
        "summary": response.choices[0].message.content
    }

def generate_video_narration(api_key: str, video_path: str, frame_interval: int = 60) -> Dict[str, str]:
    """
    Generate a video narration using GPT-4o
    """

    client = OpenAI(api_key=api_key)
    frames = _extract_frames(video_path)
    prompt_messages = [
        {
            "role": "user",
            "content": [
                "These are frames of a video. Create a short voiceover script. Only include the narration.",
                *map(lambda x: {"image": x, "resize": 768}, frames[0::frame_interval]),
            ],
        },
    ]
    
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "max_tokens": 500,
    }

    result = client.chat.completions.create(**params)
    return {
        "narration": result.choices[0].message.content
    }