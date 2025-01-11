import tkinter as tk
from pygame import mixer

# Initialize pygame mixer
mixer.init()

# Function to play the audio
def play_audio():
    mixer.music.load(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Shuffle2.wav")  # Use raw string for path
    mixer.music.play()

# Create the main tkinter window
root = tk.Tk()
root.title("Audio Player")

# Add a button to play the audio
play_button = tk.Button(root, text="Play Audio", command=play_audio)
play_button.pack(pady=20)

# Run the tkinter event loop
root.mainloop()
