# tray_launcher.py
import sys
import threading
import webbrowser

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

from image_sorter import app  # Import the Flask app

def run_server():
    # Run your Flask server on port 5000, no debug.
    # This call BLOCKS, so we use a background thread.
    app.run(host='127.0.0.1', port=5000, debug=False)

def create_image():
    """Generate a simple tray icon (64x64) via Pillow."""
    icon_size = 64
    image = Image.new('RGB', (icon_size, icon_size), 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle([(0, 0), (icon_size, icon_size)], fill='white')
    draw.text((10, 20), "Img", fill='black')
    return image

def on_clicked(icon, menu_item):
    """Handle menu item clicks from the tray icon."""
    if str(menu_item) == "Open Browser":
        # Open the local server in the browser
        webbrowser.open("http://127.0.0.1:5000")
    elif str(menu_item) == "Exit":
        # Stop the tray icon event loop
        icon.stop()
        # Exit the entire process (kills Flask too, because it’s in a daemon thread)
        sys.exit(0)

def start_tray_icon():
    # Build a right-click menu with "Open Browser" and "Exit"
    menu = (
        item("Open Browser", on_clicked),
        item("Exit", on_clicked),
    )
    # Create the tray icon
    icon = pystray.Icon(
        name="Image Sorter",
        icon=create_image(),
        title="Image Sorter Running",
        menu=menu
    )
    icon.run()

def main():
    # 1) Start Flask in a background thread.
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 2) Start the tray icon in the foreground (blocking).
    start_tray_icon()

if __name__ == "__main__":
    main()
