import os
import logging
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from openai import OpenAI  # Correct import
import whisper
import pysrt  # or any other subtitle handling library
from yt_dlp import YoutubeDL
from pathlib import Path  # Import Path for file handling

from dotenv import load_dotenv  # To load environment variables

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

class AIShortGenerator:
    def __init__(self, openai_api_key):
        self.openai = OpenAI(api_key=openai_api_key)  # Initialize OpenAI with the API key

    def download_video(self, youtube_url):
        try:
            ydl_opts = {
                'format': 'bestvideo[height<=360]+bestaudio',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
                info_dict = ydl.extract_info(youtube_url, download=False)
                video_path = ydl.prepare_filename(info_dict)
                # Ensure the video path is in mp4 format
                if not video_path.endswith('.mp4'):
                    video_path = video_path.rsplit('.', 1)[0] + '.mp4'
            logging.info("Video downloaded successfully.")
            return video_path  # Return the path of the downloaded video
        except Exception as e:
            logging.error(f"Error downloading video: {e}")  # Log the error message
            return None  # Ensure to return None on error

    def cut_video(self, video_path, start_time, end_time):
        if not os.path.exists(video_path):
            logging.error(f"Video file does not exist, {video_path}")
            return
        try:
            clip = VideoFileClip(video_path)
            cut_clip = clip.subclip(start_time, end_time)
            cut_clip.write_videofile("assets/cut_video.mp4")
            logging.info("Video cut successfully.")
            return "assets/cut_video.mp4"  # Return the path of the cut video
        except Exception as e:
            logging.error(f"Error cutting video: {e}")

    async def generate_script(self, key_points):
        try:
            completion = self.openai.chat.completions.create(  # Async call to create chat completion
                model="gpt-3.5-turbo-0125",
                max_tokens=100,
                messages=[
                    {"role": "system", "content": "You are a reddit stories narrator"},
                    {"role": "user", "content": f"Tell a reddit storie based on the following points: {key_points}"}
                ]
            )
            logging.info("Script generated successfully.")
            return completion.choices[0].message.content  # Access the message content correctly
        except Exception as e:
            logging.error(f"Error generating script: {e}")  # Log the error message
            return ""  # Return an empty string on error

    def generate_subtitles(self, audio_file):
        try:
            subtitles = self.speech_to_text(audio_file)  # Get the subtitles from speech_to_text
            srt_file = pysrt.SubRipFile()

            for index, (start, end, text) in enumerate(subtitles):
                srt_file.append(pysrt.SubRipItem(index=index + 1, start=start, end=end, text=text))

            srt_file.save('assets/subtitles.srt')  # Save as .srt
            logging.info("Subtitles generated and saved successfully.")
        except Exception as e:
            logging.error(f"Error generating subtitles: {e}")


    def speech_to_text(self, audio_file):
        try:
            audio_file = open(audio_file, "rb")  # Open the audio file
            transcript = self.openai.audio.transcriptions.create(  # Use OpenAI's transcription method
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            subtitles = []
            for word_info in transcript.words:  # Iterate through the words in the transcript
                start_time = self.convert_seconds_to_srt_time(word_info.start)  # Convert start time
                end_time = self.convert_seconds_to_srt_time(word_info.end)  # Convert end time
                text = word_info.word.strip()  # Get the word text
                subtitles.append((start_time, end_time, text))

            logging.info("Speech-to-text transcription completed.")
            return subtitles
        except Exception as e:
            logging.error(f"Error in speech-to-text transcription: {e}")
            return []

    def convert_seconds_to_srt_time(self, seconds):
        """Convert seconds into SubRipTime for SRT formatting"""
        millis = int((seconds % 1) * 1000)
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return pysrt.SubRipTime(hours, mins, secs, millis)

    async def generate_voice(self, script):
        try:
            speech_file_path = Path(__file__).parent / "assets/voice.mp3"  # Define the path for the output file
            response = self.openai.audio.speech.create(  # Create speech using the OpenAI API
                model="tts-1",
                voice="nova",  # Adjust the voice as needed
                input=script  # Use 'input' to provide the script
            )
            response.stream_to_file(speech_file_path)  # Stream the response to the specified file path
            logging.info("Voice generated successfully.")
            return speech_file_path  # Return the path of the generated audio
        except Exception as e:
            logging.error(f"Error generating voice: {e}")

    async def generate_short(self, youtube_url, start_time, end_time, key_points):
        video_path = self.download_video(youtube_url)
        if video_path:
            cut_video_path = self.cut_video(video_path, start_time, end_time)
            script = await self.generate_script(key_points)
            if script:
                audio_path = await self.generate_voice(script)
                if audio_path:
                    self.generate_subtitles(audio_path)  # Generate subtitles
                    self.add_audio_to_video(cut_video_path, audio_path, 'assets/subtitles.srt')  # Add audio and subtitles to the cut video
        else:
            logging.error("Failed to download video.")  # Log if video download fails

    def add_audio_to_video(self, video_path, audio_path, subtitles_path):
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(str(audio_path))
            final_clip = video_clip.set_audio(audio_clip)

            # Load subtitles from the SRT file
            subtitles = self.load_subtitles(subtitles_path)
            
            # Create annotated clips based on the loaded subtitles
            annotated_clips = [
                TextClip(sub.text, fontsize=40, color='cyan', font='Arial', stroke_color='green', stroke_width=0.5)  # Added stroke color and width for better contrast
                .set_position('center')
                .set_start(sub.start.ordinal / 1000)  # Convert to seconds
                .set_duration((sub.end.ordinal - sub.start.ordinal) / 1000)  # Set duration in seconds
                for sub in subtitles if sub.start is not None and sub.end is not None
            ]

            # Combine the video and subtitle clips
            final_clip = CompositeVideoClip([final_clip] + annotated_clips)
            final_clip.write_videofile("result/final_video.mp4")  # Save the final video
            logging.info("Audio and subtitles added to video successfully.")
        except Exception as e:
            logging.error(f"Error adding audio and subtitles to video: {e}")

    def load_subtitles(self, subtitles_path):
        try:
            return pysrt.open(subtitles_path)  # Return the loaded SRT file with start and end times
        except Exception as e:
            logging.error(f"Error loading subtitles: {e}")
            return []  # Return empty list on failure


# Example Usage
async def main():
    logging.info("Starting the AI Short Generator process.")  # Log the start of the process
    openai_api_key = os.getenv("OPENAI_API_KEY")
    ai_short_gen = AIShortGenerator(openai_api_key)  # Use getenv for safer access to environment variables
    video_path = ai_short_gen.download_video('https://www.youtube.com/watch?v=-yPjP85CbQE')
    if video_path:
        #logging.info(f"Video downloaded: {video_path}")  # Log the downloaded video path
        ai_short_gen.cut_video(video_path, '00:00:10', '00:00:20')
        script = await ai_short_gen.generate_script("fiction and startups")
        if script:
            logging.info("Script generated successfully.")  # Log successful script generation
            audio_path = await ai_short_gen.generate_voice(script)  # Store the generated audio path
            if audio_path:  # Check if audio generation was successful
                ai_short_gen.generate_subtitles(audio_path)
                ai_short_gen.add_audio_to_video(video_path, audio_path, 'assets/subtitles.srt')  # Add audio and subtitles to the original video  # Call to generate subtitles
    else:
        logging.error("Failed to download video.")  # Log if video download fails

# Run the main function in an asyncio event loop
import asyncio
asyncio.run(main())

