import os
import re
import json
import ctypes
import tkinter as tk
from tkinter import ttk
from typing import Literal
from ast import literal_eval as str_dict

available_colors = Literal["BLUE", "CYAN", "GREEN", "YELLOW", "RED"]
class create_logger():
    def __init__(self, name: str, UI=None):
        self.name = name
        self.ui_logging_active = False
        self.UI = None
        
        if UI:
            self.init_ui_logging(UI)

        self.OKBLUE = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.HEADER = '\033[95m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

        self.ANSI_STYLES = {
        '\033[94m': {'foreground': 'blue'},      # OKBLUE
        '\033[96m': {'foreground': 'cyan'},     # OKCYAN
        '\033[92m': {'foreground': 'green'},    # OKGREEN
        '\033[93m': {'foreground': 'orange'},   # WARNING
        '\033[91m': {'foreground': 'red'},      # FAIL
        '\033[95m': {'foreground': 'purple'},   # HEADER
        '\033[0m': {'foreground': 'black'},     # ENDC (reset)
        '\033[1m': {'font': ('Helvetica', 12, 'bold')},  # BOLD
        '\033[4m': {'font': ('Helvetica', 12, 'underline')}  # UNDERLINE
    }

    def init_ui_logging(self, UI):
        if getattr(UI, "get_log_frame", None) == None:
            self.error(f"Error when initializing ui for logging, {UI} is not a valid ui class")
            return
        self.UI = UI
        self.ui_logging_active = True

    def __parse_ansi_message(self, message: str):
        """
        Parse ANSI escape codes and return a list of text segments with their styles.
        """
        ansi_pattern = re.compile(r'(\033\[\d+m)')  # Match ANSI escape sequences
        parts = ansi_pattern.split(message)  # Split message into text and ANSI codes
        segments = []

        current_style = {}
        for part in parts:
            if part in self.ANSI_STYLES:
                # Update current style based on ANSI code
                current_style.update(self.ANSI_STYLES[part])
            elif part.strip():  # Add text segments with the current style
                segments.append((part, current_style.copy()))

        return segments

    def __log_to_ui(self, message: str):
        ui_logger: ttk.Frame = self.UI.get_log_frame()
        canvas: tk.Canvas = ui_logger.master  # The canvas containing the ui_logger

        # Check if the user is at the bottom
        _, end_fraction = canvas.yview()
        at_bottom = end_fraction >= 1.0  # Check if the scrollbar is at the bottom

        # Parse the ANSI message into styled segments
        segments = self.__parse_ansi_message(message)

        # Add each segment as a separate label with its style
        for text, style in segments:
            ttk.Label(ui_logger, text=text, wraplength=280, **style).pack(anchor="w", padx=10, pady=2)

        ui_logger.update_idletasks()

        # Update the scroll region to include the new content
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Scroll down automatically only if the user was already at the bottom
        if at_bottom:
            canvas.yview_moveto(1.0)  # Move the view to the bottom


    def __log(self, value: str, message_type: str, color: available_colors=None, newline=True):
        # Gettings prefixes
        color_prefix = {
            "BLUE": self.OKBLUE,
            "CYAN": self.OKCYAN,
            "GREEN": self.OKGREEN,
            "YELLOW": self.WARNING,
            "RED": self.FAIL
        }.get(color, "")
        message_prefix = {
            "info": "(I) ",
            "warn": "(W) ",
            "error": "(E) "
        }.get(message_type, "")

        if (type(value) != str):
            print(color_prefix, end="")
            print(value, end="")
            print(self.ENDC, end="\n" if newline else "")
            return

        # Remove newlines and the start and end to put them on later on after adding all other pre- and suffixes
        newline_prefix = ""
        newline_suffix = ""
        while value.startswith("\n"):
            newline_prefix += "\n"
            value = value[1:]  # Remove the first leading newline character
        while value.endswith("\n"):
            newline_suffix += "\n"
            value = value[:-1]  # Remove the first leading newline character

        print_val: str = newline_prefix + color_prefix + value + self.ENDC + newline_suffix

        # Actual print statement
        print(print_val, end="\n" if newline else "")

        try:
            self.__log_to_ui(print_val)
        except tk.TclError:
            self.ui_logging_active = False
            return
        except RuntimeError:
            self.ui_logging_active = False
            os._exit(1)

    def info(self, content, color: available_colors=None, newline=True):
        self.__log(content, "info", color=color, newline=newline)

    def warn(self, content, color: available_colors="YELLOW", newline=True):
        self.__log(content, "warn", color=color, newline=newline)

    def error(self, content, color: available_colors="RED", newline=True):
        self.__log(content, "error", color=color, newline=newline)

    def newline(self):
        print()

logger = create_logger("utils")

def get_absolute_path(rel_path: str, file=__file__) -> str:
  script_dir = os.path.dirname(file) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, rel_path)
  return abs_file_path

def scale_coordinates(original_coords: tuple, from_resolution: tuple[int, int], to_resolution: tuple[int, int]) -> tuple:
    original_width, original_height = from_resolution
    new_width, new_height = to_resolution

    width_scaling_factor = new_width / original_width
    height_scaling_factor = new_height / original_height

    if len(original_coords) == 2:  # Single pixel (x, y)
        x, y = original_coords
        new_x = int(x * width_scaling_factor)
        new_y = int(y * height_scaling_factor)
        return (new_x, new_y)
    elif len(original_coords) == 4:  # Bounding box (x1, y1, x2, y2)
        x1, y1, x2, y2 = original_coords
        new_x1 = int(x1 * width_scaling_factor)
        new_y1 = int(y1 * height_scaling_factor)
        new_x2 = int(x2 * width_scaling_factor)
        new_y2 = int(y2 * height_scaling_factor)
        return (new_x1, new_y1, new_x2, new_y2)
    
def configure_types(obj: dict[str, dict]) -> dict[str, dict] | tuple[None, str, str, Exception]:
    """
    A function to turn values in specified types

    Params:
        obj:
            Must be a python dict that consists of dicts that hold two attributes, value and type.
    
    The function will, on success, return the dict where each subdict value is the specified type.

    On fail, the function will return a tuple containing (None, the key where the error occured, the target type, the exeption)
    """
    for key, setting in obj.items():
        if isinstance(setting, dict) and 'value' in setting and 'type' in setting and setting["type"] == "dict": # Nested dict
            obj[key] = configure_types(setting)
        elif isinstance(setting, dict) and 'value' in setting and 'type' in setting: # Non nested dict but valid setting
            try:
                match(setting["type"]):
                    case "str":
                        setting["value"] = str(setting["value"])  
                    case "int":
                        setting["value"] = int(setting["value"])
                    case "float":
                        setting["value"] = float(setting["value"])  
                    case "bool":
                        setting["value"] = bool(setting["value"])
                    case "dict":
                        setting["value"] = str_dict(str(setting["value"]))
            except Exception as e:
                    return (None, key, setting["type"], e)
    return obj

def get_settings() -> dict[str, dict]:
    path = get_absolute_path("../settings/settings.json")
    with open(path, "r") as file:
        settings = json.load(file)

    result = configure_types(settings)

    if isinstance(result, tuple) and result[0] == None: # Error parsing settings types
            logger.error(f"\nError while getting settings.\nKey: '{result[1]}'\nTarget Type: '{result[2]}'\nExeption: '{result[3]}'\n")
            quit_program()

    return result

def write_settings(settings: dict[str, dict]) -> None:
    path = get_absolute_path("../settings/settings.json")
    with open(path, "w") as file:
            json.dump(settings, file, indent=2)

def quit_program(UI, exit=False):
    from recoil_handler import stop_event, get_hook_thread_id
    from tracker import tracker_stop_event
    stop_event.set()
    tracker_stop_event.set()
    ctypes.windll.user32.PostThreadMessageW(get_hook_thread_id(), 0x0400, 0, 0)  # This will make the mouse hook exit
    UI.stop_application(from_utils=True, exit=exit)
