# run_app.py
"""
Launcher for Email Extractor custom UI app (EXE-friendly).

This:
- Works from source (py run_app.py)
- Works as a PyInstaller --onefile EXE
- Runs a local FastAPI server (Uvicorn) on port 8501
"""

import os
import sys
import time
import threading
import webbrowser
import traceback
import urllib.request

import uvicorn


# Figure out where app.py lives (normal vs PyInstaller)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS          # temp folder used by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _open_browser():
    """Open the correct URL after the server starts."""
    url = "http://localhost:8501"
    health_url = "http://127.0.0.1:8501/health"

    # In an EXE, startup can take longer. Wait for /health to respond.
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.5)

    webbrowser.open(url)


def main():
    os.chdir(BASE_DIR)

    # In one-file EXE mode, BASE_DIR points to the temporary _MEIPASS folder.
    # Store logs next to the executable so they persist.
    if getattr(sys, "frozen", False):
        log_dir = os.path.dirname(sys.executable)
    else:
        log_dir = os.getcwd()
    log_path = os.path.join(log_dir, "launcher.log")

    # PyInstaller --noconsole can set stdout/stderr to None. Uvicorn's default
    # logging formatter expects a stream with .isatty(), so we provide a safe
    # fallback.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")  # noqa: SIM115

    # Start browser in background
    threading.Thread(target=_open_browser, daemon=True).start()

    # Import after changing working directory. This avoids surprises when
    # running from a frozen EXE where startup order matters.
    from server import app as fastapi_app

    try:
        uvicorn.run(
            fastapi_app,
            host="127.0.0.1",
            port=8501,
            log_level="info",
            log_config=None,
        )
    except Exception:
        # With --noconsole we won't see stderr. Log to a file for debugging.
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n" + ("=" * 70) + "\n")
                f.write("Launcher crash\n")
                f.write(traceback.format_exc())
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
