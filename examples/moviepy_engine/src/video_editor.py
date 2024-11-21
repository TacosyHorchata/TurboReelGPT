import os
import logging
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
from openai import OpenAI
import pysrt
from yt_dlp import YoutubeDL
from pathlib import Path
import uuid
import re  # Added import for regular expression operations
import json  # Added import for JSON operations

from dotenv import load_dotenv

# MEDIACHAIN
from core.image.generation.image_generation import generate_image
from core.image.utils.enhace_prompt import enhance_prompt

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

openai_api_key = os.getenv('OPENAI_API_KEY')

def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Create a unique filename for the image in temp directory
            unique_id = uuid.uuid4()
            temp_dir = os.path.join('/tmp', 'moviepy')  # For Unix-like systems
            os.makedirs(temp_dir, exist_ok=True)
            image_path = os.path.join(temp_dir, f"image_{unique_id}.png")
            
            # Save the image content
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            return image_path
        else:
            logging.error(f"Failed to download image. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return None

class VideoEditor:
    def __init__(self):
        self.openai = OpenAI(api_key=openai_api_key)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def download_video(self, youtube_url, quality="480"):
        try:
            downloads_dir = os.path.join(self.base_dir, '..', 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)
            
            # First extract info without downloading to get video details
            with YoutubeDL({'quiet': True}) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                video_id = info_dict['id']
            
            # Create a filename that includes quality
            quality_suffix = f"{quality}p"
            safe_filename = f"{video_id}_{quality_suffix}"
            video_path = os.path.join(downloads_dir, f"{safe_filename}.mp4")
            
            # Check if file already exists
            if os.path.exists(video_path):
                logging.info(f"Video already exists at {quality_suffix}: {video_path}")
                return video_path
            
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
                'outtmpl': os.path.join(downloads_dir, safe_filename),
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            logging.info("Video downloaded successfully.")
            return video_path
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return None

    def cut_video(self, video_path, start_time, end_time):
        if not os.path.exists(video_path):
            logging.error(f"Video file does not exist, {video_path}")
            return
        try:
            unique_id = uuid.uuid4()
            assets_dir = os.path.join(self.base_dir, '..', 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            output_path = os.path.join(assets_dir, f"cut_video_{unique_id}.mp4")
            
            clip = VideoFileClip(video_path)
            cut_clip = clip.subclip(start_time, end_time)
            cut_clip.write_videofile(output_path)
            logging.info("Video cut successfully.")
            return output_path
        except Exception as e:
            logging.error(f"Error cutting video: {e}")

    def load_subtitles(self, subtitles_path):
        try:
            return pysrt.open(subtitles_path)  # Return the loaded SRT file with start and end times
        except Exception as e:
            logging.error(f"Error loading subtitles: {e}")
            return []  # Return empty list on failure

    def add_audio_to_video(self, video_path, audio_path) -> VideoFileClip:
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(str(audio_path))
            final_clip = video_clip.set_audio(audio_clip)
            
            logging.info("Audio added to video successfully.")
            return final_clip
        except Exception as e:
            logging.error(f"Error adding audio to video: {e}")
            return None
    
    def crop_video_9_16(self, video_clip: VideoFileClip) -> VideoFileClip:
        try:
            # Crop the video to TikTok format (9:16 aspect ratio)
            video_width, video_height = video_clip.size
            target_aspect_ratio = 9 / 16
            target_height = video_height
            target_width = int(target_height * target_aspect_ratio)

            if target_width < video_width:
                # Center crop horizontally
                cropped_clip = video_clip.crop(x_center=video_width / 2, width=target_width, height=target_height)
            else:
                # If the video is already narrower than 9:16, don't crop
                cropped_clip = video_clip

            logging.info("Video cropped successfully")
            return cropped_clip
        except Exception as e:
            logging.error(f"Error cropping video: {e}")
            return None

    def add_captions_to_video(self, video_clip, subtitles_clips:list) -> CompositeVideoClip:
        try:
            if video_clip is None:
                raise ValueError("video_clip is None")

            # Ensure subtitles_clips is a list
            if not isinstance(subtitles_clips, list):
                logging.warning("subtitles_clips is not a list. Converting to a list.")
                subtitles_clips = [subtitles_clips] if subtitles_clips else []

            # Combine the video and subtitle clips
            final_clip = CompositeVideoClip([video_clip] + subtitles_clips)
            logging.info("Captions added to video successfully.")
            return final_clip
        except Exception as e:
            logging.error(f"Error adding captions to video: {e}")
            return None

    async def add_images_to_video(self, video_clip, images):
        """This function receives the following object
        **Example JSON Output:**
            {
                "images": [
                    { "timestamp": "0.00", "prompt": "People shocked staring at a coffin" },
                    { "timestamp": "3.80", "prompt": "People mourning at a funeral" },
                    { "timestamp": "7.70", "prompt": "People celebrating the life of Sir Edmund Hillary" },
                    { "timestamp": "11.50", "prompt": "Aerial view of Mount Everest" },
                    { "timestamp": "15.30", "prompt": "Close up of a golden trophy" }
                ]
            }

        """
        logging.info("Adding images to video", images)
        clips = [video_clip]
        video_duration = video_clip.duration
        
        logging.info("Enhancing prompts")
        # Enhance prompts and generate images
        for i, image_object in enumerate(images):
            prompt = image_object["prompt"]
            enhanced_prompt = enhance_prompt("openai", openai_api_key, prompt, model="gpt-3.5-turbo-0125")
            images[i]["enhanced_prompt"] = enhanced_prompt

        logging.info("Generating images")
        # Generate and download images
        for i, image_object in enumerate(images):
            image_url = await generate_image(service="pollinations", prompt=image_object["enhanced_prompt"])
            images[i]["image_url"] = image_url
            image_path = download_image(image_object["image_url"])
            images[i]["image_path"] = image_path

        logging.info("Adding images to video")
        # Add images with timestamps
        for i, image_object in enumerate(images):
            if image_object["image_path"] is not None:
                try:
                    # Get start time from current image
                    start_time = float(image_object["timestamp"])
                    
                    # Calculate end time (use next image's timestamp or video end)
                    if i < len(images) - 1:
                        end_time = float(images[i + 1]["timestamp"])
                    else:
                        end_time = video_duration
                    
                    duration = end_time - start_time
                    
                    image_clip = (ImageClip(image_object["image_path"])
                                .set_duration(duration)
                                .set_position(('center', 70))
                                .resize(height=video_clip.h / 3)
                                .set_start(start_time))
                    
                    clips.append(image_clip)
                except Exception as e:
                    logging.error(f"Error processing image at timestamp {image_object['timestamp']}: {e}")
        
        return CompositeVideoClip(clips)

    def render_final_video(self, final_clip) -> str:
        """Render the final video with all components added."""
        unique_id = uuid.uuid4()
        result_dir = os.path.abspath(os.path.join(self.base_dir, '../result'))
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, f"final_video_{unique_id}.mp4")
        
        # Ensure even dimensions
        width, height = final_clip.w, final_clip.h
        if width % 2 != 0:
            width -= 1
        if height % 2 != 0:
            height -= 1
        
        final_clip = final_clip.resize(newsize=(width, height))
        
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            preset='veryfast',
            ffmpeg_params=['-crf', '10', '-pix_fmt', 'yuv420p'],
            audio_codec='aac',
            audio_bitrate='128k',
            fps=30

        )
        
        logging.info("Final video rendered successfully.")
        return output_path
    
    def cleanup_files(self, file_paths, image_paths=None):
        """Delete temporary files and generated images to clean up the workspace."""
        # Clean up temporary files
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted temporary file: {file_path}")
                else:
                    logging.warning(f"File not found: {file_path}")
            except Exception as e:
                logging.error(f"Error deleting file {file_path}: {e}")
        
        # Clean up generated images
        if image_paths:
            for image_path in image_paths:
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logging.info(f"Deleted generated image: {image_path}")
                    else:
                        logging.warning(f"Image not found: {image_path}")
                except Exception as e:
                    logging.error(f"Error deleting image {image_path}: {e}")

    

## Pending stuff to do in this class:
# - Separate audio from captions in the add_audio_and_captions_to_video method
# - Render method separated from the add_images_to_video method

