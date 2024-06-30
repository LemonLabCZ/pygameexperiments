import win32api
import win32gui
import win32con
import time


def start_playing_video(window_name):
    hwnd = find_window(window_name)
    if hwnd is None:
        print("This is the list of available windows")
        print("-----------------------------")
        list_open_window_names()
        print("-----------------------------")
        raise Exception("Window not found!")
    set_foreground(hwnd)
    time.sleep(0.1)
    press_space()


def find_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        print("Window not found!")
        return None
    else:
        print(f"Window found: {hwnd}")
    return hwnd


def set_foreground(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


def press_space():
    win32api.keybd_event(0x20, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)


def list_open_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)
