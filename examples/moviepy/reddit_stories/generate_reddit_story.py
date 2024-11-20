import yaml
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, CompositeAudioClip, ColorClip
import random
from openai import OpenAI
import os
import re

# Update the config loading to use the correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Accessing configuration values
openai_api_key = os.getenv('OPENAI_API_KEY')

""" TurboReel-Moviepy imports """
from ..src.image_handler import ImageHandler
from ..src.video_editor import VideoEditor
from ..src.captions.caption_handler import CaptionHandler

""" MediaChain imports """

# MediaChain Script
from core.script.script_generation import generate_script
# MediaChain Audio
from core.audio.text_to_speech.tts_generation import generate_text_to_speech
from core.audio.speech_to_text.stt_generation import generate_speech_to_text
from core.image.utils.sync_with_script import generate_image_timestamps
# MediaChain Image
from core.image.generation.image_generation import generate_image

class RedditStoryGenerator:
    def __init__(self):
        self.video_editor: VideoEditor = VideoEditor()
        self.caption_handler: CaptionHandler = CaptionHandler()

    async def create_reddit_question_clip(self, reddit_question: str, video_height: int = 720) -> tuple[TextClip, str]:
        """Create a text clip for the Reddit question and generate its audio."""
        try:
            # Generate audio for the Reddit question
            reddit_question_audio_path: str = generate_text_to_speech("openai", openai_api_key, reddit_question) # this could be elevenlabs or azure_openai

            # Getting audio duration for further processing
            reddit_question_audio_clip: AudioFileClip = AudioFileClip(reddit_question_audio_path)
            reddit_question_audio_duration: float = reddit_question_audio_clip.duration
            reddit_question_audio_clip.close()

            # Calculate text clip size based on video width
            text_width = int((video_height * 9 / 16) * 0.7)  # 90% of video width after cropped to 9/16
            text_height = int(text_width * 0.35)  # 30% of cropped video width

            # Create a text clip for the Reddit question
            reddit_question_text_clip = TextClip(
                reddit_question,
                fontsize=int(video_height * 0.03),  # 2.5% of video height for font size
                color='black',
                bg_color='white',
                size=(text_width, text_height),  # Allow height to adjust automatically
                method='caption',
                align='center'
            ).set_duration(reddit_question_audio_duration)

            return reddit_question_text_clip, reddit_question_audio_path
        except Exception as e:
            logging.error(f"Error creating Reddit question clip: {e}")
            return None, None

    async def generate_video(self, video_path_or_url: str = '', 
                            video_path: str = '', 
                            video_url: str = '', 
                            video_topic: str = '',
                            captions_settings: dict = {},
                            add_images: bool = True
                            ) -> dict:
        """Generate a video based on the provided topic or ready-made script.

        Args:
            video_path_or_url (str): 'video_path' or 'video_url', depending on which one is provided.
            video_path (str): The path of the video if provided.
            video_url (str): The URL of the video to download.
            video_topic (str): The topic of the video if script type is 'based_on_topic'.        
            captions_settings (dict): The settings for the captions. (font, color, etc)

        Returns:
            dict: A dictionary with the status of the video generation and a message.
        """
        clips_to_close = []
        try:
            if not video_path_or_url:
                raise ValueError("video_path_or_url cannot be empty.")

            if not video_path and not video_url:
                raise ValueError("Either video_path or video_url must be provided.")

            if not video_topic:
                raise ValueError("For 'based_on_topic', the video topic should not be null.")
            
            """ Download or getting video """
            video_path: str = video_path if video_path_or_url == 'video_path' else self.video_editor.download_video(video_url)
            if not video_path:
                logging.error("Failed to download video.")
                return {"status": "error", "message": "No video path provided."}
            # Get video dimensions
            with VideoFileClip(video_path) as video:
                video_width, video_height = video.w, video.h

            """ Handle Script Generation and Process """
            # Generate the script or use the provided script
            script: dict = generate_script("openai", openai_api_key, video_topic)
            
            if not script:
                logging.error("Failed to generate script.")
                return {"status": "error", "message": "Failed to generate script."}

            """ Define video length for each clip (question and story) """
            # Initialize Reddit clips
            reddit_question_text_clip, reddit_question_audio_path = await self.create_reddit_question_clip(video_topic, video_height)
            reddit_question_audio_clip: AudioFileClip = AudioFileClip(reddit_question_audio_path)
            reddit_question_audio_duration: float = reddit_question_audio_clip.duration
            clips_to_close.append(reddit_question_audio_clip)
            # Initialize Background video
            background_video_clip: VideoFileClip = VideoFileClip(video_path)
            clips_to_close.append(background_video_clip)
            background_video_length: float = background_video_clip.duration
            ## Initialize Story Audio
            story_audio_path: str = generate_text_to_speech("openai", openai_api_key, script)
            if not story_audio_path:
                logging.error("Failed to generate audio.")
                return {"status": "error", "message": "Failed to generate audio."}

            story_audio_clip: AudioFileClip = AudioFileClip(story_audio_path)
            clips_to_close.append(story_audio_clip)
            story_audio_length: float = story_audio_clip.duration
        
            # Calculate video times to cut clips
            max_start_time: float = background_video_length - story_audio_length - reddit_question_audio_duration
            start_time: float = random.uniform(0, max_start_time)
            end_time: float = start_time + reddit_question_audio_duration + story_audio_length
            
            """ Cut video once """
            cut_video_path: str = self.video_editor.cut_video(video_path, start_time, end_time)
            cut_video_clip = VideoFileClip(cut_video_path)
            clips_to_close.append(cut_video_clip)

            """ Handle reddit question video """
            reddit_question_video = cut_video_clip.subclip(0, reddit_question_audio_duration)
            reddit_question_video = reddit_question_video.set_audio(reddit_question_audio_clip)
            reddit_question_video = self.video_editor.crop_video_9_16(reddit_question_video)

            # Add the text clip to the video
            reddit_question_video = CompositeVideoClip([
                reddit_question_video,
                reddit_question_text_clip.set_position(('center', 'center'))
            ])

            """ Handle story video """
            story_video = cut_video_clip.subclip(reddit_question_audio_duration)
            story_video = story_video.set_audio(story_audio_clip)
            story_video = self.video_editor.crop_video_9_16(story_video)

            font_size = video_width * 0.025

            # Generate subtitles
            story_subtitles_path, story_subtitles_clips = await self.caption_handler.process(
                story_audio_path, # THIS SHOULD RECEIVE A JSON WITH THE WORDS AND TIMESTAMPS
                captions_settings.get('color', 'white'),
                captions_settings.get('shadow_color', 'black'),
                captions_settings.get('font_size', font_size),
                captions_settings.get('font', 'LEMONMILK-Bold.otf')
            )

            video_context: str = video_topic
            story_image_paths = generate_image_timestamps("openai", openai_api_key, script) if add_images else [] # CREATE FUNCTION IN MEDIACHAIN
            
            story_video = self.video_editor.add_images_to_video(story_video, story_image_paths, # ADD TIMESTAMPS TO EACH ADDED IMAGE
            
            story_video = self.video_editor.add_captions_to_video(story_video, story_subtitles_clips)
            # Combine clips
            combined_clips = CompositeVideoClip([
                reddit_question_video,
                story_video.set_start(reddit_question_audio_duration)
            ])

            final_video_output_path = self.video_editor.render_final_video(combined_clips)
            
            # Cleanup: Ensure temporary files are removed
            self.video_editor.cleanup_files([story_audio_path, cut_video_path, story_subtitles_path, reddit_question_audio_path], story_image_paths)
            
            logging.info(f"FINAL OUTPUT PATH: {final_video_output_path}")
            return {"status": "success", "message": "Video generated successfully.", "output_path": final_video_output_path}
        
        except Exception as e:
            logging.error(f"Error in video generation: {e}")
            return {"status": "error", "message": f"Error in video generation: {str(e)}"}
        finally:
            # Close all clips
            for clip in clips_to_close:
                clip.close()
