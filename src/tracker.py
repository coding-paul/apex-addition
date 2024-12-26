import time
from PIL import ImageGrab
import pytesseract
from PIL import Image
import threading

# Stelle sicher, dass der Tesseract-Pfad korrekt ist
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Finwa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Definiere den Bereich (x1, y1, x2, y2)
bbox1 = (1550, 1030, 1675, 1060)
bbox2 = (1715, 1030, 1815, 1060)

current_weapon: str = ""

weapon1_text = ""
weapon2_text = ""

def live_text_tracking():
    global weapon1_text, weapon2_text
    try:
        while True:
            # Screenshot des definierten Bereichs
            screenshot1 = ImageGrab.grab(bbox1)
            screenshot2 = ImageGrab.grab(bbox2)

            # Text aus dem Screenshot extrahieren
            weapon1_text = pytesseract.image_to_string(screenshot1).strip()
            weapon2_text = pytesseract.image_to_string(screenshot2).strip()
            
            # Zeitintervall, um Ressourcen zu schonen
            time.sleep(0.5)
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
    global current_weapon
    try:
        while True:
            for (x, y), target_color in coordinates_and_colors_weapon1:
                # Get the color at the specified position
                color = get_color_at_position(x, y)
                
                # Check if the color matches the target color
                if color == target_color:
                    print(f"Weapon 1 ({weapon1_text})")
                    current_weapon = weapon1_text
                    break
            
            for (x, y), target_color in coordinates_and_colors_weapon2:
                # Get the color at the specified position
                color = get_color_at_position(x, y)
                
                # Check if the color matches the target color
                if color == target_color:
                    print(f"Weapon 2 ({weapon2_text})")
                    current_weapon = weapon2_text
                    break
            
            # Time interval to save resources
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Color checking stopped.")

# Create threads for both functions
thread1 = threading.Thread(target=live_text_tracking)
thread2 = threading.Thread(target=color_checking)

# Start the threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()