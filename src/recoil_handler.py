import json
import time
import ctypes
import threading
from pynput import mouse, keyboard
import utils
from tracker import get_current_weapon as tracker_get_current_weapon, main as tracker_thread, tracker_stop_event

SETTINGS = utils.get_settings()

m: mouse.Controller = None
is_left_mouse_down: bool = False
is_right_mouse_down: bool = False
logger = utils.create_logger("main.py")
patterns: dict[list] = None
stop_event = threading.Event()

def quit():
    logger.info("Exiting...")
    stop_event.set()
    tracker_stop_event.set()
    return False

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
  pattern, pattern_name = load_pattern()

  # Found a pattern
  if type(pattern) is list:
    logger.info(f"Moving mouse via the pattern: {pattern_name} with a lenght of: {len(pattern)}\n")
    for move in pattern:
        if not is_left_mouse_down or not is_right_mouse_down: # If the left or right mouse button is not pressed anymore, stop the pattern
            return
        ctypes.windll.user32.mouse_event(0x0001, int(move[0] * (SETTINGS["SENSITIVITY"] / 5)), int(move[1] * (SETTINGS["SENSITIVITY"] / 5)), 0, 0)
        time.sleep(move[2])

def on_mouse_click(x, y, button, pressed): # Example arguments: x=1962 y=1792 button=<Button.left:(4, 2, 0)> pressed=False / True when pressed and False when released
  global is_left_mouse_down, is_right_mouse_down
  
  if button == mouse.Button.left and pressed:
      is_left_mouse_down = True
  elif button == mouse.Button.left:
      is_left_mouse_down = False

  if button == mouse.Button.right and pressed:
      is_right_mouse_down = True
  elif button == mouse.Button.right:
      is_right_mouse_down = False

  if is_left_mouse_down and is_right_mouse_down:
     threading.Thread(target=move_mouse_pattern).start()

def on_keyboard_click(key):
  if(key == keyboard.KeyCode.from_char(SETTINGS["QUIT_KEY"])):
    return quit()

def main():
  logger.info("\n\nMain application running...", color="CYAN")
  global m, patterns
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
  tracker_thread_instance = threading.Thread(target=tracker_thread)
  tracker_thread_instance.start()
  
  stop_event.wait()

if __name__ == '__main__':
  main()
