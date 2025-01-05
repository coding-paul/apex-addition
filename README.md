# Apex Addition

This project provides a motivation booster when playing apex.

Recoil is actually a very annoying and unnecessary feature isn't it? 

## Authors

- [@Paul](https://www.github.com/coding-paul)
- [@Finn](https://www.github.com/Feuerkrabbe)

## Prerequisites

The following prerequisites must be installed on the system:

### Git

A guide on how to download and install **Git** can be found [here](https://learn.microsoft.com/de-de/devops/develop/git/install-and-set-up-git)

### Python3.11

A guide on how to download and install **Python** can be found [here](https://www.simplilearn.com/tutorials/python-tutorial/python-installation-on-windows) <br/>
Currently, the pynput module is broken on the python versions 3.12 and above. Therefore, is is needed to install python on version 3.11

### Visual Studio Code (VSCode)

A guide on how to download and install **VSCode** can be found [here](https://www.gitkraken.com/blog/vs-code-download)<br/>
Also the extention python is needed.

### Tesseract

Can be downloaded from the GitHub by UB Mannheim [here](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe), install it and save your path if you choose to install it on a different directory then the default local installment

### Apex Legends

A guide on how to download and install **Apex Legends** can be found [here](https://www.hp.com/us-en/shop/tech-takes/how-to-play-apex-legends-on-pc)

## Installation

Install the project via **git**

```bash
  git clone https://github.com/coding-paul/apex-addition.git
```

## Deployment


To deploy this project:

1. Open up VSCode on the directory that the project has been installed on
2. Open up a terminal by clicking **Terminal** at the top and then **New Terminal**
3. Create a virtual environment using ```python -m venv .venv``` ; the name of the venv must be .venv
4. Change the pyhton interpreter to the venv python here is how: 
    1. Open up main.py in the editor by clicking on its name on the left
    2. In the bottom right click the version next to python and select the python interpreter under the relative path: ".\\.venv\Scripts\python.exe"
4. Activate the virtual environment using ```.venv\Scripts\activate.bat```
5. Install the requirements in the requirements.txt file using ```pip install -r requirements.txt```
6. Launch main.py
7. Click **Change settings** and change the tesseract path to the installation of **Tesseract**, as listed above. If tesserect was installed on the default path, just change the user here. Click **Save Settings**
8. Click **Start Program**
9. The program is now active and ready for you to play apex

## Features

- User interface
- Automatic resolution detection
- Automatic active weapon detection
- Recoil-balancer for different detected weapons

## Settings 

Settings and the corresponding Documentation can be found in the ./settings directory