import os
import sys
import shutil
import time
import tkinter as tk
import json

# Get the correct directory for both script and exe
def get_application_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (exe)
        return os.path.dirname(sys.executable)
    else:
        # If the application is run from a Python interpreter
        return os.path.dirname(os.path.abspath(__file__))

# Constants
SCRIPT_DIR = get_application_path()
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "automover_settings.json")
DEFAULT_SOURCE_FOLDER = r"C:\temp"  # Default value for source folder

# Add sys import at the top if not already there
import sys

def save_settings():
    """Save all prefix and path pairs to JSON file"""
    settings = {
        "pairs": [
            {"prefix": prefix.get(), "path": path.get()}
            for prefix, path in entry_pairs
        ],
        "remove_prefix": remove_prefix_var.get(),
        "source_folder": source_entry.get()
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        status_label.config(text="Settings saved successfully")
    except Exception as e:
        status_label.config(text=f"Error saving settings: {str(e)}")

def load_settings():
    """Load prefix and path pairs from JSON file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                pairs = settings.get("pairs", [])
                
                # Load prefix removal setting
                remove_prefix_var.set(settings.get("remove_prefix", True))
                
                # Load source folder
                source_folder = settings.get("source_folder", DEFAULT_SOURCE_FOLDER)
                source_entry.delete(0, tk.END)
                source_entry.insert(0, source_folder)
                
                # Clear all existing rows
                for widget in rows_frame.winfo_children():
                    widget.destroy()
                entry_pairs.clear()
                
                # Add rows for each saved pair
                for pair in pairs:
                    row = add_row()
                    prefix, path = entry_pairs[-1]  # Get the last added pair
                    prefix.insert(0, pair.get("prefix", ""))
                    path.insert(0, pair.get("path", ""))
                
                # Add one empty row if no settings were loaded
                if not pairs:
                    add_row()
                
                status_label.config(text="Settings loaded successfully")
    except Exception as e:
        status_label.config(text=f"Error loading settings: {str(e)}")

root = tk.Tk()
root.title("AutoMover")

# Define dark theme colors
COLORS = {
    'bg': '#2b2b2b',  # Dark background
    'fg': '#ffffff',  # White text
    'entry_bg': '#3b3b3b',  # Slightly lighter background for entries
    'entry_fg': '#ffffff',  # White text for entries
    'button_bg': '#404040',  # Button background
    'button_fg': '#ffffff',  # Button text
    'accent': '#007acc',  # Blue accent color
    'checkbox_bg': '#3b3b3b'  # Checkbox background
}

# Configure root window
root.configure(bg=COLORS['bg'])
root.option_add('*Font', 'Arial 10')

# Create checkbox variable for prefix removal setting
remove_prefix_var = tk.BooleanVar(value=True)  # Default to removing prefix

# Define your prefix → destination mapping
ROUTES = {}

SOURCE_FOLDER = r"C:\temp"

def move_files():
    pairs = get_values()
    if not pairs:
        status_label.config(text="Please enter at least one prefix and path pair")
        return
        
    # Get and validate source folder
    source_folder = source_entry.get()
    if not source_folder:
        status_label.config(text="Please enter a source folder path")
        return
    if not os.path.exists(source_folder):
        status_label.config(text="Source folder does not exist")
        return
    
    total_files_moved = 0
    
    # Process each prefix-path pair
    for prefix, destination in pairs:
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
            except Exception as e:
                status_label.config(text=f"Error creating directory: {e}")
                continue
        
        # Check all files in source folder
        for filename in os.listdir(source_folder):
            if filename.startswith(prefix):
                # Determine the new filename based on prefix removal setting
                new_filename = filename[len(prefix):] if remove_prefix_var.get() else filename
                src = os.path.join(source_folder, filename)
                dst = os.path.join(destination, new_filename)
                moved_path = safe_move(src, dst)
                if moved_path:
                    total_files_moved += 1
                    action_text = "removed prefix" if remove_prefix_var.get() else "kept prefix"
                    status_label.config(text=f"Moved {filename} to {moved_path} ({action_text})")
                else:
                    status_label.config(text=f"Failed to move {filename}")
    
    if total_files_moved > 0:
        # Save settings after successful moves
        save_settings()
        status_label.config(text=f"Moved {total_files_moved} files and saved settings")

def unique_path(path):
    """Return a unique file path if the file already exists."""
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter += 1
    return new_path


def safe_move(src, dst, retries=10, delay=0.5):
    """Try moving the file, retrying if it's not ready yet."""
    for i in range(retries):
        try:
            dst = unique_path(dst)  # avoid overwriting
            shutil.move(src, dst)
            return dst
        except (FileNotFoundError, PermissionError):
            time.sleep(delay)  # wait until the file is ready
    return None

prefix1 = "d_"



frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create main frame with dark theme
frame = tk.Frame(root, bg=COLORS['bg'])
frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

# Create source folder frame
source_frame = tk.Frame(frame, bg=COLORS['bg'])
source_frame.pack(fill=tk.X, pady=(0, 10))

source_label = tk.Label(source_frame, text="Source Folder:",
                     bg=COLORS['bg'], fg=COLORS['fg'])
source_label.pack(side=tk.LEFT, padx=5)

source_entry = tk.Entry(source_frame, width=50,
                     bg=COLORS['entry_bg'], fg=COLORS['entry_fg'],
                     insertbackground=COLORS['fg'])
source_entry.pack(side=tk.LEFT, padx=5)
source_entry.insert(0, DEFAULT_SOURCE_FOLDER)

# Create container for rows
rows_frame = tk.Frame(frame, bg=COLORS['bg'])
rows_frame.pack(fill=tk.BOTH, expand=True)

# List to store entry pairs
entry_pairs = []

def remove_row(row_frame, prefix_entry, path_entry):
    """Remove a row and its corresponding entries"""
    # Remove from entry_pairs list
    entry_pairs.remove((prefix_entry, path_entry))
    # Destroy the row frame and all its children
    row_frame.destroy()
    # Save settings after removal
    save_settings()
    # Don't allow removing the last row
    if not entry_pairs:
        add_row()

def add_row():
    """Add a new row of prefix and path entries"""
    row_frame = tk.Frame(rows_frame, bg=COLORS['bg'])
    row_frame.pack(fill=tk.X, pady=2)
    
    # Create prefix entry
    prefix_frame = tk.Frame(row_frame, bg=COLORS['bg'])
    prefix_frame.pack(side=tk.LEFT, padx=5)
    prefix_label = tk.Label(prefix_frame, text="Prefix:", 
                          bg=COLORS['bg'], fg=COLORS['fg'])
    prefix_label.pack()
    prefix_entry = tk.Entry(prefix_frame, width=30,
                          bg=COLORS['entry_bg'], fg=COLORS['entry_fg'],
                          insertbackground=COLORS['fg'])  # Cursor color
    prefix_entry.pack()
    
    # Create path entry
    path_frame = tk.Frame(row_frame, bg=COLORS['bg'])
    path_frame.pack(side=tk.LEFT, padx=5)
    path_label = tk.Label(path_frame, text="Path:",
                        bg=COLORS['bg'], fg=COLORS['fg'])
    path_label.pack()
    path_entry = tk.Entry(path_frame, width=30,
                        bg=COLORS['entry_bg'], fg=COLORS['entry_fg'],
                        insertbackground=COLORS['fg'])  # Cursor color
    path_entry.pack()
    
    # Create remove button
    remove_button = tk.Button(
        row_frame,
        text="✕",
        command=lambda: remove_row(row_frame, prefix_entry, path_entry),
        width=2,
        height=1,
        fg=COLORS['fg'],
        bg=COLORS['button_bg'],
        activebackground=COLORS['accent'],
        activeforeground=COLORS['fg'],
        bd=0,
        font=("Arial", 8, "bold")
    )
    remove_button.pack(side=tk.LEFT, padx=5, pady=15)  # Align with entry fields
    
    # Store the entries
    entry_pairs.append((prefix_entry, path_entry))
    
    return row_frame

def get_values():
    """Get all prefix and path pairs"""
    return [(prefix.get(), path.get()) 
            for prefix, path in entry_pairs 
            if prefix.get() and path.get()]

# Add initial row
add_row()

# Create status label
status_label = tk.Label(root, text="Ready to move files",
                       bg=COLORS['bg'], fg=COLORS['fg'])
status_label.config(font=("Arial", 10))
status_label.pack(pady=5)

# Create checkbox frame
checkbox_frame = tk.Frame(root, bg=COLORS['bg'])
checkbox_frame.pack(pady=5)

# Create checkbox for prefix removal
prefix_checkbox = tk.Checkbutton(
    checkbox_frame,
    text="Remove prefix when moving files",
    variable=remove_prefix_var,
    bg=COLORS['bg'],
    fg=COLORS['fg'],
    selectcolor=COLORS['checkbox_bg'],
    activebackground=COLORS['bg'],
    activeforeground=COLORS['fg']
)
prefix_checkbox.pack()

# Create button frame for multiple buttons
button_frame = tk.Frame(root, bg=COLORS['bg'])
button_frame.pack(padx=20, pady=10)

def create_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS['button_bg'],
        fg=COLORS['fg'],
        activebackground=COLORS['accent'],
        activeforeground=COLORS['fg'],
        anchor="center",
        bd=0,
        cursor="hand2",
        font=("Arial", 11),
        height=2,
        width=12,
        relief="flat"
    )

# Create the add row button
add_row_button = create_button(button_frame, "Add Row", add_row)
add_row_button.pack(side=tk.LEFT, padx=5)

# Create the move files button
move_button = create_button(button_frame, "Move Files", move_files)
move_button.pack(side=tk.LEFT, padx=5)

# Create the save settings button
save_button = create_button(button_frame, "Save Settings", save_settings)
save_button.pack(side=tk.LEFT, padx=5)

# Pack the main frame
frame.pack(padx=20, pady=20)

# Create watermark label
watermark = tk.Label(
    root,
    text="@namoviot",
    bg=COLORS['bg'],
    fg=COLORS['fg'],
    font=("Arial", 8, "italic")
)
# Configure the label to be semi-transparent and position it in the bottom-right
watermark.configure(fg='#808080')  # Using a gray color for subtlety
watermark.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=2)

# Try to load saved settings, or add initial row if no settings exist
if os.path.exists(SETTINGS_FILE):
    load_settings()
else:
    # Add initial empty row
    add_row()

# Start the GUI main loop
root.mainloop()
