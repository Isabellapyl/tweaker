import tkinter as tk
from PIL import Image, ImageTk
import random
import csv

# Path to player balance CSV file
FILE_PATH = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"

# Card values
CARD_VALUES = list(range(2, 11)) + [11, 12, 13, 1]  # 2-10, Jack (11), Queen (12), King (13), Ace (1)
CARD_SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
DECK = [(value, suit) for value in CARD_VALUES for suit in CARD_SUITS]

# Path to card images
IMAGE_PATH_TEMPLATE = "C:/Users/Isabella.Pijl/learn/Casino Summative/Playing Cards/Playing Cards/PNG-cards-1.3/{}_of_{}.png"


class CardGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Higher or Lower Card Game")
        self.root.geometry("800x600")  # Enlarged window size
        self.root.configure(bg="#001F3F")  # navy blue background

        # Back to Lobby button in the top-left corner
        self.back_to_lobby_button = tk.Button(
            root,
            text="Back to Lobby",
            command=root.destroy,  # Close the game window (this will always bring them back to the lobby)
            bg="#FFD700",  # Yellow-gold color
            fg="#000000",  # Black text
            font=("Arial", 12),
            width=12
        )
        self.back_to_lobby_button.place(relx=0.01, rely=0.02, anchor="nw")  # Position at the top-left corner (for consitency through all the games)

        # Define font styles
        font_large = ("Arial", 20)
        font_medium = ("Arial", 16)

        # Load balance from CSV
        self.balance = self.load_balance()

        self.bet = None  # Bet must be explicitly set before game can start
        self.deck = DECK.copy()
        random.shuffle(self.deck)

        # Load card images
        self.card_images = self.load_card_images()

        # UI Components
        self.instructions_button = tk.Button(
            root, text="Instructions", command=self.show_instructions, bg="#FFD700", fg="#000000", font=("Arial", 12)
        )
        self.instructions_button.place(relx=0.9, rely=0.02, anchor="ne")  # Top-right corner

        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance}", bg="#001F3F", fg="#FFFFFF", font=font_large)
        self.balance_label.pack(pady=10)

        self.bet_label = tk.Label(root, text="Enter Bet Amount:", bg="#001F3F", fg="#FFFFFF", font=font_medium)
        self.bet_label.pack()

        # Validate function to allow only numeric input (no letters or symbols)
        vcmd = (root.register(self.validate_numeric_input), "%P")

        self.bet_entry = tk.Entry(
            root,
            font=font_medium,
            validate="key",
            validatecommand=vcmd,
            bg="#FFFFFF",  # White background
            highlightbackground="#FFD700",  # Gold border when not focused
            highlightcolor="#FFD700",  # Gold border when focused
            highlightthickness=2,  # Border thickness
        )
        self.bet_entry.pack(pady=5)
        self.bet_entry.insert(0, "10")  # Default bet amount
        self.bet_entry.bind("<KeyRelease>", self.disable_buttons)  # Detect input change and disable buttons

        self.set_bet_button = tk.Button(root, text="Set Bet", command=self.set_bet, bg="#FFD700", fg="#000000", font=font_medium)
        self.set_bet_button.pack(pady=10)

        self.guess_label = tk.Label(
            root, text="Guess if the next card is Higher or Lower than 7", bg="#001F3F", fg="#FFFFFF", font=font_medium
        )
        self.guess_label.pack()

        self.higher_button = tk.Button(root, text="Higher", command=lambda: self.make_guess("higher"), bg="#FFD700", fg="#000000", font=font_medium, state="disabled")
        self.higher_button.pack(side=tk.LEFT, padx=20)

        self.lower_button = tk.Button(root, text="Lower", command=lambda: self.make_guess("lower"), bg="#FFD700", fg="#000000", font=font_medium, state="disabled")
        self.lower_button.pack(side=tk.RIGHT, padx=20)

        self.result_label = tk.Label(root, text="", bg="#001F3F", fg="#FFFFFF", font=font_medium)
        self.result_label.pack(pady=10)

        # Frame to display the drawn card
        self.card_frame = tk.Frame(root, bg="#001F3F")
        self.card_frame.pack(pady=20)

        # Bind keys for Higher and Lower guesses
        self.root.bind("h", lambda event: self.make_guess("higher"))
        self.root.bind("l", lambda event: self.make_guess("lower"))
        self.root.bind("<Return>", lambda event: self.set_bet())

    def show_instructions(self):
        #Display the instructions in a new window
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry("400x300")
        instructions_window.configure(bg="#001F3F")  # Deep navy blue background

        font_instructions = ("Arial", 14)
        instructions_label = tk.Label(
            instructions_window,
            text=(
                "Instructions:\n"
                "- Enter your bet amount and press Enter or click 'Set Bet'.\n"
                "- Guess if the next card is higher or lower than 7.\n"
                "- Use 'Higher' or 'Lower' buttons (or press H/L).\n"
                "- Special Rules:\n"
                "  * Aces, 7s, and Kings lose 2x your bet.\n"
                "  * Correct guesses win 2x your bet.\n"
            ),
            bg="#001F3F",  # Navy blue background
            fg="#FFD700",  # Gold text
            font=font_instructions,
            justify="left",
            wraplength=380,
        )
        instructions_label.pack(pady=10, padx=10)

        close_button = tk.Button(instructions_window, text="Close", command=instructions_window.destroy, bg="#FFD700", fg="#000000")  # Gold button
        close_button.pack(pady=10)




    def validate_numeric_input(self, new_value):
        #Validate that the input contains only numeric characters.
        if new_value == "" or new_value.isdigit():
            return True
        return False

    def disable_buttons(self, event=None):
        #Disable Higher and Lower buttons if bet input changes.
        self.higher_button.config(state="disabled")
        self.lower_button.config(state="disabled")

    def enable_buttons(self):
        #Enable Higher and Lower buttons.
        self.higher_button.config(state="normal")
        self.lower_button.config(state="normal")

    def load_balance(self):
        try:
            with open(FILE_PATH, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    return int(row[1])  # Return the balance from the second column
        except (FileNotFoundError, IndexError, ValueError):
            return 500  # Default balance if file is missing or invalid

    def update_balance(self):
        rows = []
        with open(FILE_PATH, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)

        if rows and len(rows[0]) > 1:
            rows[0][1] = str(self.balance)

        with open(FILE_PATH, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        self.balance_label.config(text=f"Balance: ${self.balance}")

    def load_card_images(self):
        card_images = {}
        for value, suit in DECK:
            rank = self.get_card_name(value)
            suit_name = suit.lower()
            card_name = f"{rank} of {suit}"
            try:
                image_path = IMAGE_PATH_TEMPLATE.format(rank, suit_name)
                image = Image.open(image_path).resize((150, 218))  # Increased image size
                card_images[card_name] = ImageTk.PhotoImage(image)
            except FileNotFoundError:
                print(f"Image for {card_name} not found. Skipping...")
        return card_images

    def get_card_name(self, value):
        if value == 1:
            return "Ace"
        elif value == 11:
            return "Jack"
        elif value == 12:
            return "Queen"
        elif value == 13:
            return "King"
        else:
            return str(value)

    def set_bet(self):
        try:
            amount = int(self.bet_entry.get())
            if amount > 0:
                self.bet = amount
                self.result_label.config(text=f"Bet amount set to ${self.bet}.")
                self.enable_buttons()  # Enable buttons after setting a valid bet
            else:
                self.result_label.config(text="Bet amount must be greater than 0.")
        except ValueError:
            self.result_label.config(text="Invalid bet amount. Please enter a number.")

    def draw_card(self):
        if not self.deck:
            self.deck = DECK.copy()
            random.shuffle(self.deck)
        return self.deck.pop()

    def display_card(self, card_value, card_suit):
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        rank = self.get_card_name(card_value)
        card_name = f"{rank} of {card_suit}"
        if card_name in self.card_images:
            card_image_label = tk.Label(self.card_frame, image=self.card_images[card_name], bg="#001F3F", bd=2, relief="ridge")
            card_image_label.pack()
        else:
            self.result_label.config(text=f"Card image not available for {card_name}.")

    def make_guess(self, guess):
        if self.bet is None:
            self.result_label.config(text="You must set your bet before playing!")
            return

        if self.bet > self.balance:
            self.result_label.config(text="Not enough balance to place the bet!")
            return

        card_value, card_suit = self.draw_card()
        self.display_card(card_value, card_suit)

        card_name = self.get_card_name(card_value)

        if card_value in {1, 7, 13}:  # Ace (1), 7, or King (13)
            loss = self.bet * 2
            self.balance -= loss
            if self.balance < 0:  # Prevent negative balance
                self.balance = 0
            self.result_label.config(
                text=f"A {card_name} was drawn: {card_name} of {card_suit}. You lost 2 times your bet (${loss})!"
            )
        elif (guess == "higher" and card_value > 7) or (guess == "lower" and card_value < 7):
            winnings = int(self.bet * 2)
            self.balance += winnings
            self.result_label.config(
                text=f"A {card_name} was drawn: {card_name} of {card_suit}. You won ${winnings}!"
            )
        else:
            self.balance -= self.bet
            if self.balance < 0:  # Prevent negative balance
                self.balance = 0
            self.result_label.config(
                text=f"A {card_name} was drawn: {card_name} of {card_suit}. You lost ${self.bet}."
            )

        self.update_balance()


if __name__ == "__main__":
    root = tk.Tk()
    app = CardGameApp(root)
    root.mainloop()

