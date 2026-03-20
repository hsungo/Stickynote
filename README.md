![C++](https://img.shields.io/badge/Language-Python-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
# Desktop Sticky Notes APP

**A desktop sticky note application built with Python and Tkinter**

---

##  Key Features

### Smart Task Management
| Icon | Name | Action |
| :---: | :--- | :--- |
| **Top Bar** | **Drag Handle** | Click and drag to move the note. |
| `✖` | **Close** | Closes the application. *(Hidden when locked)* |
| `🔓` / `🔒` | **Lock / Unlock** | Pins the window in place. |
| `🗑` | **Clear All** | Deletes all current tasks. |
| `☰` | **Reorder** | Click and drag up/down to reorder tasks instantly. |
| `□` | **Delete Row** | Deletes the specific task row. |
| `+` / `-` | **Sub-note** | Opens/Closes a hidden text area. |
| `💬` | **New Group** | Creates a new note group. |
| `📅` | **Date** | Adds today's deadline date. |
| `⇲` | **Resize** | Drag to resize the window. *(Hidden when locked)* |

### Advanced Configurations
* **Persistent Data**: Automatically saves metadata to a local `appdata.json`
  > appdata.json automatically appears when the APP starts
* **Group Management**: Groups of different colors can be used to categorize different tasks.
  > Right‑click the icon to delete or rename.
* **Privacy Lock**: After 30 seconds of inactivity, the app hides content to protect your privacy.
  > Can be password-protected.
* **`autostart`**: Defaults `true`.
  * `true` :  the app automatically start when your PC boots up.
  * `false` : disable the function
  > Can be configured in appdata.json
* **`password`**: Defaults `""` (empty).
  Enter a password string to enable the **Privacy Lock**. 
  > Can be configured in appdata.json
   
---

##  How to Run 
* **Prerequisite**
  * Ensure you have **Python 3.x** installed on your system.
  * Git (winget install --id Git.Git -e --source winget)
* **Quick start**
   ```bash
   git clone https://github.com/hsungo/Stickynote.git
   cd Stickynote
   pip install pyinstaller
   pyinstaller --noconsole --onefile noteapp.py
   rm -r build
   rm *.spec
   cd dist
   ./noteapp.exe
   ```
---

