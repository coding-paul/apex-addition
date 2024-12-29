import os
from typing import Literal

def get_absolute_path(rel_path: str) -> str:
  script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
  abs_file_path = os.path.join(script_dir, rel_path)
  return abs_file_path

available_colors = Literal["BLUE", "CYAN", "GREEN", "YELLOW", "RED"]
class create_logger():
    def __init__(self, name: str):
        self.name = name
        self.OKBLUE = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.HEADER = '\033[95m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

    def __log(self, value: str, message_type: str, color: available_colors=None, newline=True):
        newline_prefix = ""
        newline_suffix = ""
        while value.startswith("\n"):
            newline_prefix += "\n"
            value = value[1:]  # Remove the first leading newline character
        while value.endswith("\n"):
            newline_suffix += "\n"
            value = value[:-1]  # Remove the first leading newline character

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

        # print(newline_prefix + color_prefix + message_prefix + self.name + "::" + value + self.ENDC + newline_suffix, end="\n" if newline else "") # Full printout line
        print(newline_prefix + color_prefix + value + self.ENDC + newline_suffix, end="\n" if newline else "") # This is without the message prefix and without the name

    def info(self, content, color: available_colors=None, newline=True):
        self.__log(content, "info", color=color, newline=newline)

    def warn(self, content, color: available_colors="YELLOW", newline=True):
        self.__log(content, "warn", color=color, newline=newline)

    def error(self, content, color: available_colors="RED", newline=True):
        self.__log(content, "error", color=color, newline=newline)

    def newline(self):
        print()