import sys
import time

history = []

def print_welcome():
    print("=" * 40)
    print("      Welcome to PyCalc CLI")
    print("=" * 40)

def main_menu():
    print("\nChoose an operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Show History")
    print("6. Save History to File")
    print("7. Exit")

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Invalid number. Please try again.")

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def perform_operation(choice):
    a = get_number("Enter first number: ")
    b = get_number("Enter second number: ")

    try:
        if choice == '1':
            result = add(a, b)
            op = '+'
        elif choice == '2':
            result = subtract(a, b)
            op = '-'
        elif choice == '3':
            result = multiply(a, b)
            op = '*'
        elif choice == '4':
            result = divide(a, b)
            op = '/'
        else:
            print("Invalid operation.")
            return

        expression = f"{a} {op} {b} = {result}"
        history.append(expression)
        print("✅ Result:", result)

    except ZeroDivisionError as e:
        print("❌", e)

def show_history():
    if not history:
        print("ℹ️  No history yet.")
    else:
        print("\n📜 Calculation History:")
        for i, record in enumerate(history, 1):
            print(f"{i}. {record}")

def save_history():
    filename = f"calc_history_{int(time.time())}.txt"
    with open(filename, 'w') as f:
        for line in history:
            f.write(line + '\n')
    print(f"💾 History saved to {filename}")

def main():
    print_welcome()

    while True:
        main_menu()
        choice = input("Enter your choice (1–7): ").strip()

        if choice in ['1', '2', '3', '4']:
            perform_operation(choice)
        elif choice == '5':
            show_history()
        elif choice == '6':
            save_history()
        elif choice == '7':
            print("👋 Exiting PyCalc. Goodbye!")
            sys.exit()
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()