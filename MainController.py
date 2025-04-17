import os
import re
import unicodedata
from PostGrabber import PostGrabber
from WebsiteInteractor import WebsiteInteractor
from SubtitleGenerator import SubtitleGenerator
from VideoProcessor import VideoProcessor
from SubtitleStyleConfig import SubtitleStyleConfig

class MainController:
    def __init__(self):
        # Instanziierung der Komponenten
        self.post_grabber = PostGrabber()
        self.website_interactor = WebsiteInteractor()
        self.subtitle_generator = SubtitleGenerator()
        self.video_processor = VideoProcessor()

    def execute(self):
        print("[INFO] Hole die besten Posts...")
        top_posts = self.post_grabber.grab_posts()
        print("[INFO] Gefundene Posts:", len(top_posts))

        for i, post in enumerate(top_posts, 1):
            print(f"[INFO] Bearbeite Post {i} | r/{post['subreddit']}")

            # Prompt vorbereiten
            prompt = post["title"] + " || " + post["text"]
            self.website_interactor.interact(prompt)
            print(f"[INFO] Audio generation completed.")

            # Extrahiere Dateinamen-sicheren Titel
            prompt_tail = post["title"].strip()
            safe_name = re.sub(r'[\\/*?:"<>|]', '', prompt_tail).replace(" ", "_")
            safe_name = unicodedata.normalize('NFKD', safe_name).encode('ASCII', 'ignore').decode()
            mp3_filename = f"{safe_name}.mp3"

            try:
                self.subtitle_generator.generate_subtitles(mp3_filename)
            except FileNotFoundError:
                print(f"[WARNUNG] Es konnten keine Untertitel für die Datei {mp3_filename} erstellt werden und daher übersprungen.")
                continue

            try:
                print(f"[INFO] Starte Videoerstellung für: {mp3_filename}")
                self.video_processor.generateVideoShort(mp3_filename)
                print(f"[INFO] Video fertig geschnitten")
            except Exception as e:
                print(f"[FEHLER] Bei der Videoerstellung ist ein Fehler aufgetreten: {e}")


        return top_posts

if __name__ == "__main__":
    controller = MainController()
    controller.execute()
