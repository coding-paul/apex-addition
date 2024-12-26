import json
from threading import Thread, Event
import time
from pynput import keyboard
from pynput.mouse import Controller, Button

mouse = None
stop_event: Event = None

def load_pattern():
    with open('pattern.json', 'r') as file:
        return json.load(file)

def move_mouse_pattern():
  pattern = load_pattern()
  for move in pattern:
      if stop_event.is_set():
          break
      mouse.move(move[1], move[2])
      time.sleep(move[3])

def on_click(x, y, button, pressed):
  if (not stop_event.is_set()) and button == Button.left and pressed:
      Thread(target=move_mouse_pattern).start()

def main(*args):
  global mouse, stop_event

  stop_event = args[0]
  mouse = Controller()

  mouse_listener = keyboard.Listener(on_click=on_click)
  mouse_listener.start()

if __name__ == '__main__':
  main()
