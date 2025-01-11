import os
import signal
import psutil
import tkinter as tk

def terminate_negro():
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = process.info['cmdline']
            if cmdline and 'gameplay.py' in " ".join(cmdline):  # Match the full command line
                os.kill(process.info['pid'], signal.SIGTERM)  # Kill the process
                print("gameplay.py terminated.")
                root.destroy()  # Close the GUI after termination
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    print("gameplay.py is not running.")

# Tkinter GUI setup
root = tk.Tk()
root.title("Log Out Controller")
root.geometry("200x100")

# Add "LOG OUT" button
logout_button = tk.Button(root, text="LOG OUT", command=terminate_negro)
logout_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
