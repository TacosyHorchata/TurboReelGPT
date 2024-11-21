import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from examples.moviepy_engine.reddit_stories.generate_reddit_story import RedditStoryGenerator

async def main():
    reddit_stories = RedditStoryGenerator(openai_api_key=os.getenv('OPENAI_API_KEY'))
    result = await reddit_stories.generate_video(
        video_path_or_url="video_url",
        video_url="https://www.youtube.com/watch?v=XBIaqOm0RKQ",
        video_topic="A story about a man who falls in love with a woman",
        add_images=True
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
