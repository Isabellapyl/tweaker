import tkinter as tk
import math
import tkinter as tk
from tkinter import messagebox
import sys
import subprocess
import csv
from PIL import Image, ImageTk

from slots import load_balance

# File paths for balance and all players
balance_file_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"
all_players_file_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\all_players.csv"


class GameLobby:
    def __init__(self, root, canvas_size=500, player_radius=10, move_speed=5, interaction_distance=30):
        self.canvas_size = canvas_size
        self.player_radius = player_radius
        self.move_speed = move_speed
        self.interaction_distance = interaction_distance
        self.root = root
        self.player_pos = [50, 50]  # Initial player position
        self.game_positions = []
        self.game_scripts = {}  # Maps positions to game scripts
        self.keys_pressed = set()
        self.near_game = None
        self.current_direction = "right"  # Default direction
        self.is_moving = False  # Track whether the player is moving

        # Load and resize animation frames for right and left directions
        self.sprite_frames_right = [
            ImageTk.PhotoImage(Image.open(f"Walk ({i}).png").resize((50, 50)))
            for i in range(1, 13)
        ]
        self.sprite_frames_left = [
            ImageTk.PhotoImage(
                Image.open(f"Walk ({i}).png").resize((50, 50)).transpose(Image.FLIP_LEFT_RIGHT)
            )
            for i in range(1, 13)
        ]
        self.idle_frame = self.sprite_frames_right[0]  # Use the first frame as the idle frame
        self.sprite_frames = self.sprite_frames_right  # Default to right-facing sprites
        self.current_frame = 0

        with open(balance_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                me = row[0]  # Append the second item to the list
        self.current_player = me
        self.balance = self.load_balance()
        self.setup_ui()
        self.place_games_in_grid()
        self.update_canvas()
        self.bind_keys()
        self.animate_sprite()  # Start sprite animation
        self.animate_player()

    def load_balance(self):
        """Load the balance for the current player."""
        with open(balance_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                return int(row[1])  # Return balance if player found

    def logout(self):
        """Log out the current player and sync their balance with the all players file."""
        try:
            updated = False
            rows = []

            with open(all_players_file_path, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == self.current_player:
                        row[1] = str(self.balance)
                        updated = True
                    rows.append(row)

            if not updated:
                rows.append([self.current_player, self.balance])
            load_balance()
            with open(all_players_file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            with open(balance_file_path, "w", newline="") as file:
                pass

            messagebox.showinfo("Logout", f"{self.current_player}'s balance has been saved successfully!")
            self.root.destroy()
        except FileNotFoundError:
            messagebox.showerror("Error", "The players file was not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        # Load the background image
        self.bg_image = ImageTk.PhotoImage(
            Image.open("Casino_Background (2).png").resize((1200, 300)))

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)

        self.balance_label = tk.Label(self.info_frame, text=f"Balance: ${self.balance}", font=("Arial", 14))
        self.balance_label.pack(side=tk.LEFT, padx=10)

        self.logout_button = tk.Button(self.info_frame, text="Logout", command=self.logout, bg="red", fg="white")
        self.logout_button.pack(side=tk.LEFT, padx=10)

    def bind_keys(self):
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.enter_game)

    def key_press(self, event):
        self.keys_pressed.add(event.keysym)

    def key_release(self, event):
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)

    def place_games_in_grid(self):
        """Place game images in a 2x2 grid and map them to scripts."""
        margin = 50
        spacing = (self.canvas_size - 2 * margin) // 2

        # Define the images for each game position
        self.game_images = [  # Store as an instance variable
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Bonus Land.webp").resize((100, 200))),
            # top left
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Blacckjack_Icon3.webp").resize((100, 100))),
            # top right
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Poker_Icon.png").resize((200, 200))),
            # bottom left
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Roulette_Icon.png").resize((150, 150))),
            # bottom right
        ]

        # Define scripts for each game position
        scripts = [
            r"C:\Users\Isabella.Pijl\learn\Casino Summative\slots.py",
            r"C:\Users\Isabella.Pijl\learn\Casino Summative\blackjack.py",
            r"C:\Users\Isabella.Pijl\learn\Casino Summative\poker.py",
            r"C:\Users\Isabella.Pijl\learn\Casino Summative\roulette.py"
        ]

        idx = 0
        for row in range(2):
            for col in range(2):
                x = margin + col * spacing + spacing // 2
                y = margin + row * spacing + spacing // 2
                self.game_positions.append((x, y))
                self.game_scripts[(x, y)] = scripts[idx]
                self.canvas.create_image(x, y, image=self.game_images[idx])  # Draw the game image
                idx += 1

    def update_canvas(self):
        self.canvas.delete("all")

        # Draw the background image first
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Draw game images at their positions
        for idx, (x, y) in enumerate(self.game_positions):
            self.canvas.create_image(x, y, image=self.game_images[idx])  # Use stored images

        # Draw player sprite
        px, py = self.player_pos
        frame_to_draw = (
            self.sprite_frames[self.current_frame] if self.is_moving else self.idle_frame
        )
        self.canvas.create_image(px, py, image=frame_to_draw)

        # Draw "Press Space to Enter" text if near a game
        if self.near_game:
            self.canvas.create_text(
                self.canvas_size // 2, self.canvas_size - 20,
                text="Press Space to Enter", fill="red", font=("Arial", 16)
            )

    def animate_sprite(self):
        if self.is_moving:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
        self.root.after(100, self.animate_sprite)

    def move_player(self):
        """Move the player based on keys pressed."""
        dx, dy = 0, 0
        if "Up" in self.keys_pressed:
            dy -= self.move_speed
        if "Down" in self.keys_pressed:
            dy += self.move_speed
        if "Left" in self.keys_pressed:
            dx -= self.move_speed
            if self.current_direction != "left":
                self.current_direction = "left"
                self.sprite_frames = self.sprite_frames_left
        if "Right" in self.keys_pressed:
            dx += self.move_speed
            if self.current_direction != "right":
                self.current_direction = "right"
                self.sprite_frames = self.sprite_frames_right

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        # Ensure player stays within canvas bounds
        if self.player_radius <= new_x <= self.canvas_size - self.player_radius:
            self.player_pos[0] = new_x
        if self.player_radius <= new_y <= self.canvas_size - self.player_radius:
            self.player_pos[1] = new_y

        # Determine if the player is moving
        self.is_moving = dx != 0 or dy != 0

        # Check if near any game
        self.near_game = None
        for gx, gy in self.game_positions:
            if math.sqrt((self.player_pos[0] - gx) ** 2 + (self.player_pos[1] - gy) ** 2) <= self.interaction_distance:
                self.near_game = (gx, gy)
                break

    def animate_player(self):
        self.move_player()
        self.update_canvas()
        self.root.after(16, self.animate_player)

    def enter_game(self, event=None):
        if self.near_game and self.near_game in self.game_scripts:
            script_path = self.game_scripts[self.near_game]
            try:
                subprocess.Popen(
                    [sys.executable, script_path],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                print(f"Error occurred while launching the game: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game Lobby")
    lobby = GameLobby(root)
    root.geometry("1400x600")  # Set initial window size to 800x600
    root.mainloop()
