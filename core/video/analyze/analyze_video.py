from services.openai import summarize_video, generate_video_narration

def generate_video_summary(openai_api_key: str, video_path: str, frame_interval: int = 60) -> dict[str]:
    try:
        return summarize_video(openai_api_key, video_path, frame_interval)
    except Exception as e:
        raise Exception(f"Error generating video summary: {e}")

def generate_video_narration(openai_api_key: str, video_path: str, frame_interval: int = 60) -> dict[str]:
    try:
        return generate_video_narration(openai_api_key, video_path, frame_interval)
    except Exception as e:
        raise Exception(f"Error generating video narration: {e}")
