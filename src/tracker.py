import time
import json
import mss
from PIL import Image
import pytesseract
import threading

import utils

SETTINGS = utils.get_settings()
UI = None

# Positions to check the weapon texts for the default resolution (x1, y1, x2, y2)
BBOX1 = (1550, 1030, 1675, 1060)
BBOX2 = (1715, 1030, 1815, 1060)
# Positions to check the weapon colors for the default resolution (x1, y1, x2, y2)
FIRST_WEAPON_PIXEL = (1678, 1038)
SECOND_WEAPON_PIXEL = (1820, 1038)
DEFAULT_RESOLUTION = (1920, 1080) # Define the default resolution of the screen
USER_RESOLUTION = DEFAULT_RESOLUTION # Actual resolution of the screen, this is a default and will get detected automatically
ACTIVE_COLORS = [
    (90, 110, 40),   # Energie (an) 
    (125, 84, 45),   # Leichte (an)
    (56, 107, 89),   # Schwere (an)
    (107, 32, 7),    # Schrot (an)
    (75, 64, 143),   # Sniper (an)
    (178, 1, 55),    # ROT (an)
]

# Debugging
SAVE_SCREENSHOTS = False

logger = utils.create_logger("tracker.py")
weapon_lock: threading.Lock = None
tracker_stop_event: threading.Event = threading.Event()
available_weapons: list[str] = None
current_weapon: str = None
weapon1_text: str = None
weapon2_text: str = None

def update_weapon(new_weapon: str, slot: int): # Only gets called when a new weapon is detected which is not None or an empty string
    global current_weapon

    # Exeptions where the weapon is sometimes not detected correctly for example R301 -> R-301
    # Could also implement multiple languages here
    match(new_weapon):
        case "3030" | "50-30" | "30-50" | "50-50":
            new_weapon = "30-30"
        case "LSTAR":
            new_weapon = "L-STAR"
        case "R301":
            new_weapon = "R-301"
        case "R99":
            new_weapon = "R-99"
        case "R59":
            new_weapon = "R-59"
        case "RE45":
            new_weapon = "RE-45"
        

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

def get_color_at_position(x: int, y: int) -> tuple[int, int, int]:
    with mss.mss() as sct:
        # Define a bounding box that captures only the single pixel at (x, y)
        monitor = sct.monitors[int(SETTINGS["APEX_MONITOR"]["value"])]
        bbox = (monitor["left"] + x, monitor["top"] + y, monitor["left"] + x + 1, monitor["top"] + y + 1)
        screenshot = sct.grab(bbox)
        color = screenshot.pixel(0, 0)  # Get the color of the single pixel
        return color

def live_text_tracking():
    global weapon1_text, weapon2_text
    while not tracker_stop_event.is_set():             
        # Capture the screenshots using mss
        with mss.mss() as sct:
            monitor = sct.monitors[int(SETTINGS["APEX_MONITOR"]["value"])]
            
            x1, y1, x2, y2 = BBOX1
            bbox = (monitor["left"] + x1, monitor["top"] + y1, monitor["left"] + x2, monitor["top"] + y2)
            screenshot1 = sct.grab(bbox)

            x1, y1, x2, y2 = BBOX2
            bbox = (monitor["left"] + x1, monitor["top"] + y1, monitor["left"] + x2, monitor["top"] + y2)
            screenshot2 = sct.grab(BBOX2)

        # Convert mss screenshot to PIL Image
        img1: Image = Image.frombytes("RGB", screenshot1.size, screenshot1.bgra, "raw", "BGRX")
        img2: Image = Image.frombytes("RGB", screenshot2.size, screenshot2.bgra, "raw", "BGRX")

        try:
            # Extract text from the screenshots using pytesseract
            weapon1_text = pytesseract.image_to_string(img1).strip()
            weapon2_text = pytesseract.image_to_string(img2).strip()
        except (FileNotFoundError, pytesseract.TesseractNotFoundError):
            logger.error("\nWrong tesseract path, go into settings and change it accordingly\n")
            utils.quit_program(UI)

        if SAVE_SCREENSHOTS:
            timestamp = int(time.time())
            img1.save(utils.get_absolute_path(f'images/screenshot1_{timestamp}.png'))
            img2.save(utils.get_absolute_path(f'images/screenshot2_{timestamp}.png'))
        
        # Zeitintervall, um Ressourcen zu schonen
        time.sleep(SETTINGS["TRACKER_DELAY"]["value"])      

    logger.info("Text checking stopped.")
    return  

def color_checking():
    while not tracker_stop_event.is_set():
        x, y = FIRST_WEAPON_PIXEL
        color = get_color_at_position(x, y)
        for target_color in ACTIVE_COLORS:
            # Get the color at the specified position
            
            # Check if the color matches the target color
            if color == target_color and weapon1_text != "" and weapon1_text is not None:
                update_weapon(weapon1_text, 1)
                break
        else:
            x, y = SECOND_WEAPON_PIXEL
            color = get_color_at_position(x, y)
            for target_color in ACTIVE_COLORS:
                # Get the color at the specified position
                
                # Check if the color matches the target color
                if color == target_color and weapon2_text != "" and weapon2_text is not None:
                    update_weapon(weapon2_text, 2)
                    break
            else:
                logger.warn("No weapon detected")
        # Time interval to save resources
        time.sleep(SETTINGS["TRACKER_DELAY"]["value"])

    logger.info("Color checking stopped.")
    return
    

def main(ui):
    global UI, weapon_lock, available_weapons, SETTINGS, USER_RESOLUTION
    UI = ui
    SETTINGS = utils.get_settings()
    tracker_stop_event.clear()

    logger.info("Tracker running...\n", color="CYAN")

    if SETTINGS["AUTO-DETECT-RESOLUTION"]["value"]["AUTO-DETECT"]:
        with mss.mss() as sct:
            monitor = sct.monitors[int(SETTINGS["APEX_MONITOR"]["value"])]
            screenshot = sct.grab(monitor)
            USER_RESOLUTION = (screenshot.width, screenshot.height)
    else:
        USER_RESOLUTION = (SETTINGS["AUTO-DETECT-RESOLUTION"]["value"]["WIDTH"], SETTINGS["AUTO-DETECT-RESOLUTION"]["value"]["HEIGHT"])

    logger.info(f"Resolution: {USER_RESOLUTION}")

    if USER_RESOLUTION != DEFAULT_RESOLUTION:
        global BBOX1, BBOX2, FIRST_WEAPON_PIXEL, SECOND_WEAPON_PIXEL
        logger.info("You are playing on an other resolution than the default 1920x1080\nThis Script will automaticly resize to your Resolution.\n")
        BBOX1 = utils.scale_coordinates(BBOX1, DEFAULT_RESOLUTION, USER_RESOLUTION)
        BBOX2 = utils.scale_coordinates(BBOX2, DEFAULT_RESOLUTION, USER_RESOLUTION)
        FIRST_WEAPON_PIXEL = utils.scale_coordinates(FIRST_WEAPON_PIXEL, DEFAULT_RESOLUTION, USER_RESOLUTION)
        SECOND_WEAPON_PIXEL = utils.scale_coordinates(SECOND_WEAPON_PIXEL, DEFAULT_RESOLUTION, USER_RESOLUTION)

    path = utils.get_absolute_path("recoil_patterns.json")
    with open(path, 'r') as file:
        data: dict = json.load(file)
        available_weapons = data["weapons"]

    pytesseract.pytesseract.tesseract_cmd = SETTINGS["TESSERACT_PATH"]["value"]

    # Create threads for both functions
    thread1 = threading.Thread(target=live_text_tracking)
    thread2 = threading.Thread(target=color_checking)

    # Start the threads
    thread1.start()
    thread2.start()

    # Create a lock for the current_weapon variable
    weapon_lock = threading.Lock()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    logger.error("\n\n!!!NOT RUNNING MAIN APPLICATION!!!\n")
    main()
