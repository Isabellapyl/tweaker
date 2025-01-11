import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import os
import csv
import sys
import pygame

class LeaderboardApp:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("Player Management and Game Lobby")
        self.root.state("zoomed")  # Maximize the window
        self.all_players_file = "all_players.csv"  # File storing all players and their balances
        self.current_player_file = "player_balance.csv"  # File for the currently selected player

        # Initialize and play background music
        self.play_music()

        # Set up the user interface
        self.setup_ui()

    def play_music(self):
        # Play looping background music using Pygame
        pygame.mixer.init()
        pygame.mixer.music.load("jazz.wav")
        pygame.mixer.music.play(-1)

    def setup_ui(self):
        # Configure the main application window's appearance
        self.root.configure(bg="#870725")  # Set background color to rich red

        # Create a frame for buttons
        button_frame = tk.Frame(self.root, bg="#870725")
        button_frame.pack(expand=True)

        # Button styles
        button_style = {
            "fg": "black",  # Button text color
            "bg": "#daa520",  # Gold background
            "font": ("Baskerville", 12, "bold"),
            "activebackground": "#FFC107",  # Highlight color when button is clicked
            "activeforeground": "black",
        }

        # Create buttons with consistent dimensions and styles
        self.add_button = tk.Button(
            button_frame, text="Add Player", command=self.add_player,
            width=20, height=2, **button_style
        )
        self.add_button.pack(pady=10, padx=20, fill=tk.X)

        self.view_players_button = tk.Button(
            button_frame, text="View All Players", command=self.view_players,
            width=20, height=2, **button_style
        )
        self.view_players_button.pack(pady=10, padx=20, fill=tk.X)

        self.select_player_button = tk.Button(
            button_frame, text="Select Player", command=self.select_player,
            width=20, height=2, **button_style
        )
        self.select_player_button.pack(pady=10, padx=20, fill=tk.X)

        self.launch_lobby_button = tk.Button(
            button_frame, text="Launch Game Lobby", command=self.open_lobby,
            width=20, height=2, **button_style
        )
        self.launch_lobby_button.pack(pady=10, padx=20, fill=tk.X)

    def add_player(self):
        # Add a new player with a starting balance of $100
        name = simpledialog.askstring("Add Player", "Enter player's name:")
        if not name:
            return  # Exit if name is empty or input is canceled

        # Check if the player already exists
        if self.check_player_exists(name):
            messagebox.showinfo("Info", f"Player '{name}' already exists!")
            return

        # Save the new player to the all_players file
        balance = 100
        try:
            with open(self.all_players_file, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, balance])
            messagebox.showinfo("Success", f"Player '{name}' added with a starting balance of $100!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def check_player_exists(self, name):
        # Check if a player already exists in the all_players file
        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                return any(row[0] == name for row in reader)
        except FileNotFoundError:
            return False

    def view_players(self):
        # Display a list of all players and their balances
        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                players = "\n".join([f"{row[0]}: ${row[1]}" for row in reader])
                if players:
                    messagebox.showinfo("All Players", players)
                else:
                    messagebox.showinfo("All Players", "No players found.")
        except FileNotFoundError:
            messagebox.showinfo("All Players", "No players found.")

    def select_player(self):
        # Load a selected player into the current_player file
        name = simpledialog.askstring("Select Player", "Enter the name of the player to load:")
        if not name:
            return  # Exit if name is empty or input is canceled

        try:
            with open(self.all_players_file, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == name:
                        # Save selected player to the current_player file
                        with open(self.current_player_file, "w", newline="") as current_file:
                            writer = csv.writer(current_file)
                            writer.writerow([row[0], row[1]])
                        messagebox.showinfo("Player Selected", f"Player '{name}' loaded with a balance of ${row[1]}.")
                        return

            messagebox.showerror("Error", f"Player '{name}' not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No players found. Add a player first.")

    def open_lobby(self):
        # Launch the game lobby in a separate process
        lobby_script = r"C:\Users\Isabella.Pijl\learn\Casino Summative\gameplay.py"
        subprocess.Popen([sys.executable, lobby_script])

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = LeaderboardApp(root)
    root.mainloop()
