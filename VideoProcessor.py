import os
import random
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class VideoProcessor:
    def __init__(self):
        # Projektverzeichnis (also da, wo dein Script liegt)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(base_dir, "temp")
        ffmpeg_dir = os.path.join(base_dir, "ffmpeg-7.1.1-essentials_build", "bin")

        # Lokale Pfade innerhalb des Projekts
        self.audio_folder = os.path.join(temp_dir, "Generated Audio")
        self.subtitle_folder = os.path.join(temp_dir, "Generated Subtitles")
        self.temp_folder = os.path.join(temp_dir, "Generated Videos")
        self.ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

        # Optional: FFmpeg in PATH hinzufügen, falls du subprocess nutzt
        os.environ["PATH"] += os.pathsep + ffmpeg_dir

        # Falls du Backgrounds und fertige Outputs noch extern hast:
        self.background_folder = r"D:\---Automated Content\Background Visuals"
        self.output_folder = r"D:\---Automated Content\Output Videos"

        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    def pick_random_background(self) -> str:
        videos = [f for f in os.listdir(self.background_folder) if f.endswith((".mp4", ".mov"))]
        return os.path.join(self.background_folder, random.choice(videos))

    def get_audio_duration(self, audio_path: str) -> float:
        result = subprocess.run([
            self.ffmpeg_path,
            "-i", audio_path,
            "-hide_banner"
        ], capture_output=True, text=True)

        for line in result.stderr.splitlines():
            if "Duration" in line:
                time_str = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = time_str.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
        logging.warning("⚠️ Konnte Audiodauer nicht erkennen – verwende Fallback 60s.")
        return 60.0

    def remove_audio(self, input_video: str, output_video: str):
        subprocess.run([
            self.ffmpeg_path,
            "-i", input_video,
            "-c", "copy",
            "-an",
            output_video
        ])

    def cut_background_video(self, input_path: str, output_path: str, duration: float):
        start_time = random.randint(0, 30)
        subprocess.run([
            self.ffmpeg_path,
            "-ss", str(start_time),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            output_path
        ])

    def merge_audio_and_video(self, video_path: str, audio_path: str, output_path: str):
        subprocess.run([
            self.ffmpeg_path,
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ])

    def add_subtitles(self, input_video: str, ass_path: str, audio_path: str, output_path: str):
        try:
            ass_path_ffmpeg = Path(ass_path).as_posix().replace(":", "\\:")
            ass_path_quoted = f"'{ass_path_ffmpeg}'"
            logging.info(f"✅ Füge Untertitel hinzu mit Pfad: {ass_path_quoted}")
            subprocess.run([
                self.ffmpeg_path,
                "-i", input_video,
                "-vf", f"ass={ass_path_quoted}",
                "-c:a", "copy",
                output_path
            ], check=True)
            logging.info("✅ Untertitel erfolgreich hinzugefügt.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Fehler beim Hinzufügen der Untertitel: {e}")


    def generateVideoShort(self, audio_filename: str, add_subs: bool = True):
        audio_path = os.path.join(self.audio_folder, audio_filename)
        base_name = Path(audio_filename).stem

        # Pfade
        cut_video_path = os.path.join(self.temp_folder, "cut_bg.mp4")
        no_audio_path = os.path.join(self.temp_folder, "no_audio.mp4")
        merged_path = os.path.join(self.temp_folder, "merged.mp4")
        final_output_path = os.path.join(self.output_folder, f"{base_name}_short.mp4")
        ass_path = os.path.join(self.subtitle_folder, f"{base_name}.ass")

        # Audio-Länge
        audio_duration = self.get_audio_duration(audio_path)

        # Hintergrundvideo vorbereiten
        background_video = self.pick_random_background()
        logging.info("✂️  Schneide Hintergrundvideo...")
        self.cut_background_video(background_video, cut_video_path, duration=audio_duration)

        logging.info("🔇 Entferne Originalton...")
        self.remove_audio(cut_video_path, no_audio_path)

        logging.info("🔊 Füge eigene Audiospur ein...")
        self.merge_audio_and_video(no_audio_path, audio_path, merged_path)

        logging.info("💬 Füge .ass Untertitel hinzu...")
        self.add_subtitles(merged_path, ass_path, audio_path, final_output_path) #TODO diese methoden nutzung muss noch geschehen

