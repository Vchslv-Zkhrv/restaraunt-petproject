
import os as _os

_os.environ["DISPLAY"] = ":0"

import pyautogui as _gui


cwd = _os.getcwd()


def _run_frontend_server(path: str):
    _gui.hotkey("Ctrl", "b", "Shift", "5")
    _gui.write(f"cd {path}")
    _gui.hotkey("enter")


def run_frontend():
    frontend = _os.path.join(cwd, "frontend")
    _gui.hotkey("Ctrl", "b", "Shift", "'")
    for dirname in _os.listdir(frontend):
        _run_frontend_server(_os.path.join(frontend, dirname))


if __name__ == "__main__":
    run_frontend()

