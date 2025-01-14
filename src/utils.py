import os
import json
from typing import Literal

available_colors = Literal["BLUE", "CYAN", "GREEN", "YELLOW", "RED"]
class create_logger():
    def __init__(self, name: str):
        self.name = name
        self.ui_logging_active = False
        self.UI = None

        self.OKBLUE = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.HEADER = '\033[95m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

    def init_ui_logging(self, UI):
        if not isinstance(UI):
            self.error(f"Error when initializing ui for logging, {UI} is not a valid ui class")
            return
        self.UI = UI
        self.ui_logging_active = True

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

        # Actual print statement
        print(newline_prefix + color_prefix + value + self.ENDC + newline_suffix, end="\n" if newline else "") # This is without the message prefix and without the name

        # If there is a UI, also log it to it
        if self.ui_logging_active:
            ...

    def info(self, content, color: available_colors=None, newline=True):
        self.__log(content, "info", color=color, newline=newline)

    def warn(self, content, color: available_colors="YELLOW", newline=True):
        self.__log(content, "warn", color=color, newline=newline)

    def error(self, content, color: available_colors="RED", newline=True):
        self.__log(content, "error", color=color, newline=newline)

    def newline(self):
        print()

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
    
def get_settings() -> dict[dict]:
    def __custom_decoder(obj: dict):
        for key, value in obj.items():
            # Check if 'value' is present in the current dictionary
            if isinstance(value, dict) and 'value' in value:
                # Convert integers to booleans only if description hints a boolean
                if "True" in value['description'] or "False" in value['description']:
                    if value['value'] == 1:
                        value['value'] = True
                    elif value['value'] == 0:
                        value['value'] = False
            # Recursively process nested dictionaries
            elif isinstance(value, dict):
                obj[key] = __custom_decoder(value)
        return obj
    path = get_absolute_path("../settings/settings.json")
    with open(path, "r") as file:
        return json.load(file, object_hook=__custom_decoder)

def quit_program(UI, exit=False):
    from recoil_handler import stop_event
    from tracker import tracker_stop_event
    stop_event.set()
    tracker_stop_event.set()
    UI.stop_application(from_utils=True, exit=exit)
