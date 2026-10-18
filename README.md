# Notes for Windows

A fast, private note taker. No account, no ads, no tracking. Your notes stay on your own computer and it works fully offline.

## Download

Open the **[Releases](../../releases/latest)** page and download `Notes-Setup-x.x.x.exe` (Windows 10 / 11).

1. Run the installer. It installs for your user account and needs no admin rights.
2. Windows may show **"Windows protected your PC"**, because the installer is not code-signed. Click **More info**, then **Run anyway**.
3. Open **Notes** from the Start menu or the desktop icon.

There is also a **Notes (browser)** shortcut in the Start menu. It opens the same app in your normal browser and stops by itself a few minutes after you close the tab.

## Your notes
Notes are saved in `%APPDATA%\Notes\notes.json`. Copy that file now and then as a backup.

## Features
- The list shows only note names. Select words in a note and press **Shift+Enter** to make them the note's name
- 12 colors, search, pin, archive, recycle bin and lock
- Right-click a note for its menu. With the list focused: `P` pin, `A` archive, `L` lock, `Delete` delete, `R` restore, `Alt`+arrow keys reorder
- Click anywhere in the writing area and type right there
- Drag the divider to resize the sidebar

## Build it yourself
The installer is built by GitHub Actions (`.github/workflows/release-desktop.yml`) with Python, Flask, pywebview and PyInstaller.

## License
See [LICENSE](LICENSE).
