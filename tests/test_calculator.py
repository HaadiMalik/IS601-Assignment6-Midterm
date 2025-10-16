import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_memento import CalculatorMemento
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

@patch('app.calculator.logging.basicConfig', side_effect=PermissionError("Cannot write to log file"))
def test_logging_setup_exception(logging_basicConfig_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # This should raise the PermissionError from basicConfig
        with pytest.raises(PermissionError, match="Cannot write to log file"):
            Calculator(CalculatorConfig())

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
def test_history_exceeds_max_history(calculator):
    # Set a small max_history_size for testing
    calculator.config.max_history_size = 3
    
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    # Perform 4 operations to exceed the max history size of 3
    calculator.perform_operation(1, 1)
    calculator.perform_operation(2, 2)
    calculator.perform_operation(3, 3)
    calculator.perform_operation(4, 4)
    
    assert len(calculator.history) == 3
    
    assert calculator.history[0].operand1 == Decimal('2')
    assert calculator.history[1].operand1 == Decimal('3')
    assert calculator.history[2].operand1 == Decimal('4')

@patch('app.calculator.pd.DataFrame.to_csv', side_effect=IOError("Disk error"))
def test_save_history_exception(mock_to_csv, calculator):
    # Test that exceptions during save_history are caught
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    
    with pytest.raises(OperationError, match="Failed to save history: Disk error"):
        calculator.save_history()

@patch('app.calculator.pd.read_csv', side_effect=IOError("Cannot read file"))
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_exception(mock_exists, mock_read_csv, calculator):
    # Test that exceptions during load_history are caught
    with pytest.raises(OperationError, match="Failed to load history: Cannot read file"):
        calculator.load_history()

def test_get_history_dataframe(calculator):
    # Test that get_history_dataframe returns a proper pandas DataFrame
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 7)
    
    df = calculator.get_history_dataframe()
    assert isinstance(df, pd.DataFrame)
    
    assert len(df) == 2
    assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']
    
    assert df.iloc[0]['operation'] == 'Addition'
    assert df.iloc[0]['operand1'] == '2'
    assert df.iloc[0]['operand2'] == '3'
    assert df.iloc[0]['result'] == '5'
    
    assert df.iloc[1]['operand1'] == '5'
    assert df.iloc[1]['operand2'] == '7'
    assert df.iloc[1]['result'] == '12'

# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# ===== REPL Tests =====

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

# Additional REPL Tests

@patch('builtins.input', side_effect=['history', 'clear', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_history_commands(mock_print, mock_input):
    # Test history, clear, undo, redo on empty state
    with patch('app.calculator.Calculator.show_history', return_value=[]):
        calculator_repl()
        mock_print.assert_any_call("No calculations in history")
        mock_print.assert_any_call("History cleared")
        mock_print.assert_any_call("Nothing to undo")
        mock_print.assert_any_call("Nothing to redo")


@patch('builtins.input', side_effect=['add', '5', '3', 'history', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_operations_with_history(mock_print, mock_input):
    # Test operation with history display and undo/redo
    calculator_repl()
    mock_print.assert_any_call("\nResult: 8")
    assert any("Calculation History:" in str(call) for call in mock_print.call_args_list)
    mock_print.assert_any_call("Operation undone")
    mock_print.assert_any_call("Operation redone")


@patch('builtins.input', side_effect=['add', 'cancel', 'subtract', '10', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_operations(mock_print, mock_input):
    # Test cancel at both number prompts
    calculator_repl()
    cancelled_calls = sum(1 for call in mock_print.call_args_list if 'Operation cancelled' in str(call))
    assert cancelled_calls == 2


@patch('builtins.input', side_effect=['subtract', '10', '3', 'multiply', '6', '7', 'divide', '20', '4', 'power', '2', '3', 'root', '27', '3', 'exit'])
@patch('builtins.print')
def test_repl_all_operations(mock_print, mock_input):
    # Test all arithmetic operations
    calculator_repl()
    mock_print.assert_any_call("\nResult: 7")
    mock_print.assert_any_call("\nResult: 42")
    mock_print.assert_any_call("\nResult: 5")
    mock_print.assert_any_call("\nResult: 8")
    mock_print.assert_any_call("\nResult: 3")

@patch('app.calculator.InputValidator.validate_number', side_effect=Exception("Unexpected error"))
def test_perform_operation_unexpected_exception(mock_validate, calculator):
    # Test that unexpected exceptions in perform_operation are caught
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    with pytest.raises(OperationError, match="Operation failed: Unexpected error"):
        calculator.perform_operation(2, 3)

@patch('app.calculator.Calculator.save_history', side_effect=Exception("Save error"))
@patch('app.calculator.Calculator.load_history', side_effect=Exception("Load error"))
@patch('builtins.input', side_effect=['save', 'load', 'exit'])
@patch('builtins.print')
def test_repl_save_load_errors(mock_print, mock_input, mock_load, mock_save):
    # Test save and load error handling
    calculator_repl()
    assert any("Error saving history" in str(call) for call in mock_print.call_args_list)
    assert any("Error loading history" in str(call) for call in mock_print.call_args_list)


@patch('builtins.input', side_effect=['add', 'invalid', '3', 'divide', '5', '0', 'multiply', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_error_handling_and_continue(mock_print, mock_input):
    # Test ValidationError, OperationError, then successful operation
    calculator_repl()
    print_calls = [str(call) for call in mock_print.call_args_list]
    assert sum("Error:" in call for call in print_calls) >= 2
    mock_print.assert_any_call("\nResult: 6")


@patch('app.operations.OperationFactory.create_operation', side_effect=RuntimeError("Factory error"))
@patch('builtins.input', side_effect=['add', '5', '3', 'exit'])
@patch('builtins.print')
def test_repl_unexpected_error(mock_print, mock_input, mock_factory):
    # Test unexpected exception handling
    calculator_repl()
    assert any("Unexpected error:" in str(call) for call in mock_print.call_args_list)


@patch('app.calculator.Calculator.save_history', side_effect=IOError("Disk error"))
@patch('builtins.input', side_effect=['unknown_cmd', 'exit'])
@patch('builtins.print')
def test_repl_unknown_command_and_exit_error(mock_print, mock_input, mock_save):
    # Test unknown command and exit with save error
    calculator_repl()
    assert any("Unknown command" in str(call) for call in mock_print.call_args_list)
    assert any("Warning: Could not save history" in str(call) for call in mock_print.call_args_list)
    mock_print.assert_any_call("Goodbye!")


@patch('builtins.input', side_effect=[KeyboardInterrupt(), EOFError()])
@patch('builtins.print')
def test_repl_interrupts(mock_print, mock_input):
    # Test KeyboardInterrupt and EOFError
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")


def test_calculator_memento_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    memento = CalculatorMemento(history=[calc])
    memento_dict = memento.to_dict()

    assert isinstance(memento_dict, dict)
    assert 'history' in memento_dict
    assert isinstance(memento_dict['history'], list)
    assert len(memento_dict['history']) == 1
    assert 'timestamp' in memento_dict
    assert isinstance(memento_dict['timestamp'], str)

    calc_dict = memento_dict['history'][0]
    assert calc_dict['operation'] == "Addition"
    assert calc_dict['operand1'] == "2"
    assert calc_dict['operand2'] == "3"
    assert calc_dict['result'] == "5"
    assert 'timestamp' in calc_dict


# Test for from_dict()
def test_calculator_memento_from_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    memento_dict = {
        'history': [calc.to_dict()],  # Serialize a sample calculation
        'timestamp': datetime.datetime.now().isoformat()  # Current timestamp in ISO format
    }

    memento_restored = CalculatorMemento.from_dict(memento_dict)

    assert isinstance(memento_restored, CalculatorMemento)
    assert len(memento_restored.history) == 1
    assert memento_restored.history[0].operation == "Addition"
    assert memento_restored.history[0].operand1 == Decimal("2")
    assert memento_restored.history[0].operand2 == Decimal("3")
    assert memento_restored.history[0].result == Decimal("5")
    assert isinstance(memento_restored.timestamp, datetime.datetime)

    assert memento_restored.timestamp.isoformat() == memento_dict['timestamp']


# Test for from_dict() with missing or invalid data
def test_calculator_memento_from_dict_invalid():
    invalid_dict = {
        'history': [],  # No history provided
        'timestamp': "invalid_timestamp"  # Invalid timestamp format
    }

    with pytest.raises(ValueError):
        CalculatorMemento.from_dict(invalid_dict)