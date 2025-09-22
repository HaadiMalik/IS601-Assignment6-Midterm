# This file is now called "Operations.py", and it contains a class `Operations` with four static methods:
# addition, subtraction, multiplication, and division.
# These methods are encapsulated within the `Operations` class, providing a structured way to perform basic math on two numbers.
# When we need to add, subtract, multiply, or divide numbers, we can call these static methods through the class.

class Operations:
    """
    The Operations class serves as a container for basic math operations.
    By using static methods, we can perform these operations without needing to create an instance of the class.
    """

    @staticmethod
    def addition(a: float, b: float) -> float:
        """
        This static method takes two numbers (a and b) and returns their sum (a + b).
        The 'float' in the parentheses indicates that both 'a' and 'b' should be numbers with decimal points.
        The '-> float' part means that this method will return a number with decimals (a float) as the result.
        Example: if we call Operations.addition(5.0, 3.0), it will return 8.0.
        """
        return a + b  # This performs the addition of the two numbers and returns the result.

    @staticmethod
    def subtraction(a: float, b: float) -> float:
        """
        This static method takes two numbers (a and b) and returns their difference (a - b).
        Just like the addition method, it expects two numbers and returns their result.
        Example: if we call Operations.subtraction(10.0, 4.0), it will return 6.0.
        """
        return a - b  # This subtracts the second number (b) from the first number (a) and returns the result.

    @staticmethod
    def multiplication(a: float, b: float) -> float:
        """
        This static method takes two numbers (a and b) and returns their product (a * b).
        Multiplying means we take one number and increase it by the other number’s value repeatedly.
        Example: if we call Operations.multiplication(2.0, 3.0), it will return 6.0.
        """
        return a * b  # This multiplies the two numbers and returns the result.

    @staticmethod
    def division(a: float, b: float) -> float:
        """
        This static method takes two numbers (a and b) and returns their quotient (a / b).
        Dividing means breaking the first number into equal parts based on the second number.
        BUT WAIT! There's an important check here: before we divide, we need to make sure that 'b' is not zero.
        
        Why? Because dividing by zero doesn't work. If we try to divide by zero, we get a big error!
        
        So, if 'b' is zero, we raise a 'ValueError', which is a way of telling the program, "Stop! You can't do this."
        Example: if we call Operations.division(10.0, 2.0), it will return 5.0.
        But if we call Operations.division(10.0, 0.0), it will raise a ValueError and say "Division by zero is not allowed."
        """
        if b == 0:
            # This part checks if 'b' is zero. If it is, we raise an error and stop the method.
            raise ValueError("Division by zero is not allowed.")  # This sends an error message when someone tries to divide by zero.
        return a / b  # If 'b' is not zero, we divide the first number (a) by the second number (b) and return the result.
