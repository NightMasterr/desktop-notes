"""Desktop launcher for Notes.

Normal start     -> your notes in their own native window (Windows' built-in Edge engine).
Notes.exe --browser -> starts quietly, opens your default browser, and stops itself
                       a few minutes after the tab is closed.
"""
import json
import logging
import os
import sys
import threading
import time
import urllib.request
import webbrowser

# A windowed .exe has no console; give print/logging somewhere harmless to write.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
logging.getLogger("werkzeug").setLevel(logging.ERROR)

import app as server  # noqa: E402  (the Flask app)
from werkzeug.serving import make_server  # noqa: E402

PORT = 47231
BG = "#e9eeec"  # same as the app background, so there is no white flash
STATE_FILE = os.path.join(server.DATA_DIR, "window.json")
IDLE_SECONDS = 180  # browser mode: quit this long after the last heartbeat

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never use a proxy for localhost


def is_up(port):
    try:
        with _opener.open(f"http://127.0.0.1:{port}/api/ping", timeout=0.4) as r:
            return r.status == 200
    except Exception:
        return False


def start_server():
    """Returns (port, started_here). Reuses a copy that is already running."""
    if is_up(PORT):
        return PORT, False
    try:
        srv = make_server("127.0.0.1", PORT, server.app, threaded=True)
    except OSError:  # port taken by something else: let the system pick one
        srv = make_server("127.0.0.1", 0, server.app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_port
    for _ in range(200):  # wait up to ~5 s, normally a few milliseconds
        if is_up(port):
            break
        time.sleep(0.025)
    return port, True


def run_in_browser(port, started_here):
    webbrowser.open(f"http://127.0.0.1:{port}/")
    if not started_here:
        return  # another copy is already running and will manage itself
    while True:
        time.sleep(10)
        if time.time() - server.STATE["ping"] > IDLE_SECONDS:
            os._exit(0)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def run_in_window(port):
    import webview

    st = load_state()
    opts = {"width": int(st.get("w", 1500)), "height": int(st.get("h", 940))}
    if "x" in st and "y" in st:
        opts.update(x=int(st["x"]), y=int(st["y"]))
    if st.get("max", True):  # opens maximized unless you last left it as a smaller window
        opts["maximized"] = True

    w = webview.create_window(
        "Notes", f"http://127.0.0.1:{port}/",
        min_size=(820, 520), background_color=BG,
        hidden=True,  # shown only once the page is ready: no white flash, no loading screen
        text_select=True, **opts,
    )
    w.events.loaded += lambda: w.show()
    threading.Timer(5, w.show).start()  # safety net, so the window can never stay hidden

    def remember():
        try:
            s = dict(st)
            scr = webview.screens[0]
            if w.width >= scr.width * 0.95 and w.height >= scr.height * 0.90:
                s["max"] = True  # keep the earlier smaller size for when you un-maximize
            else:
                s.update(max=False, w=w.width, h=w.height)
                if -20 <= w.x < 10000 and -20 <= w.y < 10000:  # ignore "minimized" coordinates
                    s.update(x=w.x, y=w.y)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(s, f)
        except Exception:
            pass

    w.events.closing += remember
    webview.start(
        gui="edgechromium",
        private_mode=False,  # keep the engine's cache between runs: faster start
        storage_path=os.path.join(server.DATA_DIR, "webview"),
    )


def main():
    port, started_here = start_server()
    if "--browser" in sys.argv:
        run_in_browser(port, started_here)
        return
    try:
        run_in_window(port)
    except Exception:  # e.g. the Edge engine is missing: still give the user the app
        run_in_browser(port, started_here)
    os._exit(0)


if __name__ == "__main__":
    main()
