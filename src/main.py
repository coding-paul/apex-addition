import json
import threading
import time
from pynput import keyboard
from pynput.mouse import Controller, Button

app_running = False

def main():
  print("Test")

mouse = Controller()

def load_pattern():
  with open('pattern.json', 'r') as file:
      return json.load(file)

def move_mouse_pattern():
  pattern = load_pattern()
  for move in pattern:
      if not app_running:
          break
      mouse.move(move['x'], move['y'])
      time.sleep(move['delay'])

def on_click(x, y, button, pressed):
  if app_running and button == Button.left and pressed:
      threading.Thread(target=move_mouse_pattern).start()

mouse_listener = keyboard.Listener(on_click=on_click)
mouse_listener.start()