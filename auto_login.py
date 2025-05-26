from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dotenv import load_dotenv
from pathlib import Path
from typing import Tuple
import os
import time

# Pfade zum Browser und Chromedriver
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
CHROMEDRIVER_PATH = r"D:\Informatik\Projekte\Python_Auto_login\chromedriver-win64\chromedriver.exe"
ENV_PATH = Path("D:/Informatik/Projekte/Python_Auto_login/Logindata.env")

def load_credentials(env_path: Path) -> Tuple[str, str]:
    """
    Lädt die GitHub-Anmeldedaten aus einer .env Datei.

    Args:
        env_path (Path): Pfad zur .env Datei mit Umgebungsvariablen.

    Returns:
        Tuple[str, str]: Ein Tuple mit (USERNAME, PASSWORD).

    Raises:
        ValueError: Wenn Benutzername oder Passwort in der .env Datei fehlen.
    """
    # .env Datei laden, um Umgebungsvariablen verfügbar zu machen
    load_dotenv(env_path)

    # Umgebungsvariablen auslesen
    USERNAME = os.getenv("GITHUB_USER")
    PASSWORD = os.getenv("GITHUB_PASS")

    # Sicherstellen, dass beide Werte gesetzt sind
    if not USERNAME or not PASSWORD:
        raise ValueError("Benutzername oder Passwort fehlen in der .env Datei")

    return USERNAME, PASSWORD

def init_driver(brave_path: str, chromedriver_path: str) -> webdriver.Chrome:
    """
    Initialisiert den Chrome WebDriver mit dem Brave Browser als ausführbarem Binary.

    Args:
        brave_path (str): Pfad zur Brave Browser ausführbaren Datei.
        chromedriver_path (str): Pfad zum Chromedriver.

    Returns:
        webdriver.Chrome: Initialisiertes WebDriver-Objekt.
    """
    # Chrome Optionen setzen und Brave als Browser binary angeben
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path

    # WebDriver Service mit dem Pfad zum Chromedriver starten
    service = Service(chromedriver_path)

    # WebDriver mit Optionen und Service initialisieren und zurückgeben
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def perform_login(driver: webdriver.Chrome, username: str, password: str) -> bool:
    """
    Führt den Login bei GitHub mit den übergebenen Zugangsdaten aus.

    Args:
        driver (webdriver.Chrome): Instanz des WebDrivers.
        username (str): GitHub Benutzername.
        password (str): GitHub Passwort.

    Returns:
        bool: True bei erfolgreichem Login, False sonst.
    """
    # GitHub Login-Seite öffnen
    driver.get("https://github.com/login")

    # WebDriverWait für max. 15 Sekunden einstellen
    wait = WebDriverWait(driver, 15)

    # Eingabefelder für Benutzername und Passwort finden und Werte eingeben
    wait.until(EC.presence_of_element_located((By.ID, "login_field"))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)

    # Login Button anklicken (Submit)
    wait.until(EC.element_to_be_clickable((By.NAME, "commit"))).click()

    # Überprüfen, ob Login erfolgreich war, indem auf das Profil-Menü gewartet wird
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[aria-label="Open global navigation menu"]')
        ))
        print("✅ Login erfolgreich!")
        return True
    except TimeoutException:
        # Wenn Timeout, Screenshot speichern und Login als fehlgeschlagen melden
        print("❌ Login fehlgeschlagen oder blockiert.")
        driver.save_screenshot("login_status.png")
        print("🖼️ Screenshot gespeichert als: login_status.png")
        return False

def main():
    """
    Hauptfunktion, die das Skript steuert.
    Lädt Credentials, startet Browser, loggt ein, wartet bis Browser geschlossen wird.
    """
    driver = None  # driver vor dem try initialisieren
    
    try:
        USERNAME, PASSWORD = load_credentials(ENV_PATH)
        driver = init_driver(BRAVE_PATH, CHROMEDRIVER_PATH)
        login_success = perform_login(driver, USERNAME, PASSWORD)

        print("Browser ist geöffnet. Bitte schließe den Browser manuell, um das Skript zu beenden.")

        while True:
            try:
                _ = driver.title  # Wenn Browser offen, funktioniert dieser Aufruf
                time.sleep(2)
            except WebDriverException:
                # Browser wurde geschlossen oder Verbindung verloren
                print("Browser wurde geschlossen. Skript wird beendet.")
                break

    except KeyboardInterrupt:
        print("\nSkript manuell mit STRG+C beendet.")
    except Exception as e:
        print(f"Es ist ein Fehler aufgetreten: {e}")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()
