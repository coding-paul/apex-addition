import ctypes

# Constants for ctypes
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),       # Relative mouse movement along the x-axis
        ("dy", ctypes.c_long),       # Relative mouse movement along the y-axis
        ("mouseData", ctypes.c_ulong),  # Wheel movement or extra buttons (unused here)
        ("dwFlags", ctypes.c_ulong),   # Flags for mouse actions (e.g., MOUSEEVENTF_MOVE)
        ("time", ctypes.c_ulong),      # Timestamp for the event (0 for current time)
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))  # Extra information (unused)
    ]
class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),  # Type of input (0 for mouse)
        ("mi", MOUSEINPUT)         # Mouse input structure
    ]

def move_mouse(dx, dy):
    INPUT_MOUSE = 0
    MOUSEEVENTF_MOVE = 0x0001  # Flag for mouse movement

    # Prepare the MOUSEINPUT structure
    extra = ctypes.c_ulong(0)
    mouse_input = MOUSEINPUT(
        dx=dx, 
        dy=dy, 
        mouseData=0, 
        dwFlags=MOUSEEVENTF_MOVE, 
        time=0, 
        dwExtraInfo=ctypes.pointer(extra)
    )

    # Wrap it in an INPUT structure
    input_data = INPUT(type=INPUT_MOUSE, mi=mouse_input)

    # Send the input event
    ctypes.windll.user32.SendInput(1, ctypes.pointer(input_data), ctypes.sizeof(input_data))
