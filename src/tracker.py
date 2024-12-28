import time
import os
from PIL import ImageGrab
from PIL import Image
import pytesseract
import threading

# Definiere den Bereich (x1, y1, x2, y2)
bbox1 = (1550, 1030, 1675, 1060)
bbox2 = (1715, 1030, 1815, 1060)

DELAY = 1 # Zeitintervall, um Ressourcen zu schonen in Sekunden

weapon_lock: threading.Lock = None
tracker_stop_event: threading.Event = threading.Event()

current_weapon: str = None
weapon1_text: str = None
weapon2_text: str = None

def main():
    global weapon_lock

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

    print("Tracker running...")

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

def get_absolute_path(path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, path)
  return abs_file_path

def update_weapon(new_weapon: str):
    global current_weapon
    with weapon_lock:
        current_weapon = new_weapon

def get_current_weapon() -> str:
    with weapon_lock:
        return current_weapon

def live_text_tracking():
    global weapon1_text, weapon2_text
    try:
        while True:
            if tracker_stop_event.is_set():
                return
            # Screenshot des definierten Bereichs
            screenshot1 = ImageGrab.grab(bbox1)
            screenshot2 = ImageGrab.grab(bbox2)

            # Text aus dem Screenshot extrahieren
            weapon1_text = pytesseract.image_to_string(screenshot1).strip()
            weapon2_text = pytesseract.image_to_string(screenshot2).strip()
            
            # Zeitintervall, um Ressourcen zu schonen
            time.sleep(DELAY)
    except KeyboardInterrupt:
        print("Live-Tracking beendet.")

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
    screenshot = ImageGrab.grab()
    color = screenshot.getpixel((x, y))
    return color

def color_checking():
    try:
        while True:
            if tracker_stop_event.is_set():
                return
            sucessfull = False
            for (x, y), target_color in coordinates_and_colors_weapon1:
                # Get the color at the specified position
                color = get_color_at_position(x, y)
                
                # Check if the color matches the target color
                if color == target_color:
                    print(f"Weapon 1 ({weapon1_text})")
                    update_weapon(weapon1_text)
                    sucessfull = True
                    break
            
            for (x, y), target_color in coordinates_and_colors_weapon2:
                # Get the color at the specified position
                color = get_color_at_position(x, y)
                
                # Check if the color matches the target color
                if color == target_color:
                    print(f"Weapon 2 ({weapon2_text})")
                    update_weapon(weapon2_text)
                    sucessfull = True
                    break

            if not sucessfull:
                print("No weapon detected")
            
            # Time interval to save resources
            time.sleep(DELAY)
    except KeyboardInterrupt:
        print("Color checking stopped.")

if __name__ == "__main__":
    main()
