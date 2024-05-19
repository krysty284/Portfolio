"""The Task Wiser"""

import csv
import os
from datetime import datetime

def main():
    print("Welcome to The Task Wiser!")
    tasks = load_tasks()

    while True:
        print("\n1. Add Task\n2. View Tasks\n3. Delete Task\n4. Save and Exit")
        choice = input("Enter your choice by number: ")

        if choice == '1':
            task_name = input("Enter task name: ")
            day = get_valid_input("Enter the day of the month (1-31): ", 1, 31)
            month = get_valid_input("Enter the month (1-12): ", 1, 12)
            year = datetime.now().year
            tasks.append((task_name, f"{year}-{month:02d}-{day:02d}"))
            print("Task added successfully!")
        elif choice == '2':
            if tasks:
                print("\nTasks:")
                for i, (date, task) in enumerate(tasks, 1):
                    print(f"{i}. {date} - {task}")
            else:
                print("No tasks added yet!")
        elif choice == '3':
            delete_task(tasks)
        elif choice == '4':
            save_tasks(tasks)
            print("Tasks saved successfully. Exiting Task Wiser. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def load_tasks(filename='tasks.csv'):
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            tasks = []
            for row in reader:
                date, task = row[0].split(' - ')
                tasks.append((date, task))
            return tasks
    except FileNotFoundError:
        return []


def save_tasks(tasks, filename='tasks.csv'):
    sorted_tasks = sorted(tasks, key=lambda x: x[0])  # Sort tasks by date
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for date, task in sorted_tasks:
            # Save tasks with a dash between date and task
            writer.writerow([f"{date} - {task}"])

def delete_task(tasks):
    try:
        index = int(input("Enter the number of the task to delete: "))
        if 1 <= index <= len(tasks):
            del tasks[index - 1]
            print("Task deleted successfully!")
        else:
            print("Invalid index. Please enter a valid index.")
    except ValueError:
        print("Invalid input. Please enter a valid index.")

def get_valid_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Value must be between {min_val} and {max_val}. Try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
