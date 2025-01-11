import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import pygame
import csv

# Constants
FILE_PATH = "player_balance.csv"  # Path to the balance file
INIT_BALANCE = 50  # Default starting balance
ITEMS = ["CHERRY", "LEMON", "ORANGE", "PLUM", "BELL", "BAR"]  # Slot machine items

# Initialize pygame mixer for sound effects
pygame.mixer.init()
SPIN_SOUND = "slot_spin.wav"  # Spin sound effect file
JACKPOT_SOUND = "jackpot_alarm.wav"  # Jackpot sound effect file
pygame.mixer.music.load(SPIN_SOUND)
jackpot_sound = pygame.mixer.Sound(JACKPOT_SOUND)

# Load the player's balance and name from the file
def load_balance():
    try:
        with open(FILE_PATH, "r") as file:
            reader = csv.reader(file)
            row = next(reader)
            return row[0], int(row[1])
    except (FileNotFoundError, ValueError, StopIteration):
        return "Player", INIT_BALANCE

# Save the player's balance and name to the file
def save_balance(player_name, balance):
    with open(FILE_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([player_name, balance])

# Initialize game state
player_name, balance = load_balance()

# Create the main GUI window
root = tk.Tk()
root.title("Slot Machine Simulator")
root.configure(bg="black")

# Add a button to return to the lobby
back_to_lobby_button = tk.Button(
    root,
    text="Back to Lobby",
    command=root.destroy,
    bg="#1E90FF",
    fg="white",
    font=("Arial", 9),
    width=10
)
back_to_lobby_button.pack(anchor="nw", padx=10, pady=10)

# Load slot item images
IMAGES = {item: ImageTk.PhotoImage(Image.open(f"{item.lower()}.png").resize((100, 100))) for item in ITEMS}

# Spin the slot wheel and return a random item
def spin_wheel():
    return random.choices(ITEMS, weights=[35, 50, 10, 3, 2, 1])[0]

# Calculate the score based on the slot result
def calculate_score(first, second, third):
    if first == "CHERRY" and second != "CHERRY":
        return 1
    elif first == "CHERRY" and second == "CHERRY" and third != "CHERRY":
        return 3
    elif first == "CHERRY" and second == "CHERRY" and third == "CHERRY":
        return 5
    elif first == "ORANGE" and second == "ORANGE" and (third == "ORANGE" or third == "BAR"):
        return 10
    elif first == "PLUM" and second == "PLUM" and (third == "PLUM" or third == "BAR"):
        return 20
    elif first == "BELL" and second == "BELL" and (third == "BELL" or third == "BAR"):
        return 50
    elif first == "BAR" and second == "BAR" and third == "BAR":
        return 500
    else:
        return -1

# Display a popup for the jackpot
def show_jackpot_screen():
    jackpot_window = tk.Toplevel(root)
    jackpot_window.title("JACKPOT!!!")
    jackpot_window.geometry("400x300")
    jackpot_window.configure(bg="black")
    tk.Label(
        jackpot_window,
        text="🎉 JACKPOT! 🎉\nYou won $500!",
        font=("Arial", 24),
        bg="black",
        fg="#daa520"
    ).pack(pady=20)
    tk.Button(
        jackpot_window,
        text="Continue",
        command=jackpot_window.destroy,
        font=("Arial", 14),
        bg="green",
        fg="white"
    ).pack(pady=10)

# Play one round of the slot machine game
def play_game():
    global balance
    if balance <= 0:
        messagebox.showinfo("Game Over", "You are out of money!")
        return

    first, second, third = spin_wheel(), spin_wheel(), spin_wheel()
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
    save_balance(player_name, balance)

    if win > 0:
        result_label.config(text=f"You win ${win}!", fg="green")
        if win == 500:
            pygame.mixer.Sound.play(jackpot_sound)
            show_jackpot_screen()
    else:
        result_label.config(text="You lose!", fg="red")

# Display the rules of the game in a popup
def show_rules():
    rules = (
        "How to Play:\n\n"
        "- Press the Play button to spin the slots.\n"
        "- Each spin costs $1.\n\n"
        "Winning Combinations:\n"
        "- 1 CHERRY: +$1\n"
        "- 2 CHERRIES: +$3\n"
        "- 3 CHERRIES: +$5\n"
        "- 3 ORANGES or ORANGE + BAR: +$10\n"
        "- 3 PLUMS or PLUM + BAR: +$20\n"
        "- 3 BELLS or BELL + BAR: +$50\n"
        "- 3 BARS: +$500 (JACKPOT!)\n\n"
        "Good luck!"
    )
    messagebox.showinfo("How to Play", rules)

# Create the slot machine interface
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

# Add buttons to the main window
buttons_frame = tk.Frame(root, bg="black")
buttons_frame.pack(pady=20)
play_button = tk.Button(buttons_frame, text="Play", command=play_game, font=("Arial", 14), bg="green", fg="white")
play_button.grid(row=0, column=0, padx=10)
how_to_play_button = tk.Button(buttons_frame, text="?", command=show_rules, font=("Arial", 14), bg="#daa520", fg="white")
how_to_play_button.grid(row=0, column=8, padx=10)

# Start the main event loop
root.mainloop()
