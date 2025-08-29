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

    def add_subtitles(self, input_video: str, ass_path: str, audio_path: str, output_path: str, title_audio_duration: float):
        try:
            ass_path_ffmpeg = Path(ass_path).as_posix().replace(":", "\\:")
            ass_path_quoted = f"'{ass_path_ffmpeg}'"

            # drawbox Filter: mittig, 40% der Breite, 20% der Höhe, voll deckend
            drawbox_filter = (
                "drawbox="
                "x=(iw-w)/2:"
                "y=(ih-h)/2:"
                "w=iw*0.4:"
                "h=ih*0.2:"
                f"color=white@1.0:t=fill:"
                f"enable='between(t,0,{title_audio_duration})'"
            )

            # combine drawbox und ass
            combined_filter = f"{drawbox_filter},ass={ass_path_quoted}"

            logging.info("🎞️ Füge Untertitel + weißen Kasten hinzu...")
            subprocess.run([
                self.ffmpeg_path,
                "-i", input_video,
                "-vf", combined_filter,
                "-c:a", "copy",
                output_path
            ], check=True)

            logging.info("✅ Untertitel + Rechteck erfolgreich eingefügt.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Fehler beim Einfügen: {e}")


    def shift_ass_timings(self, ass_path: str, offset_seconds: float):
        def shift_timestamp(timestamp: str) -> str:
            h, m, s_ms = timestamp.split(":")
            s, ms = s_ms.split(".")
            total_ms = (int(h) * 3600 + int(m) * 60 + int(s)) * 100 + int(ms)
            total_ms += int(offset_seconds * 100)

            new_h = total_ms // (3600 * 100)
            new_m = (total_ms % (3600 * 100)) // (60 * 100)
            new_s = (total_ms % (60 * 100)) // 100
            new_ms = total_ms % 100

            return f"{new_h:01}:{new_m:02}:{new_s:02}.{new_ms:02}"

        with open(ass_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                parts = line.split(",", 3)
                start_time = parts[1]
                end_time = parts[2]
                shifted_start = shift_timestamp(start_time)
                shifted_end = shift_timestamp(end_time)
                new_line = f"{parts[0]},{shifted_start},{shifted_end},{parts[3]}"
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        with open(ass_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)



    def generateVideoShort(self, audio_filenames: list, add_subs: bool = True):
        title_audio_path = os.path.join(self.audio_folder, audio_filenames[0])  # title.mp3
        post_audio_path = os.path.join(self.audio_folder, audio_filenames[1])    # post.mp3
        base_name = "_".join([Path(filename).stem for filename in audio_filenames])

        # Pfade
        cut_video_path = os.path.join(self.temp_folder, "cut_bg.mp4")
        no_audio_path = os.path.join(self.temp_folder, "no_audio.mp4")
        merged_path = os.path.join(self.temp_folder, "merged.mp4")
        final_output_path = os.path.join(self.output_folder, f"{base_name}_short.mp4")
        ass_path = os.path.join(self.subtitle_folder, "post.ass")

        # Längen der Audiodateien
        title_audio_duration = self.get_audio_duration(title_audio_path)
        post_audio_duration = self.get_audio_duration(post_audio_path)

        # Gesamtvideo-Dauer = Länge der beiden Audiodateien zusammen
        total_duration = title_audio_duration + post_audio_duration

        # Hintergrundvideo vorbereiten
        background_video = self.pick_random_background()
        logging.info("✂️  Schneide Hintergrundvideo...")
        self.cut_background_video(background_video, cut_video_path, duration=total_duration)

        logging.info("🔇 Entferne Originalton...")
        self.remove_audio(cut_video_path, no_audio_path)

        logging.info("🔊 generiere merged audio datei titel + post...")
        combined_audio_path = os.path.join(self.audio_folder, "combined_audio.mp3")
        subprocess.run([
            self.ffmpeg_path,
            "-i", title_audio_path,
            "-i", post_audio_path,
            "-filter_complex", "[0][1]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            "-y", combined_audio_path
        ], check=True)

        logging.info("🔊 Füge Merged-Audio ein...")
        self.merge_audio_and_video(no_audio_path, combined_audio_path, merged_path)

        #shifting ass datei damit untertitel passenden Startzeitpunkt haben
        self.shift_ass_timings(ass_path, offset_seconds=title_audio_duration)

        logging.info("💬 Füge .ass Untertitel hinzu...")
        self.add_subtitles(merged_path, ass_path, post_audio_path, final_output_path, title_audio_duration)


        logging.info("✅ Video wurde erfolgreich erstellt!")