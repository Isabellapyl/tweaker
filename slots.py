import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import pygame
import csv

# Constants
FILE_PATH = "player_balance.csv"  # Update with the correct file path
INIT_BALANCE = 50
ITEMS = ["CHERRY", "LEMON", "ORANGE", "PLUM", "BELL", "BAR"]

# Initialize pygame mixer
pygame.mixer.init()

# Load sound effects
SPIN_SOUND = "slot_spin.wav"  # Replace with your spin sound file
JACKPOT_SOUND = "jackpot_alarm.wav"  # Replace with your jackpot sound file
pygame.mixer.music.load(SPIN_SOUND)
jackpot_sound = pygame.mixer.Sound(JACKPOT_SOUND)

# Load initial balance and player name from file
def load_balance():
    try:
        with open(FILE_PATH, "r") as file:
            reader = csv.reader(file)
            row = next(reader)
            return row[0], int(row[1])  # Return the player's name and balance
    except (FileNotFoundError, ValueError, StopIteration):
        return "Player", INIT_BALANCE  # Default values

# Save balance and player name to file
def save_balance(player_name, balance):
    with open(FILE_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([player_name, balance])  # Save the name and balance

# Game state
player_name, balance = load_balance()  # Load name and balance at start

# Create the GUI root window
root = tk.Tk()
root.title("Slot Machine Simulator")
root.configure(bg="black")

# Back to Lobby button in the top-left corner, above all elements
back_to_lobby_button = tk.Button(
    root,
    text="Back to Lobby",
    command=root.destroy,  # Close the game window
    bg="#1E90FF",  # Same blue color
    fg="white",
    font=("Arial", 9),
    width=10
)
back_to_lobby_button.pack(anchor="nw", padx=10, pady=10)  # Use `pack` to position it at the top-left corner


# Load images
IMAGES = {item: ImageTk.PhotoImage(Image.open(f"{item.lower()}.png").resize((100, 100))) for item in ITEMS}

def spin_wheel():
    """Returns a random item from the wheel with adjusted probabilities."""
    return random.choices(
        ITEMS,
        #ITEMS=["CHERRY", "LEMON", "ORANGE", "PLUM", "BELL", "BAR"]
        weights=[25, 64, 5, 3, 2, 1]  # probabilities
        )[0]

def calculate_score(first, second, third):
    """Calculates the winnings based on the slot combination."""
    if (first == "CHERRY") and (second != "CHERRY"):
        return 1
    elif (first == "CHERRY") and (second == "CHERRY") and (third != "CHERRY"):
        return 3
    elif (first == "CHERRY") and (second == "CHERRY") and (third == "CHERRY"):
        return 5
    elif (first == "ORANGE") and (second == "ORANGE") and ((third == "ORANGE") or (third == "BAR")):
        return 10
    elif (first == "PLUM") and (second == "PLUM") and ((third == "PLUM") or (third == "BAR")):
        return 20
    elif (first == "BELL") and (second == "BELL") and ((third == "BELL") or (third == "BAR")):
        return 50
    elif (first == "BAR") and (second == "BAR") and (third == "BAR"):
        return 500
    else:
        return -1

def show_jackpot_screen():
    """Displays a special jackpot screen."""
    jackpot_window = tk.Toplevel(root)
    jackpot_window.title("JACKPOT!!!")
    jackpot_window.geometry("400x300")
    jackpot_window.configure(bg="black")

    jackpot_label = tk.Label(
        jackpot_window,
        text="🎉 JACKPOT! 🎉\nYou won $500!",
        font=("Arial", 24),
        bg="black",
        fg="#daa520"
    )
    jackpot_label.pack(pady=20)

    close_button = tk.Button(
        jackpot_window,
        text="Continue",
        command=jackpot_window.destroy,
        font=("Arial", 14),
        bg="green",
        fg="white"
    )
    close_button.pack(pady=10)

def play_game():
    """Runs the slot machine for one round."""
    global balance
    if balance <= 0:
        messagebox.showinfo("Game Over", "You are out of money!")
        return

    # Spin the wheels
    first = spin_wheel()
    second = spin_wheel()
    third = spin_wheel()

    pygame.mixer.music.play(-1)

    for _ in range(10):
        wheel1_label.config(image=IMAGES[spin_wheel()])
        wheel2_label.config(image=IMAGES[spin_wheel()])
        wheel3_label.config(image=IMAGES[spin_wheel()])
        root.update()
        time.sleep(0.1)

    pygame.mixer.music.stop()

    wheel1_label.config(image=IMAGES[first])
    wheel2_label.config(image=IMAGES[second])
    wheel3_label.config(image=IMAGES[third])

    win = calculate_score(first, second, third)
    balance += win

    balance_label.config(text=f"Balance: ${balance}")
    save_balance(player_name, balance)  # Save updated balance

    if win > 0:
        result_label.config(text=f"You win ${win}!", fg="green")
        if win == 500:
            pygame.mixer.Sound.play(jackpot_sound)
            show_jackpot_screen()
    else:
        result_label.config(text="You lose!", fg="red")

def show_rules():
    rules = (
        "How to Play:\n\n"
        "Spin the Wheel:\n"
        "- Press the Play button.\n"
        "- Each spin costs $1.\n\n"
        "Winning & Losing:\n"
        "- The wheels stop on random items.\n"
        "- Winning combinations add money to your balance.\n"
        "- Losing spins deduct $1 from your balance.\n\n"
        "Winning Combinations:\n"
        "- 1 CHERRY (in left position): +$1\n"
        "- 2 CHERRIES (in left and middle postion): +$3\n"
        "- 3 CHERRIES: +$5\n"
        "- 3 ORANGES or ORANGE + BAR: +$10\n"
        "- 3 PLUMS or PLUM + BAR: +$20\n"
        "- 3 BELLS or BELL + BAR: +$50\n"
        "- 3 BARS: +$500 (🎉 JACKPOT!)\n\n"
        "Good luck! 🎰"
    )

    messagebox.showinfo("How to Play", rules)

# Create the slot frame
slot_frame = tk.Frame(root, bg="black", highlightbackground="gold", highlightthickness=5)
slot_frame.pack(pady=20)

header = tk.Label(slot_frame, text="🎰 Slot Machine 🎰", font=("Arial", 24), bg="black", fg="gold")
header.grid(row=0, column=0, columnspan=3)

balance_label = tk.Label(slot_frame, text=f"Balance: ${balance}", font=("Arial", 16), bg="black", fg="white")
balance_label.grid(row=1, column=0, columnspan=3)

wheel1_label = tk.Label(slot_frame, bg="black")
wheel1_label.grid(row=2, column=0, padx=10)
wheel2_label = tk.Label(slot_frame, bg="black")
wheel2_label.grid(row=2, column=1, padx=10)
wheel3_label = tk.Label(slot_frame, bg="black")
wheel3_label.grid(row=2, column=2, padx=10)

wheel1_label.config(image=IMAGES["CHERRY"])
wheel2_label.config(image=IMAGES["CHERRY"])
wheel3_label.config(image=IMAGES["CHERRY"])

result_label = tk.Label(slot_frame, text="", font=("Arial", 14), bg="black", fg="white")
result_label.grid(row=3, column=0, columnspan=3)

# Buttons Frame
buttons_frame = tk.Frame(root, bg="black")
buttons_frame.pack(pady=20)

# Play Button
play_button = tk.Button(buttons_frame, text="Play", command=play_game, font=("Arial", 14), bg="green", fg="white")
play_button.grid(row=0, column=0, padx=10)

# How to Play Button
how_to_play_button = tk.Button(
    buttons_frame,
    text="?",
    command=show_rules,
    font=("Arial", 14),
    bg="#daa520",
    fg="white"
)
how_to_play_button.grid(row=0, column=8, padx=10)

# Start the main loop
root.mainloop()
