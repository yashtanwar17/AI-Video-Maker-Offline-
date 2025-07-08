import nltk,sys,os
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

nltk_path = os.path.join(base_path, 'nltk_data')
nltk.data.path.append(nltk_path)

import sys
import os
import re
import random

import asyncio
import aiofiles
import edge_tts
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QCheckBox, QSlider, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
)
from moviepy.audio.AudioClip import CompositeAudioClip
from contextlib import redirect_stdout
from io import StringIO


class QtLogger(StringIO):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def write(self, msg):
        self.output_widget.append(msg)
        QApplication.processEvents()


class AIVideoMakerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Short Video Maker")
        self.setGeometry(100, 100, 650, 700)
        self.setStyleSheet(self.load_styles())

        layout = QVBoxLayout()

        self.script_label = QLabel("Enter Script:")
        self.script_input = QTextEdit()
        layout.addWidget(self.script_label)
        layout.addWidget(self.script_input)

        self.voice_selector = QComboBox()
        self.voice_selector.addItems([
            "en-US-JennyNeural",
            "en-US-AmberNeural",
            "en-US-AriaNeural",
            "en-US-AnaNeural",
            "en-US-GuyNeural",
            "en-US-DavisNeural",
            "hi-IN-SwaraNeural",
            "hi-IN-MadhurNeural"
        ])
        layout.addWidget(QLabel("Select Voice:"))
        layout.addWidget(self.voice_selector)

        self.video_button = QPushButton("Select Gameplay Video")
        self.video_button.clicked.connect(self.select_video)
        self.video_path_label = QLabel("No video selected.")
        layout.addWidget(self.video_button)
        layout.addWidget(self.video_path_label)

        self.music_button = QPushButton("Select Background Music")
        self.music_button.clicked.connect(self.select_music)
        self.music_path_label = QLabel("No background music selected.")
        layout.addWidget(self.music_button)
        layout.addWidget(self.music_path_label)

        self.music_volume_label = QLabel("Background Music Volume:")
        self.music_volume_slider = QSlider(Qt.Horizontal)
        self.music_volume_slider.setRange(0, 100)
        self.music_volume_slider.setValue(50)
        layout.addWidget(self.music_volume_label)
        layout.addWidget(self.music_volume_slider)

        self.progress_bar_checkbox = QCheckBox("Show Yellow Progress Bar")
        layout.addWidget(self.progress_bar_checkbox)

        self.start_button = QPushButton("Generate AI Short")
        self.start_button.clicked.connect(self.generate_video)
        layout.addWidget(self.start_button)

        self.status = QLabel("")
        layout.addWidget(self.status)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Build Log:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def load_styles(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }

        QTextEdit, QLineEdit {
            background-color: #2c2c3c;
            border: 1px solid #444;
            padding: 5px;
            color: white;
            border-radius: 5px;
        }

        QLabel {
            font-weight: bold;
        }

        QComboBox {
            background-color: #2c2c3c;
            border: 1px solid #555;
            padding: 5px;
            color: white;
            border-radius: 4px;
        }

        QCheckBox {
            padding: 5px;
        }

        QPushButton {
            background-color: #007acc;
            color: white;
            border-radius: 6px;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #008ae6;
        }

        QSlider::groove:horizontal {
            border: 1px solid #333;
            height: 8px;
            background: #2c2c3c;
        }

        QSlider::handle:horizontal {
            background: #007acc;
            border: 1px solid #555;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }

        QTextEdit#log_output {
            background-color: #1e1e1e;
            color: #00ffcc;
        }
        """

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Gameplay Video", "", "MP4 Files (*.mp4)")
        if path:
            self.video_path_label.setText(path)

    def select_music(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Background Music", "", "Audio Files (*.mp3 *.wav)")
        if path:
            self.music_path_label.setText(path)

    def split_into_sentences(self, text):
        text = text.strip().replace('\n', ' ')
        return re.split(r'(?<=[.?!])\s+', text)

    def split_sentence_lines(self, sentence, max_length=45):
        words = sentence.split()
        lines = []
        current = ""
        for word in words:
            if len(current + word) <= max_length:
                current += word + " "
            else:
                lines.append(current.strip())
                current = word + " "
        lines.append(current.strip())
        return "\n".join(lines)

    def generate_video(self):
        script = self.script_input.toPlainText().strip()
        voice = self.voice_selector.currentText()
        video_path = self.video_path_label.text()
        music_path = self.music_path_label.text()
        show_progress_bar = self.progress_bar_checkbox.isChecked()
        music_volume = self.music_volume_slider.value() / 100

        if not script or not os.path.exists(video_path):
            self.status.setText("❌ Missing script or video.")
            return

        self.status.setText("⏳ Generating video. Please wait...")
        self.log_output.clear()
        QApplication.processEvents()

        async def run_pipeline():
            self.log_output.append("Generating TTS...")
            communicator = edge_tts.Communicate(text=script, voice=voice)
            audio_bytes = bytearray()

            async for chunk in communicator.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])

            async with aiofiles.open("audio.mp3", "wb") as f:
                await f.write(audio_bytes)

            audio = AudioFileClip("audio.mp3")
            duration = audio.duration

            video = VideoFileClip(video_path)
            start_time = random.uniform(0, max(0.1, video.duration - duration - 0.1))
            clip = video.subclip(start_time, start_time + duration).set_audio(audio)

            if music_path and os.path.exists(music_path):
                music = AudioFileClip(music_path).volumex(music_volume)
                final_audio = CompositeAudioClip([audio, music.set_duration(audio.duration)])
                clip = clip.set_audio(final_audio)

            sentences = self.split_into_sentences(script)
            per_sentence_duration = duration / len(sentences)
            subtitle_clips = []

            for i, sentence in enumerate(sentences):
                formatted = self.split_sentence_lines(sentence)
                txt_clip = TextClip(
                    formatted,
                    fontsize=52,
                    font="Arial-Bold",
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                ).set_start(i * per_sentence_duration)\
                 .set_duration(per_sentence_duration)\
                 .set_position("center")
                subtitle_clips.append(txt_clip)

            overlays = subtitle_clips

            if show_progress_bar:
                bar = ColorClip(size=(1, 10), color=(255, 255, 0)).set_duration(duration)
                bar = bar.set_position(lambda t: ("left", clip.h - 10))\
                         .resize(lambda t: (max(1, int(clip.w * (t / duration))), 10))
                overlays.append(bar)

            final = CompositeVideoClip([clip, *overlays])

            qt_logger = QtLogger(self.log_output)
            with redirect_stdout(qt_logger):
                final.write_videofile("output.mp4", codec="libx264", audio_codec="aac")

        asyncio.run(run_pipeline())
        self.status.setText("✅ Video Generation Complete! Saved as output.mp4.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIVideoMakerGUI()
    window.show()
    sys.exit(app.exec_())
