# 🎧 Eris (Έρις) - The Snarky Local Voice Assistant

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-blue?style=for-the-badge)

Eris is a fully autonomous, offline-first voice assistant built with Python for Linux environments that I design in my spare time. Unlike standard corporate assistants, Eris has a sarcastic, snarky personality and runs entirely locally on your machine, ensuring 100% privacy.

She listens to your voice, understands Greek, processes commands using a local LLM, and interacts with your system to launch apps, search the web, or play music.

## ✨ Features

- **Local Voice Recognition (STT):** Uses [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) for fast, offline Speech-to-Text with VAD (Voice Activity Detection) to automatically detect when you start and stop speaking.
- **Local AI Brain:** Powered by [Ollama](https://ollama.com/) (using the `qwen2.5:7b` model). Eris processes commands and always responds with a strictly structured JSON format to trigger system actions, alongside her signature snarky commentary.
- **Smart App Launcher:** Parses Linux `.desktop` files and uses fuzzy matching (`difflib`) to gracefully handle mispronunciations or Greek-to-English translations (e.g., understanding "ντισκορντ" as "discord"). Launches apps reliably using `gio launch` (supports Steam games).
- **Web & YouTube Integration:** 
  - Performs direct Google searches.
  - Uses `yt-dlp` to silently fetch the best matching YouTube video for your query and auto-plays it in your browser.
- **Desktop Notifications:** Uses `notify-send` to let you know when she is listening.

## 🛠️ Prerequisites

Since Eris interacts deeply with the system, she is currently tailored for **Linux** environments.

### System Dependencies
Ensure you have the following installed on your system:
- `notify-send` (for desktop notifications)
- `gio` (for launching `.desktop` applications)
- A working microphone setup.

### Ollama Setup
You need to have [Ollama](https://ollama.com/) installed and running on your machine.
Pull the required model:
```bash
ollama run qwen2.5:7b
```

### Python Dependencies
It's recommended to use a virtual environment. Install the required Python libraries:
```bash
pip install sounddevice numpy faster-whisper ollama yt-dlp duckduckgo-search trafilatura
```
*(Note: You may also need to install `portaudio` via your package manager, e.g., `sudo apt install portaudio19-dev`, for `sounddevice` to work properly).*

## 🚀 Setup & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Agony-sol/voice-assistant.git
   cd voice-assistant
   ```

2. **Configure Whisper Model:**
   In `model_ai.py`, update the Whisper model path to where you have stored your local Faster-Whisper model, or change it to download a standard model string (e.g., `"medium"`).
   ```python
   model = WhisperModel("path/to/your/faster-whisper-medium", device="cpu", compute_type="int8")
   ```

3. **Run Eris:**
   ```bash
   python model_ai.py
   ```

4. **Talk to her:**
   Wait for the "🎧 Σε ακούω..." notification and speak your command in Greek.
   - *"Άνοιξε το Discord"* -> Launches Discord.
   - *"Βάλε Helloween στο YouTube"* -> Searches and plays Helloween.
   - *"Ψάξε στο Google πώς να φτιάξω παστίτσιο"* -> Opens a new browser tab with the search.

## 🧠 How it Works Under the Hood

1. **Audio Capture:** `sounddevice` constantly monitors mic input. When volume exceeds the threshold, it records until a second of silence is detected.
2. **Transcription:** The audio buffer is sent to `Faster-Whisper` which returns the transcribed Greek text.
3. **Prompting:** The text is sent to the local `Ollama` model with a strict system prompt demanding a JSON output containing keys like `command_type`, `app_name`, and a snarky `reply`.
4. **Execution:** Python parses the JSON and executes the respective `subprocess` commands (app launching, URL opening, etc.).

## 🚧 Roadmap / Future Features
- [ ] **File Manipulation:** Add ability for Eris to create, open, and append to text notes dynamically based on voice input.
- [ ] **Web Scraping (RAG):** Full integration of `duckduckgo-search` and `trafilatura` to read web articles, summarize them, and answer questions directly without opening a browser.
- [ ] **TTS (Text-to-Speech):** Give Eris an actual voice to speak her snarky replies out loud.
