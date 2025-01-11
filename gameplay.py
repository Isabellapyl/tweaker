import tkinter as tk
import math
import sys
import subprocess
import csv
from PIL import Image, ImageTk

FILE_PATH = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"  # Update with the correct file path
INIT_BALANCE = 505

def load_balance():
    try:
        with open(FILE_PATH, "r") as file:
            reader = csv.reader(file)
            return float(next(reader)[1])
    except (FileNotFoundError, ValueError, StopIteration):
        print("Error: Invalid data in the balance file")
        return INIT_BALANCE


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
        self.is_moving = False  # Track whether the player is moving
        self.player_pos = [50, 50]  # Initial player position
        self.keys_pressed = set()
        self.near_game = None

        # Hitboxes and game scripts
        self.hitboxes = [
            (160, 0, 220, 100),  # Slot machine left
            (220, 0, 280, 100),  # Slot machine middle
            (280, 0, 340, 100),  # Slot machine right
            (225, 130, 400, 220),  # Blackjack table left
            (880, 130, 1060, 220),  # Blackjack table right
            (460, 365, 560, 490),  # Poker table left
            (720, 365, 825, 490),  # Poker table right
            (115, 350, 320, 440),  # Roulette table left
            (960, 355, 1170, 450),  # Roulette table right
            (460, 365, 560, 490),  # Poker table
            (540, 120, 740, 210),  # Log Out
        ]
        self.game_scripts = {
            (160, 0, 220, 100): r"C:\Users\Isabella.Pijl\learn\Casino Summative\slots.py",  # Slot machine left
            (220, 0, 280, 100): r"C:\Users\Isabella.Pijl\learn\Casino Summative\slots.py",  # Slot machine middle
            (280, 0, 340, 100): r"C:\Users\Isabella.Pijl\learn\Casino Summative\slots.py",  # Slot machine right
            (225, 130, 400, 220): r"C:\Users\Isabella.Pijl\learn\Casino Summative\blackjack.py",  # Blackjack table left
            (880, 130, 1060, 220): r"C:\Users\Isabella.Pijl\learn\Casino Summative\blackjack.py",
            # Blackjack table right
            (460, 365, 560, 490): r"C:\Users\Isabella.Pijl\learn\Casino Summative\higher or lower.py",  # Poker table left
            (720, 365, 825, 490): r"C:\Users\Isabella.Pijl\learn\Casino Summative\higher or lower.py",  # Poker table right
            (115, 350, 320, 440): r"C:\Users\Isabella.Pijl\learn\Casino Summative\roulette.py",  # Roulette table left
            (960, 355, 1170, 450): r"C:\Users\Isabella.Pijl\learn\Casino Summative\roulette.py",  # Roulette table right
            (460, 365, 560, 490): r"C:\Users\Isabella.Pijl\learn\Casino Summative\higher or lower.py",  # Poker table
            (540, 120, 740, 210): r"C:\Users\Isabella.Pijl\learn\Casino Summative\Log Out.py",  # Log Out
        }

        self.blocking_hitboxes = [
            (170, 0, 210, 90),  # Slot machine left
            (230, 0, 270, 90),  # Slot machine middle
            (290, 0, 330, 90),  # Slot machine right
            (235, 135, 390, 210),  # Blackjack table left
            (890, 135, 1050, 210),  # Blackjack table right
            (470, 370, 550, 480),  # Poker table left
            (730, 370, 815, 480),  # Poker table right
            (125, 355, 310, 430),  # Roulette table left
            (970, 360, 1160, 440),  # Roulette table right
            (120, 215, 160, 315),  # poll left
            (460, 215, 505, 315),  # poll middle left
            (780, 215, 820, 315),  # poll middle right
            (1120, 215, 1165, 315),  # poll right
            (470, 370, 550, 480),  # Poker table
            (550, 125, 730, 200),  # Log Out
        ]

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

        self.setup_ui()
        self.update_canvas()
        self.bind_keys()
        self.animate_sprite()
        self.animate_player()

    def resize_background(self):
        """Resize the background image to match the canvas size."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        resized_bg = Image.open("Casino_Background (2).png").resize((canvas_width, canvas_height))
        self.bg_image = ImageTk.PhotoImage(resized_bg)
        self.update_canvas()

    def setup_ui(self):
        self.root.bind("<Configure>", lambda event: self.resize_background())

        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load the background image
        bg_image = Image.open("Casino_Background (2).png")
        self.bg_image = ImageTk.PhotoImage(bg_image)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)

        self.balance_label = tk.Label(self.info_frame, text=f"Balance: $50", font=("Arial", 14))
        self.balance_label.pack(side=tk.LEFT, padx=10)

        # Start periodic balance updates
        self.update_balance()

    def update_canvas(self):
        self.canvas.delete("all")

        # Draw the background image
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Draw the player sprite
        px, py = self.player_pos
        frame_to_draw = self.sprite_frames[self.current_frame] if self.is_moving else self.idle_frame
        self.canvas.create_image(px, py, image=frame_to_draw)

        # Draw "Press Space to Enter" text if near a game
        if self.near_game:
            self.canvas.create_text(
                self.canvas_size // 2, self.canvas_size - 0,
                text="Press Space to Enter", fill="#daa520", font=("Arial", 20)
            )

    def check_blocking_collision(self, x, y):
        """Check if the player's position collides with any blocking hitbox."""
        for x1, y1, x2, y2 in self.blocking_hitboxes:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True
        return False

    def bind_keys(self):
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.enter_game)

    def key_press(self, event):
        self.keys_pressed.add(event.keysym)

    def key_release(self, event):
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)

    def move_player(self):
        """Move the player based on keys pressed."""
        dx, dy = 0, 0
        if "Up" in self.keys_pressed:
            dy -= self.move_speed
        if "Down" in self.keys_pressed:
            dy += self.move_speed
        if "Left" in self.keys_pressed:
            dx -= self.move_speed
            if self.sprite_frames != self.sprite_frames_left:
                self.sprite_frames = self.sprite_frames_left
        if "Right" in self.keys_pressed:
            dx += self.move_speed
            if self.sprite_frames != self.sprite_frames_right:
                self.sprite_frames = self.sprite_frames_right

        # Use actual canvas dimensions for boundaries
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        # Check collisions with canvas boundaries and blocking hitboxes
        if (
                self.player_radius <= new_x <= canvas_width - self.player_radius
                and not self.check_blocking_collision(new_x, self.player_pos[1])
        ):
            self.player_pos[0] = new_x
        if (
                self.player_radius <= new_y <= canvas_height - self.player_radius
                and not self.check_blocking_collision(self.player_pos[0], new_y)
        ):
            self.player_pos[1] = new_y

        self.is_moving = dx != 0 or dy != 0

        # Check if near any game
        self.near_game = None
        for x1, y1, x2, y2 in self.hitboxes:
            if x1 <= self.player_pos[0] <= x2 and y1 <= self.player_pos[1] <= y2:
                self.near_game = (x1, y1, x2, y2)
                break

    def animate_sprite(self):
        if self.is_moving:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
        self.root.after(100, self.animate_sprite)

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

    def update_balance(self):
        """Update the balance label every second."""
        balance = load_balance()
        self.balance_label.config(text=f"Balance: ${balance}")
        self.root.after(1000, self.update_balance)  # Schedule this method to run again after 1 second


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game Lobby")
    lobby = GameLobby(root)
    root.geometry("1400x600")
    root.mainloop()