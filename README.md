# Password Guessing Game

## Project Description
The **Password Guessing Game** is a Python-based GUI application inspired by Wordle, where players try to guess a secret password within a limited number of attempts. The game features difficulty levels, hints, Wordle-style feedback, scoring, and an interactive UI with light/dark theme design.

**Project Short Description (30 words):**  
A Wordle-inspired Python game where players guess passwords. Features difficulty levels, hints, scoring, and visual feedback with a responsive Tkinter GUI and interactive purple-themed UI.

---

## Features
- **Multiple difficulty levels:** Easy, Medium, Hard.
- **Wordle-style feedback:** Correct letters in correct position, present in wrong position, or absent.
- **Hints system:** Reveal first letter or show scrambled word.
- **Scoring system:** Base score, penalties for wrong guesses and hints.
- **Interactive GUI:** Tkinter-based with styled labels, buttons, and animations.
- **Responsive layout:** Works on different screen sizes.
- **Replayable:** Option to play again or exit after game completion.

---

## Libraries Used
- **Tkinter:** For GUI interface and layout management.
- **ttk:** Themed widgets for buttons, labels, and frames.
- **random:** To randomly select secret words and shuffle hints.
- **string:** To validate alphabetic input.
- **messagebox:** Display alerts for invalid input.

---

## Functions Overview
- **`evaluate_guess(guess, secret)`**: Returns feedback for each letter (`correct`, `present`, `absent`) with Wordle rules.
- **`scramble(word)`**: Returns a shuffled version of a word for hints.
- **`PasswordGuessApp` class**: Main app class handling screen navigation, game state, and scoring.
- **`StartScreen` class**: Displays difficulty selection and info.
- **`GameScreen` class**: Handles the game board, input, hints, live feedback, and animations.
- **`ResultScreen` class**: Shows final result, score, and options to replay or exit.
- **`_on_typing` method**: Provides live typing feedback and limits input length.
- **`submit_guess` method**: Validates input and updates game board with feedback.
- **`show_hint` method**: Provides staged hints to the player.

---

## Flowchart

```text
+-----------------+
| Start Screen    |
| Choose Difficulty|
+--------+--------+
         |
         v
+-----------------+
| Game Screen     |
| Input Guess     |
+--------+--------+
         |
         v
+------------------------+
| Validate Input & Guess |
+--------+---------------+
         |
         v
+------------------------+
| Provide Feedback       |
| (correct/present/absent)|
+--------+---------------+
         |
         v
+------------------------+
| Check Win/Loss         |
+--------+---------------+
         |
         v
+------------------------+
| Result Screen          |
| Show Score & Stats     |
+--------+---------------+
         |
         v
+------------------------+
| Replay or Exit         |
+------------------------+

## Labeled Diagram (Component Overview)

+------------------------------------------------------+
|                 PasswordGuessApp (Main)             |
|------------------------------------------------------|
| - secret: str                                        |
| - difficulty: str                                    |
| - attempts: int                                      |
| - score: int                                        |
| - hints_used: int                                    |
|------------------------------------------------------|
| Screens:                                             |
| 1. StartScreen                                       |
|    - Difficulty selection buttons                     |
|    - Info labels                                     |
| 2. GameScreen                                        |
|    - Entry widget for guesses                        |
|    - Submit & Hint buttons                            |
|    - Board with tiles for feedback                   |
|    - Status & prompt labels                           |
| 3. ResultScreen                                      |
|    - Displays win/lose message                        |
|    - Shows attempts, hints, score                     |
|    - Play again / Exit buttons                        |
+------------------------------------------------------+


How to Run

Install Python 3.x if not already installed.

Save the project files in a folder.

Run the main file:

python game1.py


Select a difficulty level and start guessing the password.

Notes

Words are pre-defined in three difficulty levels.

Maximum attempts: 6.

Base score decreases with wrong guesses and hints.

The game uses a purple-themed GUI inspired by Wordle.



