*Repo cloned from Assignment 3 and modified*
*Repo cloned from Assignment 4 and modified*

This project is a simple command-line calculator built using Python, which supports basic arithmetic operations (addition, subtraction, multiplication, and division) via a REPL (Read-Eval-Print Loop) interface. This project also includes unit tests and CI/CD integration using GitHub Actions.

# Features

- REPL Interface for continuous user interaction.
- Basic arithmetic operations: Addition, Subtraction, Multiplication, and Division.
- Input validation and error handling for invalid inputs and division by zero.
- Unit tests for the REPL and operation logic.

# Installation

Assuming that git is already setup and integrated into the command-line for the following git commands

## Follow these steps to set up the project locally.

1.  **Clone the repository:**

    ```
    git clone https://github.com/HaadiMalik/IS601-Assignment4.git
    cd IS601-Assignment4
    ```

2.  **Create a virtual environment:**

    To isolate dependencies, it's recommended to use a virtual environment.

    ```
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**

    On macOS/Linux:

    ```
    source venv/bin/activate
    ```

    On Windows:

    ```
    venv\Scripts\activate
    ```

4.  **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

# Usage

## Running the Calculator REPL:

Once the environment is set up, you can start the calculator REPL by running:

```
python main.py
```

You will be prompted to enter a mathematical operation (+, -, \*, /) and two numbers. The calculator will evaluate the operation and print the result.

## Running Tests

The project includes comprehensive unit tests for both the REPL and the arithmetic operations. To run the tests:

1. **Ensure dependencies are installed (if not already done):**

```
pip install -r requirements.txt
```

2. **Run tests using pytest:**

```
pytest
```
