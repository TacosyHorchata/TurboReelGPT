   # 🎬🔮 Mediachain

   ## Langchain for creating audiovisual experiences

   <p align="center">
   <a href="https://discord.gg/bby6DYsCPu">
      <img src="https://dcbadge.vercel.app/api/server/bby6DYsCPu?compact=true&style=flat">
   </a>
   <a href="https://star-history.com/#tacosyhorchata/mediachain)">
      <img src="https://img.shields.io/github/stars/tacosyhorchata/mediachain?style=social">
   </a>
   </p>

   ---

   ## What is Mediachain?

   AI toolkit for creating audiovisual experiences.

   The goal is simple: **help developers produce great audiovisual experiences.**

   ---

   ## Showcase 

   ### Story
   https://github.com/user-attachments/assets/91469491-03fe-4548-951c-8e52f729d28a

   ### Reddit Stories
   https://github.com/user-attachments/assets/a0231e08-ec6e-4dea-b7de-44b4627ec185


   ## Why Mediachain exists?

   A few months ago, I started working on [**TurboReel**](https://turboreelgpt.tech), an automation tool for generating short videos 100x faster. It was built with **MoviePy** and **OpenAI**. While MoviePy is great for basic tasks, I found it limiting for more complex ones. Plus, I relied too heavily on OpenAI, which made it tricky to keep improving the project.

   We ended up using Revideo for the video processing tasks. 

   That made me realize that AI tools should be separated from the video engine(MoviePy, Revideo, Remotion, etc.) or AI service(GPT, ElevenLabs, Dalle, Runway, Sora, etc.) you choose to use. So you can easily switch between the best out there.

   Also, there is no hub for audiovisual generation knowledge. So this is my attempt to create that hub.

   ---

   ## Technologies

   - **Image generation**: [Pollinations](https://github.com/pollinations/pollinations), [Dalle](https://openai.com/index/dall-e-3/), [Leonardo](https://leonardo.ai).
   - **Script generation**: [OpenAI](https://openai.com).
   - **Video generation**: Not yet.
   - **Audio generation**: [OpenAI](https://openai.com), [ElevenLabs](https://elevenlabs.io).
   - **Video editing**: [MoviePy](https://zulko.github.io/moviepy/), [Revideo](https://re.video).

   Special shoutout to [**Pollinations**](https://pollinations.ai) for their free image generation API.
   ![Pollinations](https://avatars.githubusercontent.com/u/86964862?s=48&v=4)


   ## Vision

   Mediachain is designed to be the **LangChain for audiovisual creation**, a centralized toolkit and knowledge hub for the field.  

   - **Image and video generation** is just the start.  
   - Emerging features like **video embeddings** (which can understand the context of videos) are next along with powerful video generation models.  

   Our mission is to **push boundaries and make audiovisual generation accessible** for everyone at a fraction of the cost of current solutions.

   ---

   ## Roadmap

   Here’s what’s planned for Mediachain:

   - [ ] Add the **Revideo engine** to the examples folder.  
   - [ ] Introduce new features like **image animation**, **image editing**, **voice cloning**, and **AI avatars**.  
   - [ ] Support more video generation services and models.  
   - [ ] Create useful templates using Mediachain.  
   - [ ] Publish the package on **PyPI**.  
   - [ ] Write detailed documentation.  
   - [ ] Develop a beginner-friendly guide to audiovisual generation.  

   ---

   ## How to Get Started

   The project is organized into the following folders:

   - **`core`**: Core functionality of MediaChain. See the [core README](core/README.md) for more information.
   - **`examples`**: Examples showing how to use MediaChain with tools like **MoviePy**, **Revideo**, and **Remotion**. See the [examples README](examples/README.md) for more information.

   ### Running Your First Example

   To test MediaChain, start with the **Reddit Stories example**. This template creates a video from Reddit posts.

   1. **Make Sure You’ve Got Python**: Grab Python 3.10.x from [python.org](https://www.python.org/downloads/release/python-31012/).

   2. **Install FFmpeg and ImageMagick**:
      - **For Windows**: Download the binaries from [FFmpeg](https://ffmpeg.org/download.html) and [ImageMagick](https://imagemagick.org/script/download.php). Just add them to your system's PATH.
      - **For macOS**: Use Homebrew (if you haven’t tried it yet, now’s the time!):
      ```bash
      brew install ffmpeg imagemagick
      ```
      - **For Linux**: Just use your package manager:
      ```bash
      sudo apt-get install ffmpeg imagemagick
      ```

   3. **Get the Required Python Packages**:
      ```bash
      pip install -r requirements.txt
      ```
   
   4. **Add your OpenAI API key**:
      Add your OpenAI API key to the `.env` file as `OPENAI_API_KEY`.

   5. **Edit the examples variables**:
      - Go to `examples/moviepy_engine/reddit_stories/main_moviepy.py`.
      - Change the `prompt` variable to whatever you want.
      - Change the `video_url` variable to the video you want to use as background.

   6. **Run the example**:  
      ```bash
      python3 examples/moviepy_engine/reddit_stories/main_moviepy.py
      ```

   ## Community

   Feel free to contribute, ask questions, or share your ideas!

   Discord: https://discord.gg/bby6DYsCPu

   Made with ❤️ by [@TacosyHorchata](https://github.com/TacosyHorchata)
