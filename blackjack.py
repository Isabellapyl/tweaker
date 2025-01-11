import tkinter as tk
from tkinter import messagebox
import random
import csv
from PIL import Image, ImageTk
from pygame import mixer
import time
# Initialize pygame mixer
mixer.init()

# File path to the player balance data
file_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"


# Load the player's balance from the CSV file
with open(file_path, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        BAL = row[1]   # Retrieve the balance (second column of the CSV)

# Class to manage the entire Blackjack game
class BlackjackGame:
    def __init__(self, root):
        # Initialize the main game window
        self.root = root
        self.root.title("Blackjack")
        self.root.geometry("500x700")  # Set window dimensions
        self.root.configure(bg="green")  # Set a casino-themed green background

        # Initialize game state variables
        self.balance = int(BAL)  # Starting balance
        self.current_bet = 0

        # Create the deck and card images
        self.deck = self.create_deck()
        self.card_images = self.load_card_images()
        # Hands for player and dealer
        self.player_hand = []
        self.dealer_hand = []

        # Add GUI elements to display game state and controls
        self.info_label = tk.Label(root, text="Welcome to Blackjack!", font=("Helvetica", 14), bg="green", fg="white")
        self.info_label.pack(pady=10)

        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance}", font=("Helvetica", 12), bg="green", fg="white")
        self.balance_label.pack(pady=5)

        # Add an instructions button for new players
        self.instruction_button = tk.Button(root, text="?", command=self.show_instructions, bg="black", fg="white", font=("Helvetica", 14), width=2)
        self.instruction_button.place(relx=0.9, rely=0.02, anchor="ne")

        # Bet frame allows players to input and confirm their bet
        self.bet_frame = tk.Frame(root, bg="green")
        self.bet_frame.pack(pady=10)

        # Input field for bets
        self.bet_entry = tk.Entry(self.bet_frame, width=10, validate="key")
        validate_command = (self.root.register(self.validate_numeric_input), "%P")
        self.bet_entry.configure(validatecommand=validate_command)
        self.bet_entry.pack(side=tk.LEFT, padx=5)

        # Button to confirm the bet, plays audio and starts the game
        self.bet_button = tk.Button(
            self.bet_frame,
            text="Place Bet",
            command=self.place_bet_with_audio,  # Use the wrapper function
            bg="black",
            fg="white"
        )
        self.bet_button.pack(side=tk.LEFT, padx=5)

        # Containers for displaying player and dealer hands
        self.player_container = tk.Frame(root, bg="green")
        self.player_label = tk.Label(self.player_container, text="Your Hand:", font=("Helvetica", 12), bg="green", fg="white")
        self.player_label.pack(anchor="w")
        self.player_frame = tk.Frame(self.player_container, bg="green")
        self.player_frame.pack(anchor="w")

        self.dealer_container = tk.Frame(root, bg="green")
        self.dealer_label = tk.Label(self.dealer_container, text="Dealer's Hand:", font=("Helvetica", 12), bg="green", fg="white")
        self.dealer_label.pack(anchor="w")
        self.dealer_frame = tk.Frame(self.dealer_container, bg="green")
        self.dealer_frame.pack(anchor="w")

        # Add action buttons for gameplay: Hit and Stand
        self.button_frame = tk.Frame(root, bg="green")
        self.button_frame.pack(pady=10)

        self.hit_button = tk.Button(self.button_frame, text="Hit", command=self.hit, bg="black", fg="white", state=tk.DISABLED)
        self.hit_button.pack(side=tk.LEFT, padx=20)

        self.stand_button = tk.Button(self.button_frame, text="Stand", command=self.stand, bg="black", fg="white", state=tk.DISABLED)
        self.stand_button.pack(side=tk.LEFT, padx=20)

        # Back to Lobby button for exiting the game
        self.lobby_button = tk.Button(
            root,
            text="Back to Lobby",
            command=self.back_to_lobby,
            bg="red",
            fg="white",
            font=("Helvetica", 12),
        )
        self.lobby_button.place(x=10, y=10)  # Place in the top-left corner

        # Keyboard bindings for quick access to betting and actions
        self.root.bind("<Return>", lambda event: self.place_bet_key())
        self.root.bind("h", self.hit_key)
        self.root.bind("s", self.stand_key)

    # Function to play the audio and place bet
    def place_bet_with_audio(self):
        play_audio()  # Call the audio function
        self.place_bet()  # Call the existing place_bet function

    def create_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [f"{rank} of {suit}" for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def load_card_images(self):
        card_images = {}
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        for suit in suits:
            for rank in ranks:
                card_name = f"{rank} of {suit}"
                image_path = f"C:/Users/Isabella.Pijl/learn/Casino Summative/Playing Cards/Playing Cards/PNG-cards-1.3/{rank}_of_{suit}.png"
                image = Image.open(image_path).resize((100, 145))  # Resize images for uniform dimensions
                card_images[card_name] = ImageTk.PhotoImage(image)
        return card_images

    def card_value(self, card):
        rank = card.split()[0]
        if rank in ['Jack', 'Queen', 'King']:
            return 10
        elif rank == 'Ace':
            return 11
        else:
            return int(rank)

    def hand_value(self, hand):
        value = sum(self.card_value(card) for card in hand)
        aces = sum(1 for card in hand if 'Ace' in card)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value, value - 10 if aces > 0 else value

    def validate_numeric_input(self, value):
        """Validate that the input is numeric or empty."""
        return value.isdigit() or value == ""

    def place_bet(self):
        mixer.music.load(r"C:\Users\Isabella.Pijl\learn\Casino Summative\Shuffle2.wav")
        mixer.music.play()
        time.sleep(2)
        try:
            bet = int(self.bet_entry.get())
            if bet <= 0 or bet > self.balance:
                self.info_label.config(text="Invalid bet amount. Try again.")
                return
            self.current_bet = bet
            self.balance -= bet
            rows = []
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    rows.append(row)

            # Update the second item in the first row
            if rows and len(rows[0]) > 1:  # Ensure the first row exists and has at least two items
                rows[0][1] = self.balance

            # Write the updated content back to the CSV
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            self.balance_label.config(text=f"Balance: ${self.balance}")
            self.info_label.config(text=f"Bet placed: ${bet}. Good luck!")  # Clear previous message here
            self.start_game()
            self.hit_button.config(state=tk.NORMAL)
            self.stand_button.config(state=tk.NORMAL)

            # Show hand labels only after the bet is placed
            self.player_container.pack(pady=10)
            self.dealer_container.pack(pady=10)

        except ValueError:
            self.info_label.config(text="Please enter a valid number.")

    def place_bet_key(self):
        if self.current_bet == 0:
            self.place_bet()

    def start_game(self):
        if len(self.deck) < 4:  # Ensure there are enough cards to deal
            self.deck = self.create_deck()  # Reshuffle the deck
            self.info_label.config(text="Deck reshuffled!")

        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.update_labels(show_dealer_card=False)

    def hit(self):
        self.player_hand.append(self.deck.pop())
        self.update_labels(show_dealer_card=False)
        if self.hand_value(self.player_hand)[0] > 21:
            self.info_label.config(text="You busted! Dealer wins.")
            self.current_bet = int(self.bet_entry.get())
            self.end_round()

    def hit_key(self, event=None):
        if self.hit_button["state"] == tk.NORMAL:
            self.hit()

    def stand(self):
        self.update_labels(show_dealer_card=True)
        while self.hand_value(self.dealer_hand)[0] < 17:
            if not self.deck:  # If the deck is empty, reshuffle
                self.deck = self.create_deck()
                self.info_label.config(text="Deck reshuffled during dealer's turn!")
            self.dealer_hand.append(self.deck.pop())
            self.update_labels(show_dealer_card=True)

        self.check_winner()

        self.check_winner()

    def stand_key(self, event=None):
        if self.stand_button["state"] == tk.NORMAL:
            self.stand()

    def check_winner(self):
        player_value = self.hand_value(self.player_hand)[0]
        dealer_value = self.hand_value(self.dealer_hand)[0]

        if dealer_value > 21 or player_value > dealer_value:
            self.info_label.config(text=f"You win! You earned ${int(self.bet_entry.get()) * 2}.")
            self.balance += self.current_bet * 2
            rows = []
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    rows.append(row)

            # Update the second item in the first row
            if rows and len(rows[0]) > 1:  # Ensure the first row exists and has at least two items
                rows[0][1] = self.balance

            # Write the updated content back to the CSV
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows)

        elif player_value < dealer_value:
            self.info_label.config(text="Dealer wins! Better luck next time.")
        else:
            self.info_label.config(text="It's a tie! Your bet is returned.")
            self.balance += self.current_bet
            rows = []
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    rows.append(row)

            # Update the second item in the first row
            if rows and len(rows[0]) > 1:  # Ensure the first row exists and has at least two items
                rows[0][1] = self.balance

            # Write the updated content back to the CSV
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows)

        self.current_bet = 0
        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.end_round()

    def end_round(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        # Do not reset the info_label; the message will persist

    def update_labels(self, show_dealer_card=True):
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_frame.winfo_children():
            widget.destroy()

        for card in self.player_hand:
            card_label = tk.Label(self.player_frame, image=self.card_images[card], bg="green", bd=2, relief="ridge")
            card_label.pack(side=tk.LEFT, padx=5)

        if show_dealer_card:
            for card in self.dealer_hand:
                card_label = tk.Label(self.dealer_frame, image=self.card_images[card], bg="green", bd=2, relief="ridge")
                card_label.pack(side=tk.LEFT, padx=5)
        else:
            # Show only the first dealer card and hide the second one
            card_label = tk.Label(self.dealer_frame, image=self.card_images[self.dealer_hand[0]], bg="green", bd=2,
                                  relief="ridge")
            card_label.pack(side=tk.LEFT, padx=5)

            hidden_card_label = tk.Label(self.dealer_frame, text="?", font=("Helvetica", 20), bg="green", fg="white")
            hidden_card_label.pack(side=tk.LEFT, padx=5)

        hand_value, alt_value = self.hand_value(self.player_hand)
        if hand_value != alt_value:
            self.info_label.config(text=f"Your Hand Value: {hand_value} or {alt_value}")
        else:
            self.info_label.config(text=f"Your Hand Value: {hand_value}")

    def show_instructions(self):
        instructions = (
            "Welcome to Blackjack!\n\n"
            "Instructions:\n"
            "1. Place your bet using the input field and press 'Place Bet'.\n"
            "2. You are dealt two cards, and one of the dealer's cards is hidden.\n"
            "3. Choose 'Hit' to draw another card or 'Stand' to keep your current hand.\n"
            "4. The goal is to get as close to 21 as possible without exceeding it.\n"
            "5. If your hand value exceeds 21, you lose your bet.\n"
            "6. If you beat the dealer's hand or the dealer busts, you win 2x your bet.\n"
            "7. Ties return your bet.\n"
            "8. Face cards (Jack, Queen, King) are worth 10 points each.\n"
            "9. Aces can be worth 1 or 11, whichever benefits your hand.\n"
            "10. Press 'Enter' to quickly place a bet.\n"
            "11. Press 'H' for Hit and 'S' for Stand during gameplay.\n"
            "12. Place a new bet to start the next round.\n\n"
            "Good luck!"
        )
        messagebox.showinfo("Instructions", instructions)

    def back_to_lobby(self):
        #Terminate the window and return to the lobby
        self.root.destroy()


def play_audio():
    """Play the Shuffle2.wav audio file."""

if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()