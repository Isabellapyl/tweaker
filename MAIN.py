import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import os
import csv
import sys
import pygame

class LeaderboardApp:
    def __init__(self, root):
        # Initialize the main application window and setup
        self.root = root
        self.root.title("Player Management and Game Lobby")
        self.root.state("zoomed")  # Start maximized for better visibility
        self.all_players_file = "all_players.csv"  # File storing all player data
        self.current_player_file = "player_balance.csv"  # File for the active player

        self.play_music()  # Start background music
        self.setup_ui()  # Build the user interface

    def play_music(self):
        # Set up and loop background music
        pygame.mixer.init()
        pygame.mixer.music.load("jazz.wav")
        pygame.mixer.music.play(-1)  # Loop indefinitely

    def setup_ui(self):
        # Configure main window layout and button styles
        self.root.configure(bg="#870725")  # Set background color to deep red

        # Create a frame to hold all buttons
        button_frame = tk.Frame(self.root, bg="#870725")
        button_frame.pack(expand=True)

        # Button appearance settings
        button_style = {
            "fg": "black",
            "bg": "#daa520",  # Gold-colored button
            "font": ("Baskerville", 12, "bold"),
            "activebackground": "#FFC107",  # Highlight color
            "activeforeground": "black",
        }

        # Add "Add Player" button
        self.add_button = tk.Button(
            button_frame, text="Add Player", command=self.add_player,
            width=20, height=2, **button_style
        )
        self.add_button.pack(pady=10, padx=20, fill=tk.X)

        # Add "View All Players" button
        self.view_players_button = tk.Button(
            button_frame, text="View All Players", command=self.view_players,
            width=20, height=2, **button_style
        )
        self.view_players_button.pack(pady=10, padx=20, fill=tk.X)

        # Add "Select Player" button
        self.select_player_button = tk.Button(
            button_frame, text="Select Player", command=self.select_player,
            width=20, height=2, **button_style
        )
        self.select_player_button.pack(pady=10, padx=20, fill=tk.X)

        # Add "Launch Game Lobby" button
        self.launch_lobby_button = tk.Button(
            button_frame, text="Launch Game Lobby", command=self.open_lobby,
            width=20, height=2, **button_style
        )
        self.launch_lobby_button.pack(pady=10, padx=20, fill=tk.X)

    def add_player(self):
        # Prompt user to input a new player's name
        name = simpledialog.askstring("Add Player", "Enter player's name:")
        if not name:  # Exit if no input is provided
            return

        # Ensure the player doesn't already exist
        if self.check_player_exists(name):
            messagebox.showinfo("Info", f"Player '{name}' already exists!")
            return

        # Add the player with a default balance of $100
        balance = 100
        try:
            with open(self.all_players_file, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, balance])
            messagebox.showinfo("Success", f"Player '{name}' added with a $100 balance.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add player: {e}")

    def check_player_exists(self, name):
        # Check if a player is already listed in the all_players file
        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                return any(row[0] == name for row in reader)
        except FileNotFoundError:
            return False  # No players if the file doesn't exist

    def view_players(self):
        # Display all players and their balances in a message box
        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                players = "\n".join([f"{row[0]}: ${row[1]}" for row in reader])
                if players:
                    messagebox.showinfo("All Players", players)
                else:
                    messagebox.showinfo("All Players", "No players found.")
        except FileNotFoundError:
            messagebox.showinfo("All Players", "No players found. Add some first!")

    def select_player(self):
        # Allow user to choose an active player
        name = simpledialog.askstring("Select Player", "Enter the player's name:")
        if not name:  # Exit if no input is provided
            return

        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == name:  # Match found
                        with open(self.current_player_file, "w", newline="") as current_file:
                            writer = csv.writer(current_file)
                            writer.writerow([row[0], row[1]])  # Save to active player file
                        messagebox.showinfo("Player Selected", f"Player '{name}' loaded with ${row[1]}.")
                        return
            messagebox.showerror("Error", f"Player '{name}' not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No players found. Add some first.")

    def open_lobby(self):
        # Launch the game lobby script in a new process
        lobby_script = r"C:\Users\Isabella.Pijl\learn\Casino Summative\gameplay.py"
        subprocess.Popen([sys.executable, lobby_script])

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = LeaderboardApp(root)
    root.mainloop()
