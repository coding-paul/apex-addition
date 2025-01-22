import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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
        self.root.geometry(self.SETTINGS["MAIN_UI_SIZE"]["value"])
        self.root.resizable(False, False)

        self.log_frame: ttk.Frame = None
        self.logging_window: tk.Toplevel = None
        self.weapon1_label: ttk.Label = None
        self.weapon2_label: ttk.Label = None

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
            self.setup_weapon_ui()
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
            self.weapon_window.destroy()
            print("\nStopping application...\n")
            if not exit:
                messagebox.showinfo("Info", "Application stopped")
        else:
            if not exit:
                messagebox.showwarning("Warning", "Application is not running")

    def setup_logging_ui(self):
        logging_window = tk.Toplevel(self.root)
        logging_window.title("LOG")
        logging_window.geometry(self.SETTINGS["LOGGING_UI_SIZE"]["value"])
        logging_window.resizable(False, False)

        main_ui_size: str = self.SETTINGS["MAIN_UI_SIZE"]["value"]
        main_ui_horizontal_size = int(main_ui_size.split("x")[0])
        weapon_ui_size: str = self.SETTINGS["WEAPON_UI_SIZE"]["value"]
        weapon_ui_horizontal_size = int(weapon_ui_size.split("x")[0])
        horizontal_size = main_ui_horizontal_size + weapon_ui_horizontal_size
        self.__move_window_to_screen_nr(logging_window, self.SETTINGS["UI_MONITOR"]["value"], (horizontal_size+10, 0))

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
            if canvas.winfo_exists:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        self.logging_window = logging_window
        self.log_frame = canvas_frame
    
    def get_log_frame(self):
        return self.log_frame
    
    def setup_weapon_ui(self):
        weapon_window = tk.Toplevel(self.root)
        weapon_window.title("Weapons:")
        weapon_window.geometry(self.SETTINGS["WEAPON_UI_SIZE"]["value"])
        weapon_window.resizable(False, False)

        main_ui_size: str = self.SETTINGS["MAIN_UI_SIZE"]["value"]
        main_ui_horizontal_size = int(main_ui_size.split("x")[0])
        self.__move_window_to_screen_nr(weapon_window, self.SETTINGS["UI_MONITOR"]["value"], (main_ui_horizontal_size+5, 0))

        ttk.Label(weapon_window, text="Your weapons", wraplength=350).pack(pady=(10, 20))
        self.weapon1_label = ttk.Label(weapon_window, text="Weapon 1:\nNone", wraplength=350, anchor="center")
        self.weapon1_label.pack(pady=(10, 20))
        self.weapon2_label = ttk.Label(weapon_window, text="Weapon 2:\nNone", wraplength=350, anchor="center")
        self.weapon2_label.pack(pady=(10, 20))
        self.weapon_window = weapon_window

    def set_weapon(self, weapon_name: str, number: int, selected_weapon_color="green"):
        # Check if both Labels have been initialized
        if not (isinstance(self.weapon1_label, ttk.Label) and isinstance(self.weapon2_label, ttk.Label)):
            return
        # Check if both Labels are existing (Not window closed)
        if not (self.weapon1_label.winfo_exists() and self.weapon2_label.winfo_exists()):
            return
        if number == 1:
            self.weapon1_label.config(text="Weapon 1:\n" + weapon_name, foreground=selected_weapon_color)
            self.weapon2_label.config(foreground="black")
        elif number == 2:
            self.weapon2_label.config(text="Weapon 1:\n" + weapon_name, foreground=selected_weapon_color)
            self.weapon1_label.config(foreground="black")

    def change_settings(self):
        if self.process is not None:
            messagebox.showwarning("Warning", "Can't change settings when the program is running")
            return

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Change Settings")
        settings_window.geometry(self.SETTINGS["SETTINGS_UI_SIZE"]["value"])
        settings_window.resizable(False, False)

        window_size: str = self.SETTINGS["MAIN_UI_SIZE"]["value"]
        vertical_size = int(window_size.split("x")[1])
        self.__move_window_to_screen_nr(settings_window, self.SETTINGS["UI_MONITOR"]["value"], (0, vertical_size+50))

        # Create a Canvas and a scrollbar
        canvas = tk.Canvas(settings_window)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the widgets
        canvas_frame = ttk.Frame(canvas)

        ttk.Label(canvas_frame, text="Here you can change your settings. Be careful to enter valid values. Press save settings at the bottom to save it", wraplength=350).pack(pady=(10, 20))

        inputs: dict[ttk.Entry] = {}
        for key, setting in self.SETTINGS.items():
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
            
            result = self.SETTINGS
            input_field: ttk.Entry
            for key, input_field in inputs.items():
                new_value = input_field.get()
                result[key]["value"] = new_value
            
            result = utils.configure_types(result)

            if isinstance(result, tuple) and result[0] == None: # This means it failed
                messagebox.showerror("Error", f"Invalid data type for: '{result[1]}', expected {result[2]}")
                return

            utils.write_settings(self.SETTINGS)
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
            if canvas.winfo_exists:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
