import tkinter as tk
import subprocess
import os
from pathlib import Path
from tkinter import messagebox

window = tk.Tk()
window.title("OpenNAS Manager")
window.geometry("1200x800")

NAS_ROOT = Path("/mnt/nas")
current_dir = NAS_ROOT

try:
    used_bytes = int(subprocess.run(['df', '-B1', '--output=used', str(NAS_ROOT)], capture_output=True, text=True).stdout.splitlines()[1])
    total_bytes = int(subprocess.run(['df', '-B1', '--output=size', str(NAS_ROOT)], capture_output=True, text=True).stdout.splitlines()[1])
    usedstorage = round(used_bytes / (1024 ** 3), 2)
    totalstorage = round(total_bytes / (1024 ** 3), 2)
    perstorage = round((used_bytes / total_bytes) * 100, 1)
except Exception:
    usedstorage = 0.0
    totalstorage = 0.0
    perstorage = 0.0

oss = subprocess.run(['cat', '/etc/os-release'], stdout=subprocess.PIPE, text=True).stdout
mount = bool(os.path.ismount(NAS_ROOT))

# UI Labels
osp = tk.Label(window, text=f"OS: {oss[13:31]}", font=("Roboto", 12))
osp.place(x=10, y=0)

mountp = tk.Label(window, text=f"Mount Status: {mount}", font=("Roboto", 12))
mountp.place(x=10, y=30)

path_label = tk.Label(window, text=f"Path: {current_dir}", font=("Roboto", 11, "bold"))
path_label.place(x=10, y=60)

listdirbox = tk.Listbox(window, width=145, height=30)
listdirbox.place(x=10, y=90)

def load_dir(target_path):
    global current_dir
    current_dir = target_path
    path_label.config(text=f"Path: {current_dir}")
    listdirbox.delete(0, tk.END)

    if not mount:
        listdirbox.insert(tk.END, "NAS is not mounted. Check your connection or fstab.")
        return

    if current_dir != NAS_ROOT:
        listdirbox.insert(tk.END, "..")

    try:
        items = sorted(os.listdir(current_dir))
        if not items and current_dir == NAS_ROOT:
            listdirbox.insert(tk.END, "Folder is empty")
        else:
            for item in items:
                listdirbox.insert(tk.END, item)
    except PermissionError:
        listdirbox.insert(tk.END, "Permission denied.")
    except Exception as e:
        listdirbox.insert(tk.END, f"Error: {e}")

def select(event=None):
    selected = listdirbox.curselection()
    if not (selected and mount):
        return

    choice = listdirbox.get(selected[0])

    if choice == "..":
        load_dir(current_dir.parent)
        return

    full_path = current_dir / choice

    if full_path.exists():
        if full_path.is_file():
            subprocess.Popen(["xdg-open", str(full_path)])
        elif full_path.is_dir():
            load_dir(full_path)

def download(event=None):
    selected = listdirbox.curselection()
    if not (selected and mount):
        return

    choice = listdirbox.get(selected[0])

    if choice == "..":
        load_dir(current_dir.parent)
        return

    full_path = current_dir / choice

    

    if full_path.exists():
        destination = os.path.expanduser("~/Downloads")
        if full_path.is_file():
            subprocess.Popen(["cp", str(full_path), destination])
        elif full_path.is_dir():
            subprocess.Popen(["cp", "-r", str(full_path), destination])

        messagebox.showinfo("OpenNAS Manager Notification", "Successfully downloaded your file (in Downloads folder)")

listdirbox.bind("<Double-1>", select)

openfile = tk.Button(window, text="Open", command=select)
openfile.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

openfile = tk.Button(window, text="Download", command=download)
openfile.place(relx=1.0, rely=1.0, anchor="se", x=-100, y=-10)

storagep = tk.Label(window, text=f"Used: {round(usedstorage, 0)} GB / {round(totalstorage, 0)} GB ({round(perstorage, 0)}%)", font=("Roboto", 12))
storagep.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)



load_dir(NAS_ROOT)

window.mainloop()
