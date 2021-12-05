# Do not question this file, it's to fix that windows is fucking stupid

try:
    import curses
except Exception:
    import sys
    print("Curses is not installed")
    print(f"Please go to \033[96mhttps://www.lfd.uci.edu/~gohlke/pythonlibs/#curses\033[0m and download \033[92mcurses‑x.x.x+utf8‑cp{sys.version_info.major}{sys.version_info.minor}‑cp{sys.version_info.major}{sys.version_info.minor}‑{'win_amd64' if sys.maxsize > 2**32 else 'win32'}.whl\033[0m (replace x.x.x with the latest version) the install with \033[92m{sys.executable} -m pip install \"\033[31m<path to downloaded file>\033[92m\"\033[0m")
    exit(1)

try:
    import pywin32
except Exception:
    import subprocess, sys
    print("pywin32 is not installed, installing")
    subprocess.call([sys.executable, "-m", "pip", "install", "pywin32"])
    exit(1)
