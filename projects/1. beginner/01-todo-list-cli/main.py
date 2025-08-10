import os
from datetime import datetime

TODO_FILE = os.path.join(os.path.dirname(__file__), "todos.txt")

# --- TEMP: Clear todos.txt ---
# with open(TODO_FILE, "w") as file:
#    pass  # This will empty the file


def load_todos():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]


def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        for todo in todos:
            file.write(todo + "\n")


def show_todos(todos):
    if not todos:
        print("No tasks found.")
    else:
        for i, todo in enumerate(todos, 1):
            task, due = todo.split(" | ")
            print(f"{i}. {task} (Due: {due})")


def main():
    todos = load_todos()

    while True:
        print("\n--- To-Do List ---")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Exit")

        choice = input("Choose an option (1–4): ").strip()

        if choice == "1":
            show_todos(todos)

        elif choice == "2":
            new_task = input("Enter new task: ").strip()
            if new_task:
                while True:
                    due_date = input("Enter a due date (YYYY-MM-DD): ").strip()
                    try:
                        datetime.strptime(due_date, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD.")
                todos.append(f"{new_task} | {due_date}")
                save_todos(todos)
                print("Task added.")

        elif choice == "3":
            show_todos(todos)
            try:
                task_num = int(input("Enter task number to remove: "))
                if 1 <= task_num <= len(todos):
                    removed = todos.pop(task_num - 1)
                    save_todos(todos)
                    print(f"Removed: {removed}")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a number.")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
