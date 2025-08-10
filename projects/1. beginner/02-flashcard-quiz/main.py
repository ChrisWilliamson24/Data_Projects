import json
import os
import random

FLASHCARDS = os.path.join(os.path.dirname(__file__), "flashcards.json")


def load_flashcards():
    if not os.path.exists(FLASHCARDS):
        print("No flashcards file found. Please create some flashcards")
        return []

    with open(FLASHCARDS, "r") as f:
        flashcards = json.load(f)

    return flashcards


def quiz_user():
    flashcards = load_flashcards()
    if not flashcards:
        return

    random.shuffle(flashcards)
    score = 0
    wrong_cards = []

    for i, card in enumerate(flashcards, start=1):
        print(f"\nQuestion {i}: {card['question']}")
        user_answer = input("Your answer: ").strip()

        if user_answer.lower() == card["answer"].lower():
            print("Correct! :)))")
            score += 1
        else:
            print(f"Wrong :( The correct answer was: {card['answer']}")
            wrong_cards.append(card)

    # Retry loop
    while wrong_cards:
        print("\nLet's try the ones you got wrong again...")
        new_wrong_cards = []

        for i, card in enumerate(wrong_cards, start=1):
            print(f"\nRetry Question {i}: {card['question']}")
            user_answer = input("Your answer: ").strip()

            if user_answer.lower() == card["answer"].lower():
                print("You got it this time!")
                score += 1
            else:
                print(f"Still incorrect :( The answer was: {card['answer']}")
                new_wrong_cards.append(card)

        wrong_cards = new_wrong_cards

    print(f"\n🏁 Quiz complete! Your score: {score}/{len(flashcards)}")


def create_flashcards():
    flashcards = []

    print("Enter your flashcards (type 'quit' to stop).")
    while True:
        question = input("Question: ")
        if question.lower() == "quit":
            break

        answer = input("Answer: ")
        if answer.lower() == "quit":
            break

        flashcards.append({"question": question, "answer": answer})

    with open(FLASHCARDS, "w") as f:
        json.dump(flashcards, f)

    print("Flashcards have been saved to flashcards.json")


def main():
    while True:
        print("1. Create new flashcards")
        print("2. Begin quiz")
        print("3. Exit")

        try:
            answer = int(input("What would you like to do? (1-3)"))
        except ValueError:
            print("Wrong input. Please select a number 1-3")
            continue

        if answer == 1:
            create_flashcards()
        elif answer == 2:
            quiz_user()
        elif answer == 3:
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


main()
