import json
import os
import shutil
import sys
import time
import uuid

from flask import Flask, jsonify, request, send_from_directory

FROZEN = getattr(sys, "frozen", False)  # True inside the packaged Notes.exe
# BASE holds the read-only app files (index.html, style.css, fonts).
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR holds your notes. The .exe keeps them in %APPDATA%\Notes so
# updating or moving the program never touches them.
DATA_DIR = os.environ.get("NOTES_DATA_DIR") or (
    os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Notes") if FROZEN else BASE
)
DATA_FILE = os.path.join(DATA_DIR, "notes.json")
STATE = {"ping": time.time()}  # last time a page said "I'm still open"

EDITABLE = ("title", "label", "body", "color", "pinned", "archived",
            "deleted", "locked", "sort", "pin_order")
# A locked note refuses these changes until it is unlocked.
LOCK_BLOCKED = ("title", "label", "body", "color", "archived", "deleted")

app = Flask(__name__)


def seed_data():
    """First run of the .exe: import the notes.json that sits next to it."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if FROZEN and not os.path.exists(DATA_FILE):
        old = os.path.join(os.path.dirname(sys.executable), "notes.json")
        if os.path.exists(old):
            shutil.copy(old, DATA_FILE)


seed_data()


def load_notes():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    for n in notes:  # keep notes from older versions working
        n.setdefault("label", "")
        n.setdefault("pinned", False)
        n.setdefault("archived", False)
        n.setdefault("deleted", False)
        n.setdefault("locked", False)
        n.setdefault("sort", n.get("updated", 0))
        n.setdefault("pin_order", 0)
    return notes


def save_notes(notes):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)  # safe write: never leaves a half-written file


@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE, "style.css")


@app.route("/fonts/<path:name>")
def fonts(name):
    return send_from_directory(os.path.join(BASE, "fonts"), name)


@app.route("/api/ping")
def ping():
    STATE["ping"] = time.time()
    return jsonify({"ok": True})


@app.route("/api/notes", methods=["GET"])
def list_notes():
    return jsonify(load_notes())


@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    now = time.time()
    note = {
        "id": uuid.uuid4().hex,
        "title": data.get("title", ""),
        "label": "",
        "body": data.get("body", ""),
        "color": data.get("color", "sage"),
        "pinned": False,
        "archived": False,
        "deleted": False,
        "locked": False,
        "sort": now,
        "pin_order": 0,
        "updated": now,
    }
    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    return jsonify(note), 201


@app.route("/api/notes/<note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json(silent=True) or {}
    notes = load_notes()
    for note in notes:
        if note["id"] != note_id:
            continue
        blocked = []
        if note.get("locked") and data.get("locked") is not False:
            blocked = [k for k in data if k in LOCK_BLOCKED]
            data = {k: v for k, v in data.items() if k not in LOCK_BLOCKED}
        for key in EDITABLE:
            if key in data:
                note[key] = data[key]
        if "title" in data or "body" in data:
            note["updated"] = time.time()
        save_notes(notes)
        if blocked:
            return jsonify({"error": "Note is locked", **note}), 423
        return jsonify(note)
    return jsonify({"error": "Note not found"}), 404


@app.route("/api/notes/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Permanent delete (used from Recycle). Locked notes are refused."""
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id and note.get("locked"):
            return jsonify({"error": "Note is locked"}), 423
    save_notes([n for n in notes if n["id"] != note_id])
    return jsonify({"deleted": note_id})


@app.route("/api/bin", methods=["DELETE"])
def empty_bin():
    save_notes([n for n in load_notes() if not (n["deleted"] and not n["locked"])])
    return jsonify({"emptied": True})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
