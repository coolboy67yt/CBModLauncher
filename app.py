import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import subprocess

def get_folders_in_directory(directory):
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    return folders

def save_last_selected_folder(last_selected_folder):
    config = configparser.ConfigParser()
    config['Settings'] = {'LastSelectedFolder': last_selected_folder}
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def load_last_selected_folder():
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        return config.get('Settings', 'LastSelectedFolder', fallback=None)
    return None

def create_versions_ini(mod_group_path):
    versions_ini_path = os.path.join(mod_group_path, "versions.ini")
    if not os.path.exists(versions_ini_path):
        with open(versions_ini_path, 'w') as versions_file:
            versions_file.write("[Versions]")

def save_version(mod_group_path, folder, version):
    versions_ini_path = os.path.join(mod_group_path, "versions.ini")
    config = configparser.ConfigParser()
    config.read(versions_ini_path)

    if 'Versions' not in config:
        config['Versions'] = {}

    config['Versions'][folder] = version

    with open(versions_ini_path, 'w') as versions_file:
        config.write(versions_file)

def get_version(mod_group_path, folder):
    versions_ini_path = os.path.join(mod_group_path, "versions.ini")
    config = configparser.ConfigParser()
    config.read(versions_ini_path)

    if 'Versions' in config and folder in config['Versions']:
        return config['Versions'][folder]
    return None

def on_folder_selected(event):
    selected_folder = folder_var.get()

    # Check if there is a last selected folder
    last_selected_folder = load_last_selected_folder()
    if last_selected_folder:
        move_contents_to_original(last_selected_folder)

    # Move the contents of the selected folder to %appdata%/.minecraft/mods
    move_contents_to_mods(mod_group_path, selected_folder)

    # Save the current selected folder
    save_last_selected_folder(selected_folder)

    # Show version under the "Start" button
    version = get_version(mod_group_path, selected_folder)
    version_label.config(text=f"Version: {version}")

    messagebox.showinfo("Move Complete", f"Contents of {selected_folder} moved to '%appdata%/.minecraft/mods' folder.")

def move_contents_to_mods(mod_group_path, selected_folder):
    source_path = os.path.join(mod_group_path, selected_folder)
    destination_path = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")

    # Create the 'mods' folder if it doesn't exist
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Move the contents of the selected folder to %appdata%/.minecraft/mods
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            shutil.move(item_path, destination_path)

    # Save the version information
    version = get_version(mod_group_path, selected_folder)
    save_version(mod_group_path, selected_folder, version)

def move_contents_to_original(original_folder):
    source_path = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")
    destination_path = os.path.join(mod_group_path, original_folder)

    # Move the contents of %appdata%/.minecraft/mods back to the original folder
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            shutil.move(item_path, destination_path)

def start_game_ink():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    game_ink_path = os.path.join(script_directory, "Game.Ink")

    if os.path.exists(game_ink_path):
        subprocess.run(["notepad.exe", game_ink_path], cwd=script_directory)
    else:
        messagebox.showerror("File Not Found", "The 'Game.Ink' file was not found in the script's directory.")

def start_minecraft(minecraft_launcher_path):
    if os.path.exists(minecraft_launcher_path):
        subprocess.run([minecraft_launcher_path])
    else:
        messagebox.showerror("File Not Found", "Minecraft Launcher not found at the specified path.")

# Read the configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Get paths with environment variable expansion
minecraft_launcher_path = config['Paths']['MinecraftLauncher']
mod_group_path = os.path.expandvars(config['Paths']['ModGroup'])
mods_folder_path = os.path.expandvars(config['Paths']['ModsFolder'])

# Create the main window
root = tk.Tk()
root.title("CBMods")
root.geometry("400x200")  # Set window size
root.iconbitmap("mc.ico")  # Set window icon

# Set background color
root.configure(bg='#343541')

# Get the list of folders in the specified directory
folders = get_folders_in_directory(mod_group_path)

# Check if the list of folders is empty
if not folders:
    messagebox.showinfo("No Folders Found", "No folders found in the 'modGroup' directory.")
    root.destroy()  # Close the window
    exit()

# Create a variable to store the selected folder and load the last selected folder
folder_var = tk.StringVar(root)
last_selected_folder = load_last_selected_folder()

# Set the default value if the list is not empty
folder_var.set(last_selected_folder) if last_selected_folder and last_selected_folder in folders else folders[0]

# Create a label and dropdown for folder selection
label = tk.Label(root, text="Select a modpack:", bg='#343541', fg='white')
label.pack(pady=10)

folder_dropdown = ttk.Combobox(root, textvariable=folder_var, values=folders)
folder_dropdown.pack(pady=10)
folder_dropdown.bind("<<ComboboxSelected>>", on_folder_selected)

# Create a "Start" button with updated styling
start_button = tk.Button(root, text="Start", command=lambda: [start_minecraft(minecraft_launcher_path), root.destroy()],
                         bg='#343541', fg='white', relief=tk.GROOVE, font=('Arial', 12))
start_button.pack(pady=10)

# Create a label to display the version
version_label = tk.Label(root, text="", bg='#343541', fg='white')
version_label.pack(pady=10)

# Ensure versions.ini is created
create_versions_ini(mod_group_path)

# Show version for initially selected folder
initial_version = get_version(mod_group_path, folder_var.get())
version_label.config(text=f"Version: {initial_version}")

# Run the main loop
root.mainloop()
