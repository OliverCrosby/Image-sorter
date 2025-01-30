# tray_launcher.py
import sys
import threading
import webbrowser
import os

import pystray
from pystray import MenuItem as item
from PIL import Image

from image_sorter import app  # Import the Flask app

ICON_PATH = "icon.ico"  # Path to your custom icon

def run_server():
    """Run the Flask server in a background thread."""
    app.run(host='127.0.0.1', port=5000, debug=False)

def load_icon():
    """Load the tray icon from the ICO file."""
    if os.path.exists(ICON_PATH):
        return Image.open(ICON_PATH)
    else:
        print(f"Warning: {ICON_PATH} not found! Using default tray icon.")
        return None  # Falls back to default if icon is missing

def on_clicked(icon, menu_item):
    """Handle menu item clicks from the tray icon."""
    if str(menu_item) == "Open Browser":
        webbrowser.open("http://127.0.0.1:5000")
    elif str(menu_item) == "Exit":
        icon.stop()
        sys.exit(0)

def start_tray_icon():
    """Create and run the system tray icon."""
    menu = (
        item("Open Browser", on_clicked),
        item("Exit", on_clicked),
    )
    
    # Load the custom icon or fallback
    tray_icon = load_icon()

    # Create the tray icon
    icon = pystray.Icon(
        name="Image Sorter",
        icon=tray_icon,
        title="Image Sorter Running",
        menu=menu
    )

    icon.run()

def main():
    """Start Flask server in the background and tray icon in the foreground."""
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    start_tray_icon()  # Runs in foreground

if __name__ == "__main__":
    main()
