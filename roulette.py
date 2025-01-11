import tkinter as tk
from tkinter import messagebox
import random
import time
from pygame import mixer  # For sound effects
import csv

file_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"
with open(file_path, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        BAL = row[1]  # Append the second item to the list


class RouletteGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Roulette Game")
        self.root.configure(bg="#000000")  # Black background for sleek Vegas look
        self.balance = int(BAL)
        self.selected_number = None
        self.selected_color = None
        self.choice = None
        self.number_buttons = {}
        self.red_button = None
        self.black_button = None
        self.result_label = None  # To display the result message
        self.setup_ui()

        # Initialize pygame mixer
        mixer.init()

    def setup_ui(self):
        # Display balance
        self.balance_label = tk.Label(
            self.root,
            text=f"Balance: ${self.balance}",
            font=("Arial", 16),
            bg="#000000",
            fg="#FFFF00"
        )  # Bright Yellow text
        self.balance_label.grid(row=0, column=0, columnspan=12, pady=10)

        # Instructions button at the top-right corner
        tk.Button(
            self.root,
            text="?",
            command=self.show_instructions,
            width=3,
            bg="#1E90FF",
            fg="#FFFFFF"
        ).grid(row=0, column=12, padx=10)

        # Back to Lobby button at the top-left corner
        tk.Button(
            self.root,
            text="Back to Lobby",
            command=self.root.destroy,  # Terminates the window
            width=12,
            bg="#1E90FF",
            fg="#FFFFFF"
        ).grid(row=0, column=0, padx=10, sticky="w")

        # Option to choose Color or Number
        self.choice_frame = tk.Frame(self.root, bg="#000000")
        self.choice_frame.grid(row=1, column=0, columnspan=12, pady=10)
        tk.Label(self.choice_frame, text="Choose your bet type:", bg="#000000", fg="#FFFF00").pack()
        tk.Button(
            self.choice_frame,
            text="Bet on Number",
            command=self.choose_number,
            width=15,
            bg="#ff00a2",
            fg="#000000"
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            self.choice_frame,
            text="Bet on Color",
            command=self.choose_color,
            width=15,
            bg="#ff00a2",
            fg="#000000"
        ).pack(side=tk.LEFT, padx=10)

        # Roulette grid layout (always visible)
        self.roulette_frame = tk.Frame(self.root, bg="#000000")
        self.roulette_frame.grid(row=2, column=0, columnspan=12, padx=10, pady=10)

        self.numbers = {
            0: "green",
            **{i: "red" if i % 2 == 0 else "black" for i in range(1, 37)}
        }

        for num, color in self.numbers.items():
            btn = tk.Button(
                self.roulette_frame,
                text=str(num),
                bg=color,
                fg="white",
                width=5,
                height=2,
                command=lambda n=num: self.select_number(n) if n != 0 else self.invalid_selection()
            )
            self.number_buttons[num] = btn
            row = 0 if num == 0 else (num - 1) // 12 + 1
            col = 0 if num == 0 else (num - 1) % 12
            btn.grid(row=row, column=col, padx=2, pady=2)

        # Color betting options
        self.color_frame = tk.Frame(self.root, bg="#000000")
        self.red_button = tk.Button(
            self.color_frame,
            text="Red",
            bg="red",
            fg="white",
            width=10,
            command=lambda: self.select_color("red")
        )
        self.red_button.pack(side=tk.LEFT, padx=5)
        self.black_button = tk.Button(
            self.color_frame,
            text="Black",
            bg="black",
            fg="white",
            width=10,
            command=lambda: self.select_color("black")
        )
        self.black_button.pack(side=tk.LEFT, padx=5)

        # Entry for bet amount
        self.bet_entry = tk.Entry(
            self.root,
            bg="#1E1E1E",
            fg="#FFD700",
            bd=2,
            insertbackground="#FFD700"
        )
        self.bet_entry.grid(row=5, column=0, columnspan=12, pady=10)

        # Single Spin Button (centered)
        tk.Button(
            self.root,
            text="Spin",
            command=self.spin,
            width=15,
            bg="#ff00a2",
            fg="#000000"
        ).grid(row=6, column=0, columnspan=12, pady=10, sticky="n")

        # Result message
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14),
            fg="#FFFF00",
            bg="#000000"
        )
        self.result_label.grid(row=7, column=0, columnspan=12, pady=10)

    def show_instructions(self):
        """Show instructions in a popup window."""
        instructions = (
            "Roulette Rules:\n\n"
            "Placing Bets:\n"
            "1. Decide whether to bet on a specific number or a color:\n"
            "   - Click 'Bet on Number' to select a number from the grid.\n"
            "   - Click 'Bet on Color' to choose between 'Red' or 'Black.'\n"
            "2. Enter your bet amount in the input field.\n\n"
            "Betting Rules:\n"
            "- You cannot bet on '0' or 'green.'\n"
            "- The bet amount must be greater than $0 and not exceed your current balance.\n\n"
            "Spinning the Wheel:\n"
            "1. Once you've placed your bet, click the 'Spin' button.\n"
            "2. The roulette wheel will spin, and a random result will be displayed.\n\n"
            "Winning or Losing:\n"
            "- If you bet on a number:\n"
            "  - Win: The roulette lands on your chosen number. You earn 2x your bet amount.\n"
            "- If you bet on a color:\n"
            "  - Win: The color matches your selection. You earn 1x your bet amount.\n"
            "- Lose: Your balance decreases by your bet amount if the result doesn’t match your bet.\n\n"
            "Ending the Game:\n"
            "- The game ends if your balance reaches $0.\n"
            "- You can quit the game at any time by clicking the 'Quit' button.\n"
            "Enjoy the game! 🎰"
        )

        # Create a popup window
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.configure(bg="#1E90FF")  # Neon Purple background
        instructions_window.geometry("400x500")

        # Frame to hold the text and scrollbar
        frame = tk.Frame(instructions_window, bg="#1E90FF")
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a text widget with the scrollbar
        text = tk.Text(frame, wrap=tk.WORD, font=("Arial", 12), yscrollcommand=scrollbar.set, bg="#8A2BE2",
                       fg="#FFFF00")  # Yellow text
        text.insert(tk.END, instructions)
        text.config(state=tk.DISABLED)  # Make it read-only
        text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Configure scrollbar to work with the text widget
        scrollbar.config(command=text.yview)

        # Exit button to close the instructions popup
        tk.Button(instructions_window, text="Close", command=instructions_window.destroy, bg="#ff00a2",
                  fg="#000000").pack(pady=10)

    def invalid_selection(self):
        """Display an error message for invalid bets (e.g., betting on 0/green)."""
        self.result_label.config(text="Betting on 0 or green is not allowed.", fg="red")

    def choose_number(self):
        """Activate betting on numbers and disable color selection."""
        self.choice = "number"
        self.selected_color = None
        self.reset_color_highlight()
        self.reset_number_highlight()
        self.color_frame.grid_forget()  # Hide the color options
        for num, btn in self.number_buttons.items():
            btn.config(state=tk.NORMAL)  # Enable number selection

        # Display instructional message
        self.result_label.config(text="Click a number from 1-36 on the grid.", fg="#FFFF00")  # Yellow text

    def choose_color(self):
        """Activate betting on colors and disable number selection."""
        self.choice = "color"
        self.selected_number = None
        self.reset_number_highlight()
        self.color_frame.grid(row=3, column=0, columnspan=12, pady=10)  # Show the color options
        for num, btn in self.number_buttons.items():
            btn.config(state=tk.DISABLED)  # Disable number selection

    def select_number(self, number):
        """Select a number for number betting."""
        if self.choice == "number":
            self.selected_number = number
            self.reset_number_highlight()  # Reset highlights for other numbers
            self.number_buttons[number].config(relief=tk.SUNKEN, bd=5)  # Highlight selected number
        else:
            self.result_label.config(text="You are betting on color. Choose a color instead.", fg="red")

    def select_color(self, color):
        """Select a color for color betting."""
        if self.choice == "color":
            self.selected_color = color
            self.reset_color_highlight()  # Reset highlights for other colors
            if color == "red":
                self.red_button.config(relief=tk.SUNKEN, bd=5)
                self.black_button.config(relief=tk.RAISED, bd=2)
            elif color == "black":
                self.black_button.config(relief=tk.SUNKEN, bd=5)
                self.red_button.config(relief=tk.RAISED, bd=2)

    def reset_color_highlight(self):
        """Reset the visual cues for color selection."""
        self.red_button.config(relief=tk.RAISED, bd=2)
        self.black_button.config(relief=tk.RAISED, bd=2)

    def reset_number_highlight(self):
        """Reset the visual cues for number selection."""
        for num, btn in self.number_buttons.items():
            btn.config(relief=tk.RAISED, bd=2, state=tk.NORMAL)  # Enable all number buttons

    def spin(self):
        """Perform the spin and resolve the bets only if all required fields are valid."""
        errors = []

        # Check if a valid bet amount is entered
        try:
            bet_amount = int(self.bet_entry.get())
            if bet_amount <= 0:
                errors.append("Bet amount must be greater than 0.")
            elif bet_amount > self.balance:
                errors.append("Bet amount exceeds your current balance.")
        except ValueError:
            errors.append("Bet amount must be a valid number.")

        # Check if the user has made a valid choice
        if self.choice is None:
            errors.append("You must select a bet type (number or color).")
        elif self.choice == "number" and self.selected_number is None:
            errors.append("You must select a number to bet on.")
        elif self.choice == "color" and self.selected_color is None:
            errors.append("You must select a color to bet on.")

        # If there are errors, display them and prevent the spin
        if errors:
            self.result_label.config(text="\n".join(errors), fg="#ff00a2")
            return

        # If all checks pass, proceed with spinning
        # Play spinning sound
        mixer.Sound("spin.wav").play()

        spin_result = random.randint(0, 36)
        spin_color = self.numbers[spin_result]

        self.animate_spin(spin_result)

        # Stop spinning sound
        mixer.stop()

        # Resolve bets
        if self.choice == "number":
            if spin_result == self.selected_number:
                winnings = bet_amount * 2
                self.balance += winnings
                self.result_label.config(
                    text=f"WIN! The wheel landed on {spin_result}. You won ${winnings}!", fg="green"
                )
            else:
                self.balance -= bet_amount
                self.result_label.config(
                    text=f"LOSE. The wheel landed on {spin_result}. You lost ${bet_amount}.", fg="red"
                )
        elif self.choice == "color":
            if spin_color == self.selected_color:
                winnings = bet_amount
                self.balance += winnings
                self.result_label.config(
                    text=f"WIN! The wheel landed on {spin_result} ({spin_color}). You won ${winnings}!", fg="green"
                )
            else:
                self.balance -= bet_amount
                self.result_label.config(
                    text=f"LOSE. The wheel landed on {spin_result} ({spin_color}). You lost ${bet_amount}.",
                    fg="red"
                )

        self.update_balance()
        if self.balance <= 0:
            self.result_label.config(text="Game Over! You're out of money.", fg="red")

    def animate_spin(self, result):
        """Animate the spin by flashing the buttons randomly before landing on the result."""
        all_numbers = list(self.number_buttons.keys())
        for _ in range(20):  # Simulate spinning 20 times
            random_button = random.choice(all_numbers)
            self.number_buttons[random_button].config(bg="yellow")
            self.root.update()
            time.sleep(0.05)  # Short delay for spin effect
            self.number_buttons[random_button].config(bg=self.numbers[random_button])
            self.root.update()

        # Highlight the final result
        for _ in range(3):  # Flash the result 3 times
            self.number_buttons[result].config(bg="yellow")
            self.root.update()
            time.sleep(0.3)
            self.number_buttons[result].config(bg=self.numbers[result])
            self.root.update()
            time.sleep(0.3)

    def update_balance(self):
        """Update the displayed balance."""
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

    def quit_game(self):
      self.root.quit()


# Initialize the game
root = tk.Tk()
game = RouletteGame(root)
root.mainloop()
