import tkinter as tk
import math
import sys
import subprocess
import csv
from PIL import Image, ImageTk

FILE_PATH = "player_balance.csv"  # Update with the correct file path
INIT_BALANCE = 50
def load_balance():
    try:
        with open(FILE_PATH, "r") as file:
            reader = csv.reader(file)
            return int(next(reader)[1])
    except (FileNotFoundError, ValueError, StopIteration):
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

        # Define hitboxes for precise collision detection
        self.hitboxes = [
            (50, 50, 150, 150),  # Adjusted slot machines area
            (200, 200, 300, 300),  # Adjusted blackjack table
            (400, 100, 500, 200),  # Adjusted bar counter
            (600, 150, 700, 250),  # Adjusted poker table
            (200, 400, 300, 500),  # Adjusted roulette table
            (400, 350, 550, 450),  # Adjusted blackjack table bottom center
            (960, 350, 1160, 450),  # Adjusted poker table bottom right
        ]

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
        # Make the Canvas fill the entire window
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load the background image
        bg_image = Image.open("Casino_Background (2).png")
        self.bg_image = ImageTk.PhotoImage(bg_image)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)

        self.balance_label = tk.Label(self.info_frame, text=f"Balance: ${self.balance}", font=("Arial", 14))
        self.balance_label.pack(side=tk.LEFT, padx=10)

        self.logout_button = tk.Button(self.info_frame, text="Logout", command=self.logout, bg="red", fg="white")
        self.logout_button.pack(side=tk.LEFT, padx=10)

        # Bind resize event to update the canvas
        self.root.bind("<Configure>", self.update_canvas_on_resize)

    def update_canvas_on_resize(self, event):
        """Update the background image and elements when the window resizes."""
        # Resize the background image to match the new canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        resized_bg = Image.open("Casino_Background (2).png").resize((canvas_width, canvas_height))
        self.bg_image = ImageTk.PhotoImage(resized_bg)

        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")

        # Draw the resized background image
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Draw hitboxes (for debugging, optional)
        for x1, y1, x2, y2 in self.hitboxes:
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)

        # Draw game images at their positions
        for idx, (x, y) in enumerate(self.game_positions):
            self.canvas.create_image(x, y, image=self.game_images[idx])

        # Draw player sprite
        px, py = self.player_pos
        frame_to_draw = self.sprite_frames[self.current_frame] if self.is_moving else self.idle_frame
        self.canvas.create_image(px, py, image=frame_to_draw)

        # Draw "Press Space to Enter" text if near a game
        if self.near_game:
            self.canvas.create_text(
                self.canvas_size // 2, self.canvas_size - 20,
                text="Press Space to Enter", fill="red", font=("Arial", 16)
            )

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
        self.game_images = [
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Bonus Land.webp").resize((100, 200))),
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Blacckjack_Icon3.webp").resize((100, 100))),
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Poker_Icon.png").resize((200, 200))),
            ImageTk.PhotoImage(
                Image.open(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Roulette_Icon.png").resize((150, 150))),
        ]

    def animate_sprite(self):
        if self.is_moving:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
        self.root.after(100, self.animate_sprite)

    def check_collision(self, x, y):
        """Check if the player's position collides with any hitbox."""
        for x1, y1, x2, y2 in self.hitboxes:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True
        return False

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

        # Keep player within the canvas bounds and check collisions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if self.player_radius <= new_x <= canvas_width - self.player_radius and not self.check_collision(new_x, self.player_pos[1]):
            self.player_pos[0] = new_x
        if self.player_radius <= new_y <= canvas_height - self.player_radius and not self.check_collision(self.player_pos[0], new_y):
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
