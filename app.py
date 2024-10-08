import yaml
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import random
import asyncio
from openai import OpenAI
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

from src.ImageHandler import ImageHandler
from src.AIShortGenerator import AIShortGenerator

def load_config(file_path):
    """Load the YAML configuration file."""
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        logging.error(f"Config file {file_path} not found.")
        raise
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        raise

def load_prompt(file_path):
    """Load the YAML prompt template file."""
    try:
        with open(file_path, 'r') as file:
            prompt_template_file = yaml.safe_load(file)
        return prompt_template_file
    except FileNotFoundError:
        logging.error(f"Prompt file {file_path} not found.")
        raise
    except Exception as e:
        logging.error(f"Error loading prompt file: {e}")
        raise

config = load_config('config.yaml')

# Accessing configuration values
openai_api_key = os.getenv('OPENAI_API_KEY', config['api_keys']['OPENAI_API_KEY'])
pexels_api_key = os.getenv('PEXELS_API_KEY', config['api_keys']['PEXELS_API_KEY'])

openai = OpenAI(api_key=openai_api_key)

def gpt_summary_of_script(video_script):
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            temperature=0.25,
            max_tokens=250,
            messages=[
                {"role": "user", "content": f"Summarize the following video script; it is very important that you keep it to one line. \n Script: {video_script}"}
            ]
        )
        logging.info("Script generated successfully.")
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating script summary: {e}")
        return ""  # Return an empty string on error

async def generate_video(video_topic='', video_url='', video_script='', video_script_type='based_on_topic'):
    """Generate a video based on the provided topic or ready-made script.

    Args:
        video_topic (str): The topic of the video if script type is 'based_on_topic'.
        video_url (str): The URL of the video to download.
        video_script (str): The ready-made script if script type is 'ready_made_script'.
        video_script_type (str): The type of script generation ('based_on_topic' or 'ready_made_script').

    Returns:
        dict: A dictionary with the status of the video generation and a message.
    """
    try:
        # Ensure the script type is provided
        if not video_script_type:
            raise ValueError("The video script type must be provided.")

        # Handle the different cases for script generation
        if video_script_type == 'ready_made_script':
            if not video_script:
                raise ValueError("For 'ready_made_script', the video script should not be null.")
            if len(video_script) > 400:
                raise ValueError("The video script exceeds the 400 character limit.")

        elif video_script_type == 'based_on_topic':
            if not video_topic:
                raise ValueError("For 'based_on_topic', the video topic should not be null.")
            # video_script = generate_script_from_topic(video_topic) # You'd need to implement this

        else:
            raise ValueError("Invalid video script type. It must be either 'ready_made_script' or 'based_on_topic'.")

        # Load prompt template
        prompt_template = load_prompt('prompt_templates/reddit_thread.yaml')

        logging.info(f"Starting video generation process for: {video_script_type}")
        ai_short_gen = AIShortGenerator(openai_api_key)
        image_handler = ImageHandler(pexels_api_key, openai_api_key)

        video_path = ai_short_gen.download_video(video_url)
        if not video_path:
            logging.error("Failed to download video.")
            return {"status": "error", "message": "No video path provided."}

        script = video_script if video_script_type == 'ready_made_script' else await ai_short_gen.generate_script(video_topic, prompt_template)
        if not script:
            logging.error("Failed to generate script.")
            return {"status": "error", "message": "Failed to generate script."}

        audio_path = await ai_short_gen.generate_voice(script)
        if not audio_path:
            logging.error("Failed to generate audio.")
            return {"status": "error", "message": "Failed to generate audio."}

        audio_clip = AudioFileClip(str(audio_path))
        audio_length = audio_clip.duration
        audio_clip.close()

        video_length = VideoFileClip(video_path).duration
        max_start_time = video_length - audio_length

        if max_start_time <= 0:
            logging.error("Calculated start time is invalid.")
            return {"status": "error", "message": "Calculated start time is invalid."}

        start_time = random.uniform(0, max_start_time)
        end_time = start_time + audio_length

        cut_video_path = ai_short_gen.cut_video(video_path, start_time, end_time)
        if not cut_video_path:
            logging.error("Failed to cut video.")
            return {"status": "error", "message": "Failed to cut video."}

        subtitles_path = ai_short_gen.generate_subtitles(audio_path)
        logging.info(f"Subtitles generated successfully.")

        video_context = video_script if video_script_type == 'ready_made_script' else video_topic
        image_paths = image_handler.get_images_from_subtitles(subtitles_path, video_context)
        logging.info(f"Downloaded images successfully.")

        clip = ai_short_gen.add_audio_and_captions_to_video(cut_video_path, audio_path, subtitles_path)
        ai_short_gen.add_images_to_video(clip, image_paths)

        # Cleanup: Ensure temporary files are removed
        cleanup_files([audio_path, cut_video_path, subtitles_path])

        return {"status": "success", "message": "Video generated successfully."}
    
    except Exception as e:
        logging.error(f"Error in video generation: {e}")
        return {"status": "error", "message": f"Error in video generation: {str(e)}"}


def cleanup_files(file_paths):
    """Delete temporary files to clean up the workspace."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted temporary file: {file_path}")
            else:
                logging.warning(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")


# Example usage
video_url = config['assets']['YOUTUBE_URL']
video_topic = config['video_parameters']['VIDEO_TOPIC']
video_script = config['video_parameters']['VIDEO_SCRIPT']
video_script_type = config['video_parameters']['VIDEO_SCRIPT_TYPE']

asyncio.run(generate_video(video_topic=video_topic, 
                           video_url=video_url, 
                           video_script=video_script, 
                           video_script_type=video_script_type))
