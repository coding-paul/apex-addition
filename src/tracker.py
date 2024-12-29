import time
import os
import json
import mss
from PIL import Image
import pytesseract
import threading
import utils

# Definiere den Bereich (x1, y1, x2, y2)
BBOX1 = (1550, 1030, 1675, 1060)
BBOX2 = (1715, 1030, 1815, 1060)
DELAY = 1 # Zeitintervall, um Ressourcen zu schonen in Sekunden
PATTERN_FILE = "recoil_patterns.json"

logger = utils.create_logger("tracker.py")
weapon_lock: threading.Lock = None
tracker_stop_event: threading.Event = threading.Event()
available_weapons: list[str] = None
current_weapon: str = None
weapon1_text: str = None
weapon2_text: str = None

def get_absolute_path(path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, path)
  return abs_file_path

def update_weapon(new_weapon: str, slot: int): # Only gets called when a new weapon is detected which is not None or an empty string
    global current_weapon

    # Exeptions where the weapon is sometimes not detected correctly for example R301 -> R-301
    # Could also implement multiple languages here
    match(new_weapon):
        case "R301":
            new_weapon = "R-301"

    for weapon in available_weapons:
        if weapon.lower() in new_weapon.lower():
            logger.info(f"Found valid Weapon({slot}): {weapon}", color="GREEN")
            with weapon_lock:
                current_weapon = weapon
            return
    logger.warn(f"Tracker did not find valid weapon: {new_weapon} ?")

def get_current_weapon() -> str:
    with weapon_lock:
        return current_weapon

def live_text_tracking():
    global weapon1_text, weapon2_text
    while True:
        if tracker_stop_event.is_set():
            logger.info("Text checking stopped.")
            return
        
        # Capture the screenshots using mss
        with mss.mss() as sct:
            screenshot1 = sct.grab(BBOX1)
            screenshot2 = sct.grab(BBOX2)

        # Convert mss screenshot to PIL Image
        img1: Image = Image.frombytes("RGB", screenshot1.size, screenshot1.bgra, "raw", "BGRX")
        img2: Image = Image.frombytes("RGB", screenshot2.size, screenshot2.bgra, "raw", "BGRX")

        # Extract text from the screenshots using pytesseract
        weapon1_text = pytesseract.image_to_string(img1).strip()
        weapon2_text = pytesseract.image_to_string(img2).strip()

        # Save screenshots
        # timestamp = int(time.time())
        # screenshot1.save(utils.get_absolute_path(f'images/screenshot1_{timestamp}.png'))
        # screenshot2.save(utils.get_absolute_path(f'images/screenshot2_{timestamp}.png'))
        
        # Zeitintervall, um Ressourcen zu schonen
        time.sleep(DELAY)        

# Define the coordinates and the target colors for the first weapon
coordinates_and_colors_weapon1 = [
    ((1678, 1038), (90, 110, 40)),   # Energie (an) 
    ((1678, 1038), (125, 84, 45)),   # Leichte (an)
    ((1678, 1038), (56, 107, 89)),   # Schwere (an)
    ((1678, 1038), (107, 32, 7)),    # Schrot (an)
    ((1678, 1038), (75, 64, 143)),   # Sniper (an)
    ((1678, 1038), (178, 1, 55)),    # ROT (an)
]

# Define the coordinates and the target colors for the second weapon
coordinates_and_colors_weapon2 = [
    ((1820, 1038), (90, 110, 40)),   # Energie (an) 
    ((1820, 1038), (125, 84, 45)),   # Leichte (an)
    ((1820, 1038), (56, 107, 89)),   # Schwere (an)
    ((1820, 1038), (107, 32, 7)),    # Schrot (an)
    ((1820, 1038), (75, 64, 143)),   # Sniper (an)
    ((1820, 1038), (178, 1, 55)),    # ROT (an)
]

def get_color_at_position(x, y):
    with mss.mss() as sct:
        # Define a bounding box that captures only the single pixel at (x, y)
        bbox = [y, x, y+1, x+1]
        screenshot = sct.grab(bbox)
        color = screenshot.pixel(0, 0)  # Get the color of the single pixel
        return color

def color_checking():
    while True:
        if tracker_stop_event.is_set():
            logger.info("Color checking stopped.")
            return

        for (x, y), target_color in coordinates_and_colors_weapon1:
            # Get the color at the specified position
            color = get_color_at_position(x, y)
            
            # Check if the color matches the target color
            if color == target_color and weapon1_text != "" and weapon1_text is not None:
                update_weapon(weapon1_text, 1)
                break
        else:
            for (x, y), target_color in coordinates_and_colors_weapon2:
                # Get the color at the specified position
                color = get_color_at_position(x, y)
                
                # Check if the color matches the target color
                if color == target_color and weapon2_text != "" and weapon2_text is not None:
                    update_weapon(weapon2_text, 2)
                    break
            else:
                logger.warn("No weapon detected")
        # Time interval to save resources
        time.sleep(DELAY)
    

def main():
    global weapon_lock, available_weapons

    path = utils.get_absolute_path(PATTERN_FILE)
    with open(path, 'r') as file:
        data: dict = json.load(file)
        available_weapons = data["weapons"]

    # Stelle sicher, dass der Tesseract-Pfad korrekt ist
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\paul\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

    # Create threads for both functions
    thread1 = threading.Thread(target=live_text_tracking)
    thread2 = threading.Thread(target=color_checking)

    # Start the threads
    thread1.start()
    thread2.start()

    # Create a lock for the current_weapon variable
    weapon_lock = threading.Lock()

    logger.info("Tracker running...\n", color="CYAN")

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    logger.error("\n\n!!!NOT RUNNING MAIN APPLICATION!!!\n")
    main()
