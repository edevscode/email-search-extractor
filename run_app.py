# run_app.py
"""
Launcher for Email Extractor Streamlit app (EXE-friendly).

This:
- Works from source (py run_app.py)
- Works as a PyInstaller --onefile EXE
- Forces Streamlit to use port 8501
- Disables dev mode so 3000/404 issues go away
"""

import os
import sys
import time
import threading
import webbrowser
from streamlit.web import cli as stcli


# Figure out where app.py lives (normal vs PyInstaller)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS          # temp folder used by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _open_browser():
    """Open the correct URL after the server starts."""
    time.sleep(2)
    webbrowser.open("http://localhost:8501")


def main():
    os.chdir(BASE_DIR)

    # Start browser in background
    threading.Thread(target=_open_browser, daemon=True).start()

    # Pretend we ran this in a terminal:
    #   streamlit run app.py --server.port 8501 --global.developmentMode false
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        "8501",
        "--global.developmentMode",
        "false",
    ]

    stcli.main()


if __name__ == "__main__":
    main()
