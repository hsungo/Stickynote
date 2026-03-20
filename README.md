# Desktop Sticky Notes APP

![Screenshot](放你的截圖連結在這裡.png)

A sleek, minimalist, and feature-rich desktop sticky note application built with Python and Tkinter. Designed to be a true "sticky note," it stays silently on your desktop layer without cluttering your taskbar or obstructing other active applications.

## ✨ Key Features

### 📝 Smart Task Management
* **Live Drag & Drop (☰)**: Instantly reorder your tasks by dragging the handle. The active row is highlighted during dragging, and positions update in real-time.
* **Smart Deadline Tracking (📅)**: Click the calendar icon to stamp today's date. **Dynamic Auto-Update**: If you manually edit the date (e.g., `2026/3/22`), the app will automatically calculate and update the correct day of the week `(Sun)` for you!
* **Sub-Notes (+ / -)**: Expand a hidden text area under any task for detailed descriptions or sub-tasks.
* **Quick Delete (□)**: Remove any task instantly. The list will auto-adjust.
* **One-Click Reset (🗑)**: Clear all tasks and start fresh with a single click (Optimized bold UI for better visibility).

### 🪟 Intelligent Window Controls
* **Frameless & Taskbar-Hidden**: True desktop integration with no OS borders or taskbar icons.
* **Bottom Layer Display**: Stays pinned to the desktop layer, ensuring it never blocks your browser or media players.
* **Safe Lock Mode (🔓 / 🔒)**: Pin the note in place. When locked, it disables dragging, hides the resize grip, and **completely hides the close button (✖)** to prevent accidental data loss.
* **Custom Resizing (⇲)**: Drag the bottom-right corner to adjust the window size freely.
* **Hover UI Effects**: Smooth color transitions when hovering over control buttons for a modern feel.

### 💾 Auto-Save Memory
* **Persistent Data**: Automatically saves your tasks, dates, sub-notes, window position, window size, and lock state to a local `note_data.json` file. Everything restores perfectly upon restart.

## 🚀 How to Run (Development)

1. Ensure you have **Python 3.x** installed.
2. Clone this repository to your local machine.
3. Run the script via terminal:
   ```bash
   python sticky_note.py
   ```