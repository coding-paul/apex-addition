import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import ast
import threading
from ctypes import windll
from pynput import keyboard

from recoil_handler import main as start_recoil_handler
import utils


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Apex Addition UI")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Directly scales to the screens resolution
        windll.shcore.SetProcessDpiAwareness(1)

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=6)
        self.style.configure("TLabel", font=("Helvetica", 12))

        # Main Frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(expand=True)

        # Title Label
        ttk.Label(self.main_frame, text="Apex Addition UI", font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

        # Buttons
        self.start_button = ttk.Button(self.main_frame, text="Start Application", command=self.start_application)
        self.start_button.pack(fill="x", pady=5)

        self.stop_button = ttk.Button(self.main_frame, text="Stop Application", command=self.stop_application)
        self.stop_button.pack(fill="x", pady=5)

        self.settings_button = ttk.Button(self.main_frame, text="Change Settings", command=self.change_settings)
        self.settings_button.pack(fill="x", pady=5)

        # Load settings and keyboard listener
        self.SETTINGS = utils.get_settings()
        self.keyboard_controller = keyboard.Controller()
        self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_click)
        self.keyboard_listener.start()

        self.process = None

    def on_keyboard_click(self, key):
        if key == keyboard.KeyCode.from_char(self.SETTINGS["QUIT_KEY"]):
            self.process = None

    def on_close(self):
        self.stop_application(exit=True)
        self.root.destroy()

    def start_application(self):
        if self.process is None:
            self.process = threading.Thread(target=start_recoil_handler, args=(self,))
            self.process.start()
            messagebox.showinfo("Info", "Application started")
        else:
            messagebox.showwarning("Warning", "Application is already running")

    def stop_application(self, exit=False, from_utils=False):
        if not from_utils:
            utils.quit_program(self, exit) # This will do some stuff and then recall this function
            return
        if self.process is not None:
            self.process = None
            print("\nApplication stopped from ui\n")
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
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)

        # Create a Canvas and a scrollbar
        canvas = tk.Canvas(settings_window)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the widgets
        canvas_frame = ttk.Frame(canvas)

        ttk.Label(canvas_frame, text="Here you can change your settings. Be careful to enter valid values.", wraplength=350).pack(pady=(10, 20))

        path = utils.get_absolute_path("../settings/settings.json")
        with open(path, "r") as file:
            settings = json.load(file)

        inputs = {}
        for key, value in settings.items():
            ttk.Label(canvas_frame, text=f"{key}:").pack(anchor="w", padx=10)
            if isinstance(value, dict):
                # Warning label for dictionary settings
                ttk.Label(canvas_frame, text=f"⚠️ Be VERY careful when modifying {key}!\nEditing this incorrectly can cause crashes.", foreground="red", wraplength=350).pack(anchor="w", padx=10, pady=(0, 5))
            input_field = ttk.Entry(canvas_frame)
            input_field.insert(0, value)
            input_field.pack(fill="x", padx=10, pady=5)
            inputs[key] = input_field

        def save_settings():
            if self.process is not None:
                messagebox.showwarning("Warning", "Can't save settings when the program is running")
                return
            for key, input_field in inputs.items():
                type_of_setting = type(settings[key])
                new_value = input_field.get()
                try:
                    if type_of_setting == str:
                        pass
                    elif type_of_setting in [float, int]:
                        new_value = float(new_value)
                    elif type_of_setting == dict:
                        new_value = ast.literal_eval(new_value)
                    else:
                        messagebox.showerror(
                            "Error", f"Invalid data type for: '{new_value}', expected {type_of_setting}")
                        return
                except (ValueError, SyntaxError):
                    messagebox.showwarning("Warning", f"Invalid value for: '{key}'")
                    return
                settings[key] = new_value

            with open(path, "w") as file:
                json.dump(settings, file, indent=2)
            self.SETTINGS = utils.get_settings()
            settings_window.destroy()
            messagebox.showinfo("Info", "Settings saved")

        save_button = ttk.Button(canvas_frame, text="Save", command=save_settings)
        save_button.pack(pady=20)

        # Add canvas and scrollbar to the settings window
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a window on the canvas to contain the frame
        canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

        # Update the scrollable region of the canvas
        canvas_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Bind the mouse scroll wheel to scroll the canvas
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
