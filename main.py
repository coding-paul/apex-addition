'''

Start this script to run the UI of the application

In the UI you can start the actual anti recoil script, which will call recoil_handler.py and this will activate the tracker.py 

'''

import subprocess
from src.utils import get_absolute_path

if __name__ == "__main__":
    path = get_absolute_path("src/ui.py", __file__)
    venv_python = get_absolute_path(".venv/Scripts/python.exe", __file__)
    subprocess.Popen([venv_python, path])
