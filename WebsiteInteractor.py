from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import subprocess
import re
import os
import time
import unicodedata

class WebsiteInteractor:
    def __init__(self):
        # Basisverzeichnis des Projekts
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(base_dir, "temp")
        self.download_path = os.path.join(self.temp_dir, "Generated Audio")

        # Firefox bleibt wie gehabt (externer Pfad)
        self.firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

    def interact(self, prompt):
        FIREFOX_PATH = self.firefox_path
        DOWNLOAD_PATH = self.download_path

        # Funktion zur Extraktion der Firefox-Version
        def get_firefox_version():
            output = subprocess.check_output(
                f'"{FIREFOX_PATH}" --version', shell=True
            )

            try:
                version_string = output.decode('cp1252').strip()
            except UnicodeDecodeError:
                version_string = output.decode('utf-8', errors='replace').strip()

            match = re.search(r'\d+\.\d+\.\d+', version_string)
            if match:
                return match.group(0)
            else:
                raise RuntimeError(f"Firefox-Version konnte nicht extrahiert werden. Output war: '{version_string}'")

        # Firefox-Version extrahieren
        firefox_version = get_firefox_version()
        print(f"[INFO] Firefox Version: {firefox_version}")

        # Firefox Profil konfigurieren
        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg")  # Stelle sicher, dass der MIME-Typ korrekt ist
        profile.set_preference("browser.download.useDownloadDir", True)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("pdfjs.disabled", True)
        profile.set_preference("browser.download.panel.shown", False)

        # Selenium Options setzen
        options = Options()
        options.binary_location = FIREFOX_PATH
        options.profile = profile  # Profil explizit setzen

        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )

        # Website öffnen
        driver.get("https://www.openai.fm/")

        # Warten, bis die Seite geladen ist
        driver.implicitly_wait(10)

        # Prompt in Textfeld 1 einfügen
        try:
            textfeld1 = driver.find_element(By.CSS_SELECTOR, 'textarea#prompt')
            textfeld1.clear()
            textfeld1.send_keys(prompt)
            print("[INFO] Prompt in Textfeld 1 eingefügt.")
        except Exception as e:
            print(f"[ERROR] Textfeld 1: {e}")

        # Persönlichkeitsbeschreibung in Textfeld 2 einfügen
        personality_description = """
            Personality/Affect:
            An energetic, super-charged motivator who’s ready to lift you up and make every moment feel like a celebration! Imagine a friend who’s always ready to hype you up and keep the good vibes flowing, no matter what task you're tackling.
            
            Voice:
            High-energy, bright, and bubbly. This voice radiates excitement and positivity, instantly uplifting the listener. It’s like having a personal cheerleader in your ear, bringing endless enthusiasm and joy to even the most ordinary moments.
            
            Tone:
            Playful, encouraging, and infectious! It makes you feel like every little achievement is a huge win. Whether you’re starting your day or crossing off a to-do list, this voice adds an extra dose of fun and motivation. Every phrase is full of life, pushing you forward with a smile!
            
            Dialect:
            Casual, approachable, and full of pep talk-style expressions. It uses super friendly, informal language that makes you feel like you're chatting with your best friend. Expect lots of "Let’s do this!" and "You’ve totally got this!" to keep the vibe upbeat.
            
            Pronunciation:
            Crisp, sharp, and full of zest! There’s a clear emphasis on positive, exciting words, with playful inflections that make them pop. The rhythm of the voice is bouncy, keeping everything lively and energetic. Every word feels deliberate and filled with energy to keep the listener engaged and smiling.
            
            Features:
            The voice is packed with motivational catchphrases, cheerful exclamations, and an infectious pace that makes every second feel action-packed. It’s all about creating a sense of engagement, making you feel like you’re on an exciting journey together. Expect a lot of "YES!", "You’re crushing it!", "Let’s goooo!", and "So close!" to amp up the excitement!
            """
        try:
            textfeld2 = driver.find_element(By.CSS_SELECTOR, 'textarea#input')
            textfeld2.clear()
            textfeld2.send_keys(personality_description)
            print("[INFO] Persönlichkeitsbeschreibung in Textfeld 2 eingefügt.")
        except Exception as e:
            print(f"[ERROR] Textfeld 2: {e}")

        # Knopf 1: Auswahl der Stimme klicken
        try:
            knopf1 = driver.find_element(By.XPATH, "//span[text()='S']/ancestor::div[contains(@class, 'Button_Button__u2RFO')]")
            knopf1.click()
            print("[INFO] Knopf 1 wurde geklickt.")
        except Exception as e:
            print(f"[ERROR] Knopf 1: {e}")

        # Knopf 2: Download klicken
        try:
            knopf2 = driver.find_element(By.XPATH, "//span[text()='Download']/ancestor::div[contains(@class, 'Button_Button__u2RFO')]")
            knopf2.click()
            print("[INFO] Knopf 2 (Download) wurde geklickt.")
        except Exception as e:
            print(f"[ERROR] Download-Knopf: {e}")

        # Warten, bis der Download abgeschlossen ist
        self.wait_for_download(DOWNLOAD_PATH, prompt)

        driver.quit()

    def wait_for_download(self, download_path, prompt):
        mp3_file = None
        while True:
            files = os.listdir(download_path)
            mp3_files = [f for f in files if f.endswith('.mp3')]
            partial_files = [f for f in files if f.endswith('.part')]

            if mp3_files and not partial_files:
                mp3_file = mp3_files[0]
                full_path = os.path.join(download_path, mp3_file)
                if self.is_file_fully_written(full_path):
                    break

            time.sleep(1)

        # Umbenennen also hole den Titel des posts
        # Extrahiere Teil vor dem "||"
        prompt_tail = prompt.split("||")[0].strip()

        # Ersetze Leerzeichen durch Unterstriche und entferne ungültige Zeichen für Dateinamen
        safe_name = re.sub(r'[\\/*?:"<>|]', '', prompt_tail)
        safe_name = safe_name.replace(" ", "_")
        safe_name = unicodedata.normalize('NFKD', safe_name).encode('ASCII', 'ignore').decode()

        neuer_name = f"{safe_name}.mp3"
        alter_pfad = os.path.join(download_path, mp3_file)
        neuer_pfad = os.path.join(download_path, neuer_name)
        print(f"[TEST] Datei gespeichert unter dem namen " + neuer_name)

        # Datei umbenennen
        os.rename(alter_pfad, neuer_pfad)

    @staticmethod
    def is_file_fully_written(file_path, wait_time=2):
        """Prüft, ob eine Datei sich inhaltlich nicht mehr verändert (z. B. noch beschrieben wird)."""
        try:
            initial_size = os.path.getsize(file_path)
            time.sleep(wait_time)
            new_size = os.path.getsize(file_path)
            return initial_size == new_size
        except FileNotFoundError:
            return False
