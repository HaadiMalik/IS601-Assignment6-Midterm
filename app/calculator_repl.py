########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

from colorama import Fore, Style, init
from dotenv import load_dotenv
import os

init(autoreset=True)
load_dotenv()

PRECISION = int(os.getenv('CALCULATOR_PRECISION', 10))
MAX_INPUT_VALUE = Decimal(os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999'))

def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(f"{Fore.CYAN}Calculator started. Type 'help' for commands.{Style.RESET_ALL}")

        while True:
            try:
                # Prompt the user for a command (with subtle color)
                command = input(f"\n{Fore.WHITE}Enter command: {Style.RESET_ALL}").lower().strip()

                if command == 'help':
                    # Display available commands with organized sections
                    print(f"\n{Fore.CYAN}Available commands:{Style.RESET_ALL}")
                    print(f"  {Fore.GREEN}Operations:{Style.RESET_ALL}")
                    print("    add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff")
                    print(f"  {Fore.YELLOW}History:{Style.RESET_ALL}")
                    print("    history - Show calculation history")
                    print("    clear - Clear calculation history")
                    print("    undo - Undo the last calculation")
                    print("    redo - Redo the last undone calculation")
                    print(f"  {Fore.BLUE}File Operations:{Style.RESET_ALL}")
                    print("    save - Save calculation history to file")
                    print("    load - Load calculation history from file")
                    print(f"  {Fore.MAGENTA}exit{Style.RESET_ALL} - Exit the calculator")
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(f"{Fore.GREEN}History saved successfully.{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.YELLOW}Warning: Could not save history: {e}{Style.RESET_ALL}")
                    print(f"{Fore.RED}{Style.BRIGHT}Goodbye!{Style.RESET_ALL}")
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(f"{Fore.YELLOW}No calculations in history{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.CYAN}Calculation History:{Style.RESET_ALL}")
                        for i, entry in enumerate(history, 1):
                            print(f"{Fore.WHITE}{i}.{Style.RESET_ALL} {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(f"{Fore.GREEN}History cleared{Style.RESET_ALL}")
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(f"{Fore.GREEN}Operation undone{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Nothing to undo{Style.RESET_ALL}")
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(f"{Fore.GREEN}Operation redone{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Nothing to redo{Style.RESET_ALL}")
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(f"{Fore.GREEN}History saved successfully{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Error saving history: {e}{Style.RESET_ALL}")
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(f"{Fore.GREEN}History loaded successfully{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Error loading history: {e}{Style.RESET_ALL}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'int_divide', 'percent', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print(f"\n{Fore.CYAN}Enter numbers (or 'cancel' to abort):{Style.RESET_ALL}")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                            continue
                        # if Decimal(a) > MAX_INPUT_VALUE:
                        #     print(f"Error: Input exceeds maximum allowed value of {MAX_INPUT_VALUE}")
                        #     continue

                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                            continue
                        # if Decimal(b) > MAX_INPUT_VALUE:
                        #     print(f"Error: Input exceeds maximum allowed value of {MAX_INPUT_VALUE}")
                        #     continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()
                            if len(str(result)[str(result).find('.') + 1:]) > PRECISION:
                                result = round(result, PRECISION)

                        print(f"\n{Fore.GREEN}{Style.BRIGHT}Result: {result}{Style.RESET_ALL}")
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                    continue

                # Handle unknown commands
                print(f"{Fore.RED}Unknown command: '{command}'. Type 'help' for available commands.{Style.RESET_ALL}")

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(f"\n{Fore.CYAN}Input terminated. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"{Fore.RED}{Style.BRIGHT}Fatal error: {e}{Style.RESET_ALL}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise