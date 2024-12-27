import os
import json
import time
import ctypes
import threading
from pynput import mouse, keyboard
from tracker import get_current_weapon as tracker_get_current_weapon, main as tracker_thread, tracker_stop_event

# Dont create pycache 
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

DELAY = 0.1 # Time interval to save resources in seconds

QUIT_KEY = "q" # Key to quit the program
PATTERN_FILE = "recoil_patterns.json" # Relative path to the file containing the recoil-patterns
SENSITIVITY = 1 # Sensitivity of the mouse movement, 1 is default, 2 is double the movement, 0.5 is half the movement

m: mouse.Controller = None
stop_event = threading.Event()

def quit():
    print("Exiting...")
    stop_event.set()
    tracker_stop_event.set()
    return False

def get_absolute_path(path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, path)
  return abs_file_path

def get_current_weapon() -> str:
   print("Tracking...")  # THIS IS AN EXAMPLE, WILL BE REPLACED WITH ACTUAL CODE
   return tracker_get_current_weapon() 
  #  return "R-99q" 

def load_pattern() -> list:
    weapon_scan: str = get_current_weapon() # THIS MUST RETURN THE NAME OF THE WEAPON
    if weapon_scan is None:
        return None
    path = get_absolute_path(PATTERN_FILE)
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
  print(type(pattern))
  print(type(pattern) is list)
  if type(pattern) is list:
    for move in pattern:
        print("Moving mouse")
        ctypes.windll.user32.mouse_event(0x0001, int(move[0] * SENSITIVITY), int(move[1] * SENSITIVITY), 0, 0)
        time.sleep(move[2])
  else:
     time.sleep(DELAY)

def on_mouse_click(x, y, button, pressed): # Example arguments: x=1962 y=1792 button=<Button.left:(4, 2, 0)> pressed=False / True when pressed and False when released
  if button == mouse.Button.left and pressed:
      threading.Thread(target=move_mouse_pattern).start()

def on_keyboard_click(key):
  if(key == keyboard.KeyCode.from_char(QUIT_KEY)):
    return quit()

def main():
  print("Running")
  global m
  m = mouse.Controller()

  mouse.Listener(on_click=on_mouse_click).start()
  keyboard.Listener(on_press=on_keyboard_click).start()
  
  # Start the tracker thread
  tracker_thread_instance = threading.Thread(target=tracker_thread)
  tracker_thread_instance.start()
  
  stop_event.wait()

if __name__ == '__main__':
  main()
