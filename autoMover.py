import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygame
import tkinter as tk

root = tk.Tk()


(width, height) = (300, 200)
#screen = pygame.display.set_mode((width, height))
#pygame.display.flip()

# Define your prefix → destination mapping
ROUTES = {
    "d_": r"X:\desti",
    "car_": r"C:\props\vehicles",
    "env_": r"C:\props\environment"
}

SOURCE_FOLDER = r"X:\temp"


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

T = tk.Text(root, height = 5, width = 52)

# Create label
l = tk.Label(root, text = "Fact of the Day")
l.config(font =("Courier", 14))

def buttonClicked():
    print("button clikcedsd")
button = tk.Button(
    root,
    text = "click me",
    command=buttonClicked,
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   font=("Arial", 12),
                   height=2,
                   highlightbackground="black",
                   highlightcolor="green",
                   highlightthickness=2,
                   justify="center",
                   overrelief="raised",
                   padx=10,
                   pady=5,
                   width=15,
                   wraplength=100

)


class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        file_name = os.path.basename(file_path)

        for prefix, destination in ROUTES.items():
            if file_name.startswith(prefix):
                os.makedirs(destination, exist_ok=True)
                # Remove the prefix from the filename for the destination
                new_file_name = file_name[len(prefix):]
                target_path = os.path.join(destination, new_file_name)
                moved_path = safe_move(file_path, target_path)

                if moved_path:
                    print(f"Moved {file_name} → {moved_path}")
                else:
                    print(f"⚠ Failed to move {file_name}")
                break


running = True

if __name__ == "__main__":
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, SOURCE_FOLDER, recursive=False)
    observer.start()
    print("Watching folder:", SOURCE_FOLDER)
    button.pack(padx=20,pady=20)
    T.pack()
    T.insert(tk.END,prefix1)
    root.mainloop()

    #observer.stop()
    observer.join()