import whisper
import os
from SubtitleStyleConfig import SubtitleStyleConfig

class SubtitleGenerator:
    def __init__(self, style_config=None):
        # Hole das Verzeichnis, in dem die Datei liegt
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(base_dir, "temp")

        # Passe die Ordnerpfade an das Projektverzeichnis an
        self.input_folder = os.path.join(temp_dir, "Generated Audio")
        self.output_folder = os.path.join(temp_dir, "Generated Subtitles")

        # FFmpeg relativ zum Projektverzeichnis
        ffmpeg_dir = os.path.join(base_dir, "ffmpeg-7.1.1-essentials_build", "bin")

        # FFmpeg-Pfad
        self.ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

        # Füge FFmpeg zum PATH hinzu, damit subprocess es finden kann
        os.environ["PATH"] += os.pathsep + ffmpeg_dir

        self.style_config = SubtitleStyleConfig()

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def transcribe_with_timestamps(self, audio_path):
        model = whisper.load_model("base")
        try:
            result = model.transcribe(audio_path, word_timestamps=True, task="transcribe")  # ✅ geändert
            return result['segments']
        except Exception as e:
            print(f"[ERROR] Während der Transkription trat ein Fehler auf: {e}")
            raise

    def create_srt_from_segments(self, segments, srt_path):
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments):
                start_time = self.format_time(segment['start'])
                end_time = self.format_time(segment['end'])
                text = segment['text']
                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def create_ass_from_segments(self, segments, ass_path):
        cfg = self.style_config

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")

            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, "
                    "Alignment, MarginL, MarginR, MarginV, Outline, Shadow\n")
            f.write(f"Style: Default,{cfg.font},{cfg.font_size},{cfg.primary_color},{cfg.outline_color},"
                    f"-1,0,{cfg.alignment},30,30,{cfg.margin_v},{cfg.outline_width},{cfg.shadow}\n\n")

            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

            for seg in segments:
                word_objs = seg.get("words", [])  # ✅ echte Wortobjekte

                if not word_objs:
                    continue  # falls keine Wörter enthalten sind

                for i in range(0, len(word_objs), cfg.words_per_line):
                    chunk = word_objs[i:i + cfg.words_per_line]

                    # Echten Text extrahieren
                    chunk_text_raw = "".join([w["word"] for w in chunk]).strip()

                    # Mit Formatierung
                    chunk_text = f"{{\\fsp{cfg.letter_spacing}}}{{\\ws{cfg.word_spacing}}}{chunk_text_raw}"

                    # Echte Zeitpunkte für Start und Ende
                    chunk_start = chunk[0]["start"]
                    chunk_end = chunk[-1]["end"]

                    start = self.format_ass_time(chunk_start)
                    end = self.format_ass_time(chunk_end)

                    # Effekt (Bounce)
                    bounce = r"\t(0,100,\fscx120\fscy120)\t(100,200,\fscx100\fscy100)"
                    effect_str = "{" + bounce + "}"

                    # Zeile schreiben
                    f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{effect_str}{chunk_text}\n")

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

    def format_ass_time(self, seconds):
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        cs = int((s - int(s)) * 100)
        return f"{int(h)}:{int(m):02}:{int(s):02}.{cs:02}"

    def generate_subtitles(self, audio_filename):
        audio_path = os.path.join(self.input_folder, audio_filename)

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"{audio_filename} wurde nicht gefunden!")

        segments = self.transcribe_with_timestamps(audio_path)

        base_name = os.path.splitext(audio_filename)[0]
        srt_path = os.path.join(self.output_folder, base_name + ".srt")
        ass_path = os.path.join(self.output_folder, base_name + ".ass")

        self.create_srt_from_segments(segments, srt_path)
        self.create_ass_from_segments(segments, ass_path)

        print(f"[INFO] SRT und ASS Untertitel für {base_name} wurden erstellt.")
