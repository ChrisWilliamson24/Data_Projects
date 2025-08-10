# 02-flashcard-quiz

A beginner-friendly Python app that allows users to create flashcards and quiz themselves on saved questions. Flashcards are stored persistently in a local JSON file.

## Features

- Create new flashcards with a question and answer.
- Save flashcards to a JSON file (`flashcards.json`) for later use.
- Load saved flashcards and quiz the user in random order.
- Track correct and incorrect answers.
- Retry incorrect flashcards until all are answered correctly.
- Final score displayed at the end of the quiz.
- Menu system to select between creating flashcards, starting a quiz, or exiting the app.

## How It Works

- Flashcards are stored as dictionaries with `question` and `answer` fields.
- All flashcards are saved in a single JSON file in the same directory as the script.
- During a quiz, incorrect answers are tracked and re-asked until they are correctly answered.
- The app tracks your score as the number of flashcards you eventually answer correctly.
