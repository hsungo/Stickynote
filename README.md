![C++](https://img.shields.io/badge/Language-Python-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
# Desktop Sticky Notes APP

**A desktop sticky note application built with Python and Tkinter**

---

##  Key Features

### 📝 Smart Task Management
| Icon | Name | Action |
| :---: | :--- | :--- |
| **Top Bar** | **Drag Handle** | Click and drag to move the note. |
| `✖` | **Close** | Closes the application. *(Hidden when locked)* |
| `🔓` / `🔒` | **Lock / Unlock** | Pins the window in place. |
| `🗑` | **Clear All** | Deletes all current tasks. |
| `☰` | **Reorder** | Click and drag up/down to reorder tasks instantly. |
| `□` | **Delete Row** | Deletes the specific task row. |
| `+` / `-` | **Sub-note** | Opens/Closes a hidden text area. |
| `📅` | **Date** | Adds today's deadline date. |
| `⇲` | **Resize** | Drag to resize the window. *(Hidden when locked)* |

### 💾 Auto-Save Memory
* **Persistent Data**: Automatically saves metadata to a local `note_data.json`
  > Everything restores perfectly upon restart.
  
---

## 🚀 How to Run (Development)
* **Prerequisite**
  * Ensure you have **Python 3.x** installed on your system.
* **Quick start**
   ```bash
   git clonehttps://github.com/hsungo/Stickynote.git
   cd Stickynote
   pip install pyinstaller
   pyinstaller --noconsole --onefile noteapp.py
   rm -rf build
   rm *.spec
   cd dist
   ./noteapp
   ```


   
