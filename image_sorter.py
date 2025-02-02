# image_sorter.py
import os
import time
import shutil
import uuid
import json
from flask import Flask, request, render_template, redirect, url_for, session, send_file, jsonify

##############################################################################
# Config
##############################################################################

CONFIG_FILE = 'image_sorter_config.json'
DEFAULT_CONFIG = {
    "last_folder": "",
    "buttons": []  # list of { "label": str, "path": str }
}
CONFIG = {}

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
    else:
        CONFIG = DEFAULT_CONFIG.copy()

def save_config():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(CONFIG, f, indent=2)

##############################################################################
# Flask setup
##############################################################################

app = Flask(__name__)
app.secret_key = 'replace-with-any-random-secret-key'

# Just call load_config() once, right after creating the Flask app:
load_config()
app.config['MOVE_BUTTONS'] = CONFIG["buttons"]

# A global in-memory store for session data (like image list).
data_store = {}

def get_session_id():
    """Retrieve or generate a unique ID for the current browser session."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_data_for_session(create_if_missing=True):
    """
    Return a dict with session-specific data:
      {
         'image_folder': str,
         'image_list': list of filenames,
         'current_index': int
      }
    """
    s_id = get_session_id()
    if s_id not in data_store and create_if_missing:
        data_store[s_id] = {
            'image_folder': None,
            'image_list': [],
            'current_index': 0
        }
    return data_store.get(s_id, None)

##############################################################################
# Routes
##############################################################################

@app.route('/')
def index():
    """Main entry point."""
    data = get_data_for_session(create_if_missing=False)
    if data and data['image_folder']:
        # If we have images, figure out the current file name
        file_name = ""
        if data['image_list']:
            file_name = data['image_list'][data['current_index']]

        return render_template(
            "index.html",
            data={
                'image_folder': data['image_folder'],
                'image_list': data['image_list'],
                'current_index': data['current_index'],
                'total_images': len(data['image_list'])
            },
            file_name=file_name,
            move_buttons=app.config['MOVE_BUTTONS'],
            last_folder=CONFIG["last_folder"]
        )
    else:
        # Show the "pick a folder" form
        return render_template(
            "index.html",
            data=None,
            move_buttons=app.config['MOVE_BUTTONS'],
            file_name="",
            last_folder=CONFIG["last_folder"]
        )

@app.route('/set_directory', methods=['POST'])
def set_directory():
    folder = request.form.get('folder', '').strip()
    if not os.path.isdir(folder):
        return f"Directory '{folder}' does not exist. Please go back and try again."

    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    all_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    # Sort by modification time desc
    image_files = []
    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            full_path = os.path.join(folder, f)
            mtime = os.path.getmtime(full_path)
            image_files.append((f, mtime))
    image_files.sort(key=lambda x: x[1], reverse=True)
    image_files = [x[0] for x in image_files]

    data = get_data_for_session()
    data['image_folder'] = folder
    data['image_list'] = image_files
    data['current_index'] = 0

    # Persist to config
    CONFIG["last_folder"] = folder
    save_config()

    return redirect(url_for('index'))

@app.route('/navigate/<direction>')
def navigate(direction):
    data = get_data_for_session(create_if_missing=False)
    if not data or not data['image_list']:
        return redirect(url_for('index'))

    idx = data['current_index']
    total = len(data['image_list'])

    if direction == 'next':
        idx = (idx + 1) if idx < (total - 1) else 0
    elif direction == 'prev':
        idx = (idx - 1) if idx > 0 else (total - 1)

    data['current_index'] = idx
    return redirect(url_for('index'))

@app.route('/ajax_navigate/<direction>')
def ajax_navigate(direction):
    """AJAX endpoint to navigate images without a full page reload."""
    data = get_data_for_session(create_if_missing=False)
    if not data or not data['image_list']:
        return jsonify(error="No images available"), 404

    idx = data['current_index']
    total = len(data['image_list'])
    if direction == 'next':
        idx = (idx + 1) if idx < (total - 1) else 0
    elif direction == 'prev':
        idx = (idx - 1) if idx > 0 else (total - 1)
    else:
        return jsonify(error="Invalid direction"), 400

    data['current_index'] = idx
    file_name = data['image_list'][idx]
    image_url = url_for('show_current_image')
    # Log in Flask (visible in server console)
    app.logger.info(f"AJAX navigate {direction}: index {idx}, file {file_name}")
    return jsonify(image_url=image_url, file_name=file_name)

@app.route('/show_current_image')
def show_current_image():
    data = get_data_for_session(create_if_missing=False)
    if not data or not data['image_list']:
        return ""  # or serve a placeholder image

    folder = data['image_folder']
    idx = data['current_index']
    filename = data['image_list'][idx]
    full_path = os.path.join(folder, filename)
    return send_file(full_path)

@app.route('/add_button', methods=['POST'])
def add_button():
    label = request.form.get('btn_label', '').strip()
    path = request.form.get('btn_path', '').strip()
    if label and path:
        new_btn = {"label": label, "path": path}
        app.config['MOVE_BUTTONS'].append(new_btn)
        CONFIG["buttons"].append(new_btn)
        save_config()
    return redirect(url_for('index'))

@app.route('/move_image', methods=['POST'])
def move_image():
    data = get_data_for_session(create_if_missing=False)
    if not data or not data['image_list']:
        return redirect(url_for('index'))

    target_path = request.form.get('target_path', '').strip()
    if not os.path.isdir(target_path):
        return f"Target folder '{target_path}' does not exist. Please create it or update the button."

    idx = data['current_index']
    filename = data['image_list'][idx]
    src_full = os.path.join(data['image_folder'], filename)
    dst_full = os.path.join(target_path, filename)

    shutil.move(src_full, dst_full)
    data['image_list'].pop(idx)

    if len(data['image_list']) == 0:
        data['current_index'] = 0
    else:
        data['current_index'] = min(idx, len(data['image_list']) - 1)

    return redirect(url_for('index'))

@app.route('/remove_button', methods=['POST'])
def remove_button():
    remove_path = request.form.get('remove_path', '').strip()
    if not remove_path:
        return redirect(url_for('index'))

    # 1) Remove from app.config['MOVE_BUTTONS']
    new_buttons = []
    for b in app.config['MOVE_BUTTONS']:
        if b['path'] != remove_path:
            new_buttons.append(b)
    app.config['MOVE_BUTTONS'] = new_buttons

    # 2) Remove from CONFIG["buttons"] and save
    new_config_buttons = []
    for b in CONFIG["buttons"]:
        if b['path'] != remove_path:
            new_config_buttons.append(b)
    CONFIG["buttons"] = new_config_buttons
    save_config()

    return redirect(url_for('index'))

@app.route('/change_folder', methods=['POST'])
def change_folder():
    """
    Expects JSON { "folder": "C:/some/path" }, used by the clickable folder text
    in the right panel. Switches to new folder if valid, else returns error JSON.
    """
    data = get_data_for_session(create_if_missing=True)
    if not data:
        return {"error": "No session data found"}, 400

    payload = request.get_json()
    if not payload:
        return {"error": "Missing JSON data"}, 400

    new_folder = payload.get("folder", "").strip()
    if not new_folder:
        return {"error": "Invalid folder path"}, 400

    if not os.path.isdir(new_folder):
        return {"error": f"Directory '{new_folder}' does not exist."}, 400

    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    all_files = [f for f in os.listdir(new_folder) if os.path.isfile(os.path.join(new_folder, f))]

    image_files = []
    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            full_path = os.path.join(new_folder, f)
            mtime = os.path.getmtime(full_path)
            image_files.append((f, mtime))
    image_files.sort(key=lambda x: x[1], reverse=True)
    image_files = [x[0] for x in image_files]

    data['image_folder'] = new_folder
    data['image_list'] = image_files
    data['current_index'] = 0

    CONFIG["last_folder"] = new_folder
    save_config()

    return {"status": "ok", "new_folder": new_folder, "count": len(image_files)}, 200

@app.route('/rename_image', methods=['POST'])
def rename_image():
    data = get_data_for_session(create_if_missing=False)
    if not data or not data['image_list']:
        return "No session data or images found", 400

    payload = request.get_json()
    if not payload:
        return "Missing JSON data", 400

    old_name = payload.get("old_name", "").strip()
    new_base = payload.get("new_base", "").strip()
    if not old_name or not new_base:
        return "Invalid rename parameters", 400

    folder = data['image_folder']
    if old_name not in data['image_list']:
        return f"File '{old_name}' not found in current list", 404

    old_full = os.path.join(folder, old_name)
    if not os.path.isfile(old_full):
        return "Original file not found on disk", 404

    _, ext = os.path.splitext(old_name)
    new_name = new_base + ext
    new_full = os.path.join(folder, new_name)

    try:
        os.rename(old_full, new_full)
    except OSError as e:
        return f"Rename error: {str(e)}", 500

    idx = data['image_list'].index(old_name)
    data['image_list'][idx] = new_name

    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True)