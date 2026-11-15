# DoBu — Multipurpose Discord Bot

**DoBu** is an asynchronous Python Discord bot built with `discord.py`, combining YouTube music streaming, conversational AI, live weather forecasts, and news updates through native slash commands.

## Key Features
* **YouTube Music Streaming (`/play`):** Searches and streams audio directly from YouTube URLs or search queries into Discord voice channels using `yt-dlp` and `FFmpeg`.
* **Conversational AI Assistant:** Powered by **Google Gemini** (`google-genai`) with per-channel conversation memory.
* **Real-Time Weather (`/weather`):** Fetches live weather data for any location via the **OpenWeatherMap API**.
* **Latest News:** Retrieves current headlines using **News API**.

## Tech Stack
* **Language:** Python 3
* **Discord Library:** `discord.py`
* **Media Pipeline:** `yt-dlp`, `FFmpeg`
* **External Integrations:** Google Gemini API, OpenWeatherMap API, News API
