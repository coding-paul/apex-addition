# SETTINGS

In the settings.json file in this directory the user settins can be adjusted, see below for a documentation of all of the available settings. Changing settings the wrong way will lead to the program not working. 

| SETTING                 | DESCRIPTION 
| ----------------------- | ------------- 
| TESSERACT_PATH          | Path to the Tesseract installation <br/> Default: Default path to the local tesseract installation, change the user here.
| HOLD_RIGHT              | Use True when holding right mouse button to go into scope, use False when going into scope on press <br/> default: True
| QUIT_KEY                | The key used to stop the program <br/> Default: "p"
| SENSITIVITY             | The sensitivity in the apex settings. This is needed to move the mouse at the right speed <br/> Default: 5
| TRACKER_DELAY           | Time in seconds between checks of the held weapon. This is to save recources <br/> Default: 0.5
| WINDOW_SIZE             | Size of the window in Pixel <br/> Default: "400x300"
| APEX_MONITOR            | Which monitor apex is played on <br/> Default: 1
| UI_MONITOR              | Which monitor the ui is printed on. <br/> Default: 1
| AUTO-DETECT-RESOLUTION  | Used to specify custom resolution when you dont want the program to auto-detect it. Set the AUTO-DETECT property to false and enter the wanted custom resolution in x and y. <br/> Default: {"AUTO-DETECT": true, "WIDTH": null, "HEIGHT": null}
