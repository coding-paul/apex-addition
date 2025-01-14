import json
import time
import ctypes
import threading
from pynput import mouse, keyboard

import utils
from tracker import get_current_weapon as tracker_get_current_weapon, main as tracker_thread, tracker_stop_event

SETTINGS = utils.get_settings()
UI = None

m: mouse.Controller = None
is_left_mouse_down: bool = False
is_right_mouse_down: bool = False
moving_pattern: bool = False
logger = utils.create_logger("main.py")
patterns: dict[list] = None
stop_event = threading.Event()

def load_pattern() -> tuple[list, str]:
    logger.info("\nLoading pattern...")
    weapon_scan: str = tracker_get_current_weapon()  # Is None from beginning but is a valid name of a weapon in the recoil_patterns.json file once a weapon is detected

    # No weapon detected yet
    if(weapon_scan is None):
        logger.warn("Not any weapon detected yet\n")
        return (None, None)
    # Valid weapon detected
    for pattern_name in patterns:
        if weapon_scan == pattern_name:
            return (patterns[pattern_name], pattern_name)
    # Weapon not found -> Should not happen
    logger.error(f"\nPattern not found for '{weapon_scan}' this is a bug and SHOULD NOT happen\n")
    return (None, None)

def move_mouse_pattern():
    global moving_pattern
    pattern, pattern_name = load_pattern()
    moving_pattern = True
    # Found a pattern
    if type(pattern) is list:
        logger.info(f"Moving mouse via the pattern: {pattern_name} with a lenght of: {len(pattern)}\n")
        for move in pattern:
            if SETTINGS["HOLD_RIGHT"]["value"]:
                if not is_left_mouse_down or not is_right_mouse_down: # If the left or right mouse button is not pressed anymore, stop the pattern
                    moving_pattern = False
                    return
            else:
                if not is_left_mouse_down: # If the left mouse button is not pressed anymore, stop the pattern
                    moving_pattern = False
                    return
            ctypes.windll.user32.mouse_event(0x0001, int(move[0] * (SETTINGS["SENSITIVITY"]["value"] / 5)), int(move[1] * (SETTINGS["SENSITIVITY"]["value"] / 5)), 0, 0)
            time.sleep(move[2])
    moving_pattern = False

def on_mouse_click(x, y, button, pressed): # Example arguments: x=1962 y=1792 button=<Button.left:(4, 2, 0)> pressed=False / True when pressed and False when released
    global is_left_mouse_down, is_right_mouse_down, moving_pattern
    
    if button == mouse.Button.left and pressed:
        is_left_mouse_down = True
    elif button == mouse.Button.left:
        is_left_mouse_down = False

    if button == mouse.Button.right and pressed:
        is_right_mouse_down = True
    elif button == mouse.Button.right:
        is_right_mouse_down = False

    if SETTINGS["HOLD_RIGHT"]["value"]: 
        if is_left_mouse_down and is_right_mouse_down:
            if not moving_pattern:
                threading.Thread(target=move_mouse_pattern).start()
    else:
        if is_left_mouse_down:
            if not moving_pattern:
                threading.Thread(target=move_mouse_pattern).start()

def on_keyboard_click(key):
    if(key == keyboard.KeyCode.from_char(SETTINGS["QUIT_KEY"]["value"])):
        return utils.quit_program(UI)

def main(ui):
    global UI, m, patterns, SETTINGS
    UI = ui

    SETTINGS = utils.get_settings()
    stop_event.clear()
    logger.info("\n\nMain application running...", color="CYAN")
    m = mouse.Controller()

    path = utils.get_absolute_path("recoil_patterns.json")
    with open(path, 'r') as file:
        data: dict = json.load(file)
        patterns = data["recoil_patterns"]

    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()
    keyboard_listener = keyboard.Listener(on_press=on_keyboard_click)
    keyboard_listener.start()
    
    # Start the tracker thread
    tracker_thread_instance = threading.Thread(target=tracker_thread, args=(UI,))
    tracker_thread_instance.start()
    
    stop_event.wait()
    mouse_listener.stop()
    keyboard_listener.stop()

if __name__ == '__main__':
    main()
