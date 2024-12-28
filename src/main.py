import os
import json
import time
import ctypes
import threading
from pynput import mouse, keyboard
import utils
from tracker import get_current_weapon as tracker_get_current_weapon, main as tracker_thread, tracker_stop_event

DELAY = 0.1 # Time interval to save resources in seconds

QUIT_KEY = "q" # Key to quit the program
PATTERN_FILE = "recoil_patterns.json" # Relative path to the file containing the recoil-patterns
SENSITIVITY = 5 # Sensitivity in your apex settings, 5 is default

m: mouse.Controller = None
stop_event = threading.Event()

def quit():
    print("Exiting...")
    stop_event.set()
    tracker_stop_event.set()
    return False

def get_absolute_path(rel_path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, rel_path)
  return abs_file_path

def load_pattern() -> list:
    print("Loading pattern...")
    weapon_scan: str = tracker_get_current_weapon()  # THIS MUST RETURN THE NAME OF THE WEAPON
    if weapon_scan is None or weapon_scan == "":
        print("No weapon found")
        return None
    path = utils.get_absolute_path(PATTERN_FILE)
    with open(path, 'r') as file:
        data: dict = json.load(file)
        patterns: dict[list] = data["recoil_patterns"]
        for pattern_name in patterns:
            if pattern_name.lower() in weapon_scan.lower():
                print(f"Found pattern for {pattern_name}")
                return patterns[pattern_name]
        print(f"Pattern not found for {weapon_scan}")
        return None

def move_mouse_pattern():
  pattern = load_pattern()
  if type(pattern) is list:
    print(f"Moving mouse via a pattern with a lenght of: {len(pattern)}")
    for move in pattern:
        ctypes.windll.user32.mouse_event(0x0001, int(move[0] * (SENSITIVITY / 5)), int(move[1] * (SENSITIVITY / 5)), 0, 0)
        time.sleep(move[2])
    print("Mouse moved")
  else:
     time.sleep(DELAY)

def on_mouse_click(x, y, button, pressed): # Example arguments: x=1962 y=1792 button=<Button.left:(4, 2, 0)> pressed=False / True when pressed and False when released
  if button == mouse.Button.left and pressed:
      threading.Thread(target=move_mouse_pattern).start()

def on_keyboard_click(key):
  if(key == keyboard.KeyCode.from_char(QUIT_KEY)):
    return quit()

def main():
  print("Main application running...")
  global m
  m = mouse.Controller()

  mouse_listener = mouse.Listener(on_click=on_mouse_click)
  mouse_listener.start()
  keyboard_listener = keyboard.Listener(on_press=on_keyboard_click)
  keyboard_listener.start()
  
  # Start the tracker thread
  tracker_thread_instance = threading.Thread(target=tracker_thread)
  tracker_thread_instance.start()
  
  stop_event.wait()

if __name__ == '__main__':
  main()
