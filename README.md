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
| `💬` | **New Tab** | Creates a new note group. |
| `📅` | **Date** | Adds today's deadline date. |
| `⇲` | **Resize** | Drag to resize the window. *(Hidden when locked)* |

### Advanced Configurations
* **Persistent Data**: Automatically saves metadata to a local `note_data.json`
  > Everything restores perfectly upon restart.
* **`autostart` (true/false)**: Defaults to `true`. When set to true, the app automatically writes itself to the Windows Registry to launch silently when your PC boots up. Change to `false` to disable auto-start.
* **`password` (string)**: Defaults to `""` (empty). Enter a password string (e.g., `"password": "123"`) to enable the **Privacy Lock**. If enabled, the app will hide your notes after 30 seconds of inactivity and require this password to unlock.
* **Idle Privacy Lock**: After 30 seconds of inactivity, the app hides your tasks and displays a "to do list" button to protect your privacy. (Can be password-protected via JSON).   
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

## Future Work
- [ ] multi category
- [ ] color change
- [x] TBD
   
