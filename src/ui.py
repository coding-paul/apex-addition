import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import ast
import mss
import threading
from ctypes import windll

from recoil_handler import main as start_recoil_handler
import utils


class App:
    def __init__(self, root: tk.Tk):
        # Load settings and set variables
        self.SETTINGS = utils.get_settings()
        self.process = None

        self.root = root
        self.root.title("Apex Addition UI")
        self.root.geometry(self.SETTINGS["WINDOW_SIZE"]["value"])
        self.root.resizable(False, False)

        self.log_frame: ttk.Frame = None
        self.logging_window: tk.Toplevel = None

        # Directly scales to the screens resolution
        windll.shcore.SetProcessDpiAwareness(2)

        # Get monitor information
        self.__move_window_to_screen_nr(self.root, self.SETTINGS["UI_MONITOR"]["value"])

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

        self.stop_button = ttk.Button(self.main_frame, text="Exit", command=self.on_close)
        self.stop_button.pack(fill="x", pady=5)

    def __move_window_to_screen_nr(self, object: tk.Tk, monitor_nr: int, extra_px: tuple[int,int]=None):
        monitor_nr = int(monitor_nr)
        monitors = mss.mss().monitors
        if monitor_nr < len(monitors):
            monitor = monitors[monitor_nr]
            x,y = (monitor["left"], monitor["top"])
            if extra_px:
                extra_x, extra_y = extra_px
                x += extra_x
                y += extra_y
            object.geometry(f"+{x}+{y}")
        else:
            print(f"Too high monitor number")
            self.stop_application()

    def on_close(self):
        self.stop_application(exit=True)
        self.root.destroy()

    def start_application(self):
        if self.process is None:
            self.setup_logging_ui()
            self.process = threading.Thread(target=start_recoil_handler, args=(self,))
            self.process.start()
            messagebox.showinfo("Info", "Application started")
        else:
            if not self.logging_window.winfo_exists():
                self.setup_logging_ui()
            messagebox.showwarning("Warning", "Application is already running")

    def stop_application(self, exit=False, from_utils=False):
        if not from_utils:
            utils.quit_program(self, exit) # This will set all stop_events and then recall this function
            return
        if self.process is not None:
            self.process = None
            self.logging_window.destroy()
            print("\nStopping application...\n")
            if not exit:
                messagebox.showinfo("Info", "Application stopped")
        else:
            if not exit:
                messagebox.showwarning("Warning", "Application is not running")

    def setup_logging_ui(self):
        logging_window = tk.Toplevel(self.root)
        logging_window.title("LOG")
        logging_window.geometry("300x500")
        logging_window.resizable(False, False)

        window_size: str = self.SETTINGS["WINDOW_SIZE"]["value"]
        x = int(window_size.split("x")[0])
        self.__move_window_to_screen_nr(logging_window, self.SETTINGS["UI_MONITOR"]["value"], (int(x), 0))

        # Create a Canvas and a scrollbar
        canvas = tk.Canvas(logging_window, width=280)  # Set width to match wraplength
        scrollbar = ttk.Scrollbar(logging_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a frame inside the canvas to hold the widgets
        canvas_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

        # Configure the canvas scroll region after adding widgets
        canvas_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind scrolling to the mouse wheel
        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        self.logging_window = logging_window
        self.log_frame = canvas_frame
    
    def get_log_frame(self):
        return self.log_frame

    def change_settings(self):
        if self.process is not None:
            messagebox.showwarning("Warning", "Can't change settings when the program is running")
            return

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Change Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        self.__move_window_to_screen_nr(settings_window, self.SETTINGS["UI_MONITOR"]["value"])

        # Create a Canvas and a scrollbar
        canvas = tk.Canvas(settings_window)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the widgets
        canvas_frame = ttk.Frame(canvas)

        ttk.Label(canvas_frame, text="Here you can change your settings. Be careful to enter valid values. Press save settings at the bottom to save it", wraplength=350).pack(pady=(10, 20))

        path = utils.get_absolute_path("../settings/settings.json")
        with open(path, "r") as file:
            settings = json.load(file)

        inputs: dict[ttk.Entry] = {}
        for key, setting in settings.items():
            ttk.Label(canvas_frame, text=f"{key}:").pack(anchor="w", padx=10)
            if isinstance(setting["value"], dict):
                # Warning label for dictionary settings
                ttk.Label(canvas_frame, text=f"⚠️ Be VERY careful when modifying {key}!\nEditing this incorrectly can cause crashes.", foreground="red", wraplength=350).pack(anchor="w", padx=10, pady=(0, 5))
            input_field = ttk.Entry(canvas_frame)
            input_field.insert(0, str(setting["value"]))
            input_field.pack(fill="x", padx=10, pady=5)
            inputs[key] = input_field

        def save_settings():
            if self.process is not None:
                messagebox.showwarning("Warning", "Can't save settings when the program is running")
                return
            for key, input_field in inputs.items():
                type_of_setting = type(settings[key]["value"])
                new_value = input_field.get()
                try:
                    if type_of_setting == str:
                        new_value = str(new_value)
                    elif type_of_setting in [float, int]:
                        new_value = float(new_value)
                    elif type_of_setting == dict:
                        new_value = ast.literal_eval(new_value)
                    elif type_of_setting == bool:
                        if not (new_value == 'True' or new_value == 'False'):
                            messagebox.showerror("Warning", f"{key} can only be 'True' or 'False'")
                            return
                        new_value = new_value == "True"
                    else:
                        messagebox.showerror(
                            "Error", f"Invalid data type for: '{new_value}', expected {type_of_setting}")
                        return
                except (ValueError, SyntaxError):
                    messagebox.showwarning("Warning", f"Invalid value for: '{key}'")
                    return
                settings[key]["value"] = new_value

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
