# 🖼️ Image Sorter

A **Flask-based** tool for sorting images into folders, with a **tray icon launcher** for easy access on Windows. Users can navigate through images in a folder, move them to predefined locations, rename them, and even edit the folder path inline. 

---

## 🚀 Features

- **Web-based Interface** – Runs a local Flask server and provides a UI for sorting images.
- **Folder Navigation** – View images in a selected folder, switch folders dynamically.
- **Move Images** – Custom buttons allow quick and easy moving images to predefined folders.
- **Scroll Navigation** –  
  - **Scroll wheel** moves **next/previous** image.  
  - **Ctrl + Scroll** zooms **into the cursor position** (only on the left panel).  
- **File Renaming** – Click on the image filename to rename it.
- **Inline Folder Path Editing** – Click the folder path, modify it, and press Enter to switch folders.
- **System Tray Icon (Windows)** – `tray_launcher.py` minimizes the script to the system tray so you can open in browser or close it.
- **move-to buttons save for later** in 'image_sorter_config.json', so they're saved between sessions. Delete this file to reset the move-to buttons.
---

## 🛠️ Installation

### **1️⃣ Install Dependencies**
Ensure you have **Python 3.10+** installed, then install the required libraries:

```sh
pip install -r requirements.txt
```
Run using `Image Sorter.bat`, or if you just want the flask server without the Windows system tray icon, run with `python image_sorter.py`
## Screenshot
![alt text](screenshot-1.png)
