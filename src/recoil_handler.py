import json
import time
import threading
import ctypes
from ctypes import wintypes

import utils
from tracker import get_current_weapon as tracker_get_current_weapon, main as tracker_thread, tracker_stop_event

# Windows API constants and structures
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
LPARAM = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
mouse_hook = None
hook_thread_id = None
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),   # The x and y coordinates of the cursor
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

# Global variables
SETTINGS = utils.get_settings()
UI = None
is_left_mouse_down = False
is_right_mouse_down = False
logger = utils.create_logger("main.py")
patterns: dict[list] = None
stop_event = threading.Event()
lock = threading.Lock()

def get_hook_thread_id():
    with lock:
        return hook_thread_id
    
def set_hook_thread_id(val):
    global hook_thread_id
    with lock:
        hook_thread_id = val

def hook_thread():
    set_hook_thread_id(ctypes.windll.kernel32.GetCurrentThreadId())
    hook_handle = install_mouse_hook()

    try:
        msg = wintypes.MSG()
        while not stop_event.is_set() and ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
    finally:
        ctypes.windll.user32.UnhookWindowsHookEx(hook_handle)

# Install the hook
def install_mouse_hook() -> int:
    global mouse_hook  # Keep a reference to prevent garbage collection
    HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, LPARAM)
    mouse_hook = HOOKPROC(mouse_hook_proc)  # Store the hook procedure globally
    hook_handle = ctypes.windll.user32.SetWindowsHookExW(WH_MOUSE_LL, mouse_hook, None, 0)

    if not hook_handle:
        error_code = ctypes.GetLastError()
        logger.error(f"Failed to install hook! Error code: {error_code}")
        utils.quit_program()
        quit(1)

    return hook_handle

# Callback function for the mouse hook
def mouse_hook_proc(nCode, wParam, lParam) -> int:
    if nCode != 0: # No event
        return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, LPARAM(lParam))
    
    global is_left_mouse_down, is_right_mouse_down
    # mouse_data = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
    if wParam == WM_LBUTTONDOWN:
        is_left_mouse_down = True
    elif wParam == WM_LBUTTONUP:
        is_left_mouse_down = False
    elif wParam == WM_RBUTTONDOWN:
        is_right_mouse_down = True
    elif wParam == WM_RBUTTONUP:
        is_right_mouse_down = False

    if wParam == WM_LBUTTONDOWN or wParam == WM_RBUTTONDOWN:
        if SETTINGS["HOLD_RIGHT"]["value"]:
            if is_left_mouse_down and is_right_mouse_down:
                threading.Thread(target=move_mouse_pattern).start()
        elif is_left_mouse_down:
            threading.Thread(target=move_mouse_pattern).start()
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, LPARAM(lParam))

def move_mouse_pattern() -> None:
    pattern, pattern_name = load_pattern()

    if isinstance(pattern, list):
        logger.info(f"Moving mouse via the pattern: {pattern_name} with a length of: {len(pattern)}")
        for move in pattern:
            if SETTINGS["HOLD_RIGHT"]["value"]:
                if not is_left_mouse_down or not is_right_mouse_down:
                    return
            else:
                if not is_left_mouse_down:
                    return

            sensitivity_factor = SETTINGS["SENSITIVITY"]["value"] / 5
            ctypes.windll.user32.mouse_event(
                0x0001,
                int(move[0] * sensitivity_factor),
                int(move[1] * sensitivity_factor),
                0,
                0
            )
            time.sleep(move[2])

def load_pattern() -> tuple[list, str]:
    logger.info("\nLoading pattern...")
    weapon_scan = tracker_get_current_weapon()

    if weapon_scan is None:
        logger.warn("No weapon detected yet")
        return None, None

    for pattern_name in patterns:
        if weapon_scan == pattern_name:
            return patterns[pattern_name], pattern_name

    logger.error(f"Pattern not found for '{weapon_scan}'")
    return None, None

def main(ui) -> None:
    global UI, patterns, SETTINGS
    UI = ui

    SETTINGS = utils.get_settings()
    stop_event.clear()
    logger.info("\nRecoil_handler running...", color="CYAN")

    path = utils.get_absolute_path("recoil_patterns.json")
    with open(path, 'r') as file:
        data = json.load(file)
        patterns = data["recoil_patterns"]

    hook_thread_instance = threading.Thread(target=hook_thread)
    hook_thread_instance.start()

    tracker_thread_instance = threading.Thread(target=tracker_thread, args=(UI,))
    tracker_thread_instance.start()

if __name__ == '__main__':
    logger.error("\nRecoil_handler must be called from UI\n")
