import tkinter as tk
import main # Import main app from same directory
from pynput import keyboard
from threading import Thread, Event


# Tkinter variables
is_main_screen = False
main_screen = None
key_label = None

app: Thread = None
stop_event = Event()
listener = None
app_running = False  # New variable to track the state
start_stop_key = 'h'  # Default key

def show_title_screen():
    global is_main_screen, title_screen, key_label
    print("Showing title screen")
    if main_screen:
        main_screen.destroy()
    title_screen = tk.Tk()
    title_screen.title("Aimbot")
    title_screen.geometry("400x600")
    title_label = tk.Label(title_screen, text="Aimbot", font=("Helvetica", 24))
    title_label.pack(pady=50)
    start_button = tk.Button(title_screen, text="Start", command=start_app)
    start_button.pack(pady=20)
    set_key_button = tk.Button(title_screen, text="Set Start/Stop Key", command=set_key)
    set_key_button.pack(pady=20)
    key_label = tk.Label(title_screen, text=f"Key: {start_stop_key}", font=("Helvetica", 24))
    key_label.pack(pady=50)
    is_main_screen = False
    title_screen.mainloop()

def start_app(event=None):
    global is_main_screen, main_screen, title_screen, app_running, key_label
    print("Starting app")
    if not is_main_screen:
        title_screen.destroy()
        main_screen = tk.Tk()
        main_screen.title("Main Application")
        main_screen.geometry("400x300")
        label = tk.Label(main_screen, text="Application is OFF")
        label.pack(pady=20)
        key_label = tk.Label(main_screen, text=f"Start/Stop Key: {start_stop_key}")
        key_label.pack(pady=20)
        stop_button = tk.Button(main_screen, text="Stop", command=show_title_screen)
        stop_button.pack(pady=20)
        is_main_screen = True
        app_running = False  # Ensure the app starts in the "OFF" state
        main_screen.mainloop()

def set_key():
    global title_screen
    print("Setting key")
    key_window = tk.Toplevel(title_screen)
    key_window.title("Set Start/Stop Key")
    key_window.geometry("300x200")
    label = tk.Label(key_window, text="Press a key to set as Start/Stop key")
    label.pack(pady=20)
    key_window.bind('<Key>', save_key)

def save_key(event):
    global start_stop_key
    start_stop_key = event.keysym
    print(f"Key set to: {start_stop_key}")
    event.widget.destroy()
    update_key_label()  # Update the label to show the new key

def on_press(key):
    global start_stop_key, app_running, app
    try:
        if key.char == start_stop_key:
            app_running = not app_running  # Toggle the state
            print(f"Key pressed: {key.char}, app_running: {app_running}")
            update_label()  # Update the label text
            if app_running:
                app = Thread(target=main.main, args=[stop_event]).start()  # Start the main app in a new thread
            elif app:
                stop_event.set()  # Stop the main app
    except AttributeError:
        pass

def update_label():
    global main_screen, app_running
    if main_screen:
        label_text = "Application is ON" if app_running else "Application is OFF"
        print(f"Updating label to: {label_text}")
        for widget in main_screen.winfo_children():
            if isinstance(widget, tk.Label) and "Application is" in widget.cget("text"):
                widget.config(text=label_text)

def update_key_label():
    global main_screen, start_stop_key, key_label
    if main_screen:
        key_label.config(text=f"Key: {start_stop_key}")
        for widget in main_screen.winfo_children():
            if isinstance(widget, tk.Label) and "Start/Stop Key" in widget.cget("text"):
                widget.config(text=f"Start/Stop Key: {start_stop_key}")

def start_listener():
    global listener
    print("Starting listener")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


def main():
    start_listener()
    show_title_screen()

if __name__ == "__main__":
    main()
