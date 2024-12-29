import tkinter as tk
from tkinter import messagebox
import json
import ast
import subprocess
import utils
from pynput import keyboard

class App:
  def __init__(self, root):

    self.root = root
    self.root.title("Apex Addition UI")

    self.start_button = tk.Button(root, text="Start Application", command=self.start_application)
    self.start_button.pack(pady=10)

    self.stop_button = tk.Button(root, text="Stop Application", command=self.stop_application)
    self.stop_button.pack(pady=10)

    self.settings_button = tk.Button(root, text="Change Settings", command=self.change_settings)
    self.settings_button.pack(pady=10)

    self.SETTINGS = utils.get_settings()

    self.keyboard_controller = keyboard.Controller()
    self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_click)
    self.keyboard_listener.start()

    self.process = None

  def on_keyboard_click(self, key):
    if(key == keyboard.KeyCode.from_char(self.SETTINGS["QUIT_KEY"])):
      self.process = None

  def on_close(self):
    self.stop_application(exit=True)
    root.destroy()

  def start_application(self):
    if self.process is None:
      path = utils.get_absolute_path("main.py")
      venv_python = utils.get_absolute_path("../.venv/Scripts/python.exe")
      self.process = subprocess.Popen([venv_python, path])
      messagebox.showinfo("Info", "Application started")
    else:
      messagebox.showwarning("Warning", "Application is already running")

  def stop_application(self, exit=False):
    if self.process is not None:
      self.keyboard_controller.press(self.SETTINGS["QUIT_KEY"])
      self.process = None
      if not exit:
        messagebox.showinfo("Info", "Application stopped")
    else:
      if not exit:
        messagebox.showwarning("Warning", "Application is not running")

  def change_settings(self):
    if self.process is not None:
      messagebox.showwarning("Warning", "Can't change settings when the program is running")
      return
    settings_window = tk.Toplevel(self.root)
    settings_window.title("Change Settings")
    tk.Label(settings_window, text="Here you can change your settings, but dont wonder why you can't exit the program if you enter an unvalid exit key..").pack()

    path = utils.get_absolute_path("../settings/settings.json")
    with open(path, "r") as file:
      settings: dict = json.load(file)

    inputs = {}
    for key, value in settings.items():
      if type(value) == dict:
        tk.Label(settings_window, text=key).pack(pady=(20, 0))
        tk.Label(settings_window, text=f"Be VERY careful when modifying {key}!\nRemoving or adding a new property can cause crashes and function loss of this program\nOnly edit if you really know what you are doing").pack()
      else:
        tk.Label(settings_window, text=key).pack()
      input = tk.Entry(settings_window)
      input.insert(0, value)
      input.pack()
      inputs[key] = input

    def save_settings():
      for key, input in inputs.items():
        type_of_setting = type(settings[key])
        new_value = input.get()
        # Put the setting into the right data format
        try:
          if type_of_setting == str:
              pass
          elif type_of_setting == float or type_of_setting == int:
            new_value = float(new_value)
          elif type_of_setting == dict:
            new_value = ast.literal_eval(new_value)
          else:
            messagebox.showerror("Error", f"Found no valid data type for: '{new_value}' target type: {type_of_setting}")
            return
        except ValueError:
          messagebox.showwarning("Warning", f"Wrong data type for: '{new_value}' is not a {type_of_setting}")
          return
        except SyntaxError:
          messagebox.showwarning("Warning", "Wrong JSON-Syntax")
          return
        except:
          messagebox.showerror("Error", f"Something went wrong trying to turn: '{new_value}' into target type: {type_of_setting}")
          return
        settings[key] = new_value

      # Successfull
      path = utils.get_absolute_path("../settings/settings.json")
      with open(path, "w") as file:
        json.dump(settings, file, indent=2)
      self.SETTINGS = utils.get_settings()
      settings_window.destroy()
      messagebox.showinfo("Info", "Settings saved")

    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)

if __name__ == "__main__":
  root = tk.Tk()
  app = App(root)
  root.protocol("WM_DELETE_WINDOW", app.on_close)
  root.mainloop()