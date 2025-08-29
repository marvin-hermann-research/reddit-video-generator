# Automated Reddit Short-Form Video Generator

## Project Description
This project is a tool for fully automated generation of short-form videos from Reddit posts, featuring AI-generated voiceovers and synchronized subtitles.  
It scrapes multiple subreddits, converts posts to TTS audio, generates subtitles, and merges these with pre-prepared background videos to produce ready-to-share vertical videos.

---

## Features
- Automatic scraping of Reddit posts via Reddit API.  
- AI-generated voiceovers for each post using OpenAI TTS.  
- Synchronized subtitles in `.ASS` format.  
- Integration with pre-made vertical background videos.  
- Configurable content filtering for text sanitation and profanity removal.  
- Modular pipeline architecture for easy extension and customization.

---

## Usage / How to Run
1. Configure your target subreddits and API credentials in the `.env` or configuration file.  
2. Run the `MainController.py` script to start the pipeline.  
3. The system will:
   - Scrape posts via `PostGrabber.py`  
   - Generate TTS audio using `WebsiteInteractor.py`  
   - Produce subtitles via `SubtitleGenerator.py`  
   - Assemble the final video with `VideoProcessor.py`  
4. Output videos are saved in the designated output folder.

### Workflow / Example Screenshots

<p align="center">
  <img width="500" height="794" alt="image" src="https://github.com/user-attachments/assets/9ae3c92c-fcd1-4c1b-978b-77b366a98a03" />
  <img width="500" height="794" alt="image" src="https://github.com/user-attachments/assets/10137275-8d87-4859-a6d9-b7969045e4c1" />
</p>
<p align="center">
  <img width="300" height="156" alt="image" src="https://github.com/user-attachments/assets/37e944c6-add7-4ae5-9aea-b9d18e8b8f54" />
  <img src="example.gif" alt="Generated Video Example" width="400"/>
</p>

---

## Motivation
This project was motivated by the need to **quickly generate engaging short-form content** from Reddit stories with minimal manual effort.  
It combines **AI voice synthesis, automatic subtitling, and video production** into a unified, modular workflow, providing a scalable solution for content creation.

---

## Project Context / Scope
This tool is intended as an **advanced learning and experimental project** combining AI, multimedia processing, and automation.  
It demonstrates **full pipeline orchestration**, from raw Reddit posts to finished short videos, and is designed for **scalability and modularity**.

---

## Architecture Overview
The system follows a **pipeline-based design**, with each component handling a distinct stage of content processing:

- **ContentFilter.py**: Text sanitization, profanity filtering, and pattern management.  
- **PostGrabber.py**: Reddit scraping, engagement filtering, and multi-subreddit support.  
- **WebsiteInteractor.py**: Automated TTS generation and file handling.  
- **SubtitleGenerator.py**: Generates `.ASS`/`.SRT` subtitles with styling for vertical videos.  
- **VideoProcessor.py**: Merges audio, subtitles, and background video using FFmpeg.  
- **MainController.py**: Orchestrates the full pipeline, handles errors, and tracks progress.  
- **SubtitelStyleConfig.py**: Configuration for subtitle appearance and animation.

### Pipeline / Processing Screenshots

<p align="center">
  <img width="144" height="117" alt="image" src="https://github.com/user-attachments/assets/651796f2-346d-427c-9f1f-da4f631da66e" />
  <img width="346" height="145" alt="image" src="https://github.com/user-attachments/assets/c77060d9-fa8f-4459-b61a-f1e0c5576153" />
  <img width="114" height="102" alt="image" src="https://github.com/user-attachments/assets/770c70db-1482-4168-b671-6e93cc8d66e9" />
  <img width="228" height="143" alt="image" src="https://github.com/user-attachments/assets/6002a116-bf2a-45d6-a78b-67a190b913f7" />
</p>

---

## Lessons Learned
- Modular pipeline design for multimedia processing  
- Integration of AI voice services with Python automation  
- Advanced subtitle styling and dynamic positioning  
- Full orchestration of scraping, processing, and video assembly  
- Handling of real-world edge cases in text and audio data

---

## Future / Possible Enhancements
- Implement a **database for used posts** to avoid repetition.  
- Expand content filtering with advanced bad-word detection.  
- Automatically clean up temporary files after generation.  
- High-quality background video acquisition and selection.  
- Automatic detection and handling of audio durations (too short/long).  

---

## Logs
- Full console log of a run: [View log](logs/full_run.log)

---

## Disclaimer
This project is **experimental and intended for learning purposes**.  
It showcases a complex AI-powered content generation pipeline but is not production-ready.  
Expect rough edges, rapid prototyping decisions, and early-stage code.
