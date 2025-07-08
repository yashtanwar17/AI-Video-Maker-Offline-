# AI Short Video Maker (Offline)

🎬 **See a sample video before using**: [Demo](https://github.com/yashtanwar17/AI-Video-Maker-Offline-/raw/refs/heads/main/imgs/output.mp4)

This is a **Python-based desktop app** to create TikTok-style vertical gameplay videos with **voiceovers and animated subtitles**. 
To make it fully offline, replace `edge-tts` with an offline TTS engine like pyttsx3.

![UI Screenshot](https://raw.githubusercontent.com/yashtanwar17/AI-Video-Maker-Offline-/refs/heads/main/imgs/ui.jpeg)

## Features
- Create 9:16 short videos from long gameplay footage
- AI voiceover using Edge TTS
- Subtitle generation (sentence-based)
- Background music support
- Yellow progress bar (like TikTok)

## How to Use
1. Run the app:
   ```bash
   python main.py
   ```
2. Paste your script
3. Select a voice and gameplay video
4. (Optional) Add background music and adjust volume
5. Click **"Generate AI Short"** → `output.mp4` will be created

### ✅ Recommended: Use the Precompiled `.exe`
Just double-click `ASVM.exe` — no Python or setup needed!
Scroll down for `Releases`

## 📁 Requirements
- Python 3.10+
- Packages:
  ```bash
  pip install edge-tts moviepy PyQt5 aiofiles nltk
  ```

## 📦 Releases

| Version | Download | Description |
|---------|----------|-------------|
| v1.0.0  | [Download v1.0.0](https://mega.nz/file/5r4yURRQ#awmbrs6y8NnUkigogM4n-meJS5OITu_6vMaTtRpqing) | Initial release with basic TTS, subtitles, music, and progress bar support. |

> 🔗 More versions & changelogs will be added here.
---
