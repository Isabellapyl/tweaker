import os
import signal
import psutil
import pandas as pd
import tkinter as tk

# Define the file paths
file1_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"
file2_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\all_players.csv"
output_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\all_players.csv"

def terminate_negro():
    # Terminate gameplay.py process
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = process.info['cmdline']
            if cmdline and 'gameplay.py' in " ".join(cmdline):  # Match the full command line
                os.kill(process.info['pid'], signal.SIGTERM)  # Kill the process
                print("gameplay.py terminated.")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    else:
        print("gameplay.py is not running.")

    # Combine the CSV files
    try:
        # Read the contents of file1 and file2
        df1 = pd.read_csv(file1_path, header=None)  # Load file1 exactly as is, without assigning headers
        df2 = pd.read_csv(file2_path, header=None)  # Load file2 exactly as is, without assigning headers

        # Replace the last line of df2 with the contents of df1
        if not df2.empty:
            updated_df = pd.concat([df2.iloc[:-1], df1], ignore_index=True)  # Remove the last line and append df1
        else:
            updated_df = df1  # If df2 is empty, just use df1

        # Save the updated content back to the file2 path
        updated_df.to_csv(output_path, index=False, header=False)

        # Display the updated DataFrame for verification
        print("CSV files combined successfully:")
        print(updated_df)

    except FileNotFoundError as e:
        print(f"Error: {e}. Please check the file path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}.")

    # Close the GUI after execution
    root.destroy()

# Tkinter GUI setup
root = tk.Tk()
root.title("Log Out Controller")
root.geometry("200x100")

# Add "LOG OUT" button
logout_button = tk.Button(root, text="LOG OUT", command=terminate_negro)
logout_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
