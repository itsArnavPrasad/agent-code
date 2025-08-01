import sys

def add(x, y):
  """Add two numbers."""
  return x + y

def subtract(x, y):
  """Subtract two numbers."""
  return x - y

def multiply(x, y):
  """Multiply two numbers."""
  return x * y

def divide(x, y):
  """Divide two numbers. Handle division by zero."""
  try:
    return x / y
  except ZeroDivisionError:
    return "Division by zero error!"

def main():
  """Handle user input and output for basic arithmetic operations."""
  while True:
    print("Select operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

    choice = input("Enter choice(1/2/3/4/5): ")

    if choice == '5':
      break

    try:
      num1 = float(input("Enter first number: "))
      num2 = float(input("Enter second number: "))
    except ValueError:
      print("Invalid input. Please enter numbers only.")
      continue

    if choice == '1':
      print(num1, "+", num2, "=", add(num1, num2))
    elif choice == '2':
      print(num1, "-", num2, "=", subtract(num1, num2))
    elif choice == '3':
      print(num1, "*", num2, "=", multiply(num1, num2))
    elif choice == '4':
      print(num1, "/", num2, "=", divide(num1, num2))
    else:
      print("Invalid input")

if __name__ == "__main__":
  main()