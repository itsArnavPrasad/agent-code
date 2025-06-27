import os
import shutil
from pathlib import Path
from typing import Optional, List, Union
import re


class WriteUtilsError(Exception):
    """Custom exception for write operations"""
    pass


def backup_file(file_path: str) -> str:
    """Create a backup of the file before modification"""
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    return backup_path


def read_file_lines(file_path: str) -> List[str]:
    """Read file and return lines as list"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        raise WriteUtilsError(f"Failed to read file {file_path}: {e}")


def write_file_lines(file_path: str, lines: List[str]) -> None:
    """Write lines to file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except Exception as e:
        raise WriteUtilsError(f"Failed to write file {file_path}: {e}")


def find_function_or_class_boundaries(lines: List[str], start_line: int, target_name: str) -> tuple[int, int]:
    """
    Find the start and end lines of a function or class definition.
    Returns (start_line_index, end_line_index) in 0-based indexing.
    """
    # Convert to 0-based indexing
    start_idx = start_line - 1
    
    # Find the actual start of the function/class (handle decorators)
    actual_start = start_idx
    for i in range(start_idx - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('@') or line == '':
            actual_start = i
        else:
            break
    
    # Find the end by looking for the next function/class or end of file
    base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    end_idx = len(lines)
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        
        current_indent = len(line) - len(line.lstrip())
        
        # If we find a line at the same or lower indentation level that's not empty
        if current_indent <= base_indent and line.strip():
            # Check if it's a new function, class, or other top-level construct
            stripped = line.strip()
            if (stripped.startswith('def ') or stripped.startswith('class ') or 
                stripped.startswith('if __name__') or not line.startswith(' ')):
                end_idx = i
                break
    
    return actual_start, end_idx


def add_code(file_path: str, code: str, line_number: Optional[int] = None, after_function: Optional[str] = None, after_class: Optional[str] = None) -> str:
    """
    Add code to a file at a specific location.
    
    Args:
        file_path: Path to the file to modify
        code: Code to add (should include proper indentation and newlines)
        line_number: Specific line number to insert at (1-based)
        after_function: Insert after this function name
        after_class: Insert after this class name
    
    Returns:
        Success message with details of the operation
    """
    if not os.path.exists(file_path):
        raise WriteUtilsError(f"File {file_path} does not exist")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    try:
        lines = read_file_lines(file_path)
        
        # Ensure code ends with newline
        if not code.endswith('\n'):
            code += '\n'
        
        insert_idx = None
        
        if line_number is not None:
            # Insert at specific line number (1-based)
            insert_idx = line_number - 1
            if insert_idx < 0:
                insert_idx = 0
            elif insert_idx > len(lines):
                insert_idx = len(lines)
        
        elif after_function or after_class:
            # Find the function or class and insert after it
            target_name = after_function or after_class
            target_type = 'def' if after_function else 'class'
            
            for i, line in enumerate(lines):
                if f"{target_type} {target_name}" in line:
                    # Find the end of this function/class
                    _, end_idx = find_function_or_class_boundaries(lines, i + 1, target_name)
                    insert_idx = end_idx
                    break
            
            if insert_idx is None:
                raise WriteUtilsError(f"Could not find {target_type} '{target_name}' in {file_path}")
        
        else:
            # Default: append to end of file
            insert_idx = len(lines)
        
        # Insert the code
        lines.insert(insert_idx, code)
        
        # Write back to file
        write_file_lines(file_path, lines)
        
        return f"Successfully added code to {file_path} at line {insert_idx + 1}"
    
    except Exception as e:
        # Restore backup on error
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        raise WriteUtilsError(f"Failed to add code: {e}")


def replace_code(file_path: str, new_code: str, line_number: Optional[int] = None,
                 function_name: Optional[str] = None, class_name: Optional[str] = None,
                 start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Replace code in a file.
    
    Args:
        file_path: Path to the file to modify
        new_code: New code to replace with (should include proper indentation and newlines)
        line_number: Replace single line at this line number (1-based)
        function_name: Replace entire function with this name
        class_name: Replace entire class with this name
        start_line: Start line for range replacement (1-based, inclusive)
        end_line: End line for range replacement (1-based, inclusive)
    
    Returns:
        Success message with details of the operation
    """
    if not os.path.exists(file_path):
        raise WriteUtilsError(f"File {file_path} does not exist")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    try:
        lines = read_file_lines(file_path)
        
        # Ensure new code ends with newline
        if not new_code.endswith('\n'):
            new_code += '\n'
        
        replace_start = None
        replace_end = None
        
        if line_number is not None:
            # Replace single line
            replace_start = line_number - 1
            replace_end = line_number - 1
        
        elif function_name or class_name:
            # Replace entire function or class
            target_name = function_name or class_name
            target_type = 'def' if function_name else 'class'
            
            for i, line in enumerate(lines):
                if f"{target_type} {target_name}" in line:
                    replace_start, replace_end = find_function_or_class_boundaries(lines, i + 1, target_name)
                    replace_end -= 1  # Make it inclusive
                    break
            
            if replace_start is None:
                raise WriteUtilsError(f"Could not find {target_type} '{target_name}' in {file_path}")
        
        elif start_line is not None and end_line is not None:
            # Replace line range
            replace_start = start_line - 1
            replace_end = end_line - 1
        
        else:
            raise WriteUtilsError("Must specify either line_number, function_name, class_name, or start_line/end_line")
        
        # Validate indices
        if replace_start < 0 or replace_end >= len(lines):
            raise WriteUtilsError(f"Line range {replace_start + 1}-{replace_end + 1} is out of bounds")
        
        # Replace the lines
        new_lines = lines[:replace_start] + [new_code] + lines[replace_end + 1:]
        
        # Write back to file
        write_file_lines(file_path, new_lines)
        
        return f"Successfully replaced lines {replace_start + 1}-{replace_end + 1} in {file_path}"
    
    except Exception as e:
        # Restore backup on error
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        raise WriteUtilsError(f"Failed to replace code: {e}")


def delete_code(file_path: str, line_number: Optional[int] = None,
                function_name: Optional[str] = None, class_name: Optional[str] = None,
                start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Delete code from a file.
    
    Args:
        file_path: Path to the file to modify
        line_number: Delete single line at this line number (1-based)
        function_name: Delete entire function with this name
        class_name: Delete entire class with this name
        start_line: Start line for range deletion (1-based, inclusive)
        end_line: End line for range deletion (1-based, inclusive)
    
    Returns:
        Success message with details of the operation
    """
    if not os.path.exists(file_path):
        raise WriteUtilsError(f"File {file_path} does not exist")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    try:
        lines = read_file_lines(file_path)
        
        delete_start = None
        delete_end = None
        
        if line_number is not None:
            # Delete single line
            delete_start = line_number - 1
            delete_end = line_number - 1
        
        elif function_name or class_name:
            # Delete entire function or class
            target_name = function_name or class_name
            target_type = 'def' if function_name else 'class'
            
            for i, line in enumerate(lines):
                if f"{target_type} {target_name}" in line:
                    delete_start, delete_end = find_function_or_class_boundaries(lines, i + 1, target_name)
                    delete_end -= 1  # Make it inclusive
                    break
            
            if delete_start is None:
                raise WriteUtilsError(f"Could not find {target_type} '{target_name}' in {file_path}")
        
        elif start_line is not None and end_line is not None:
            # Delete line range
            delete_start = start_line - 1
            delete_end = end_line - 1
        
        else:
            raise WriteUtilsError("Must specify either line_number, function_name, class_name, or start_line/end_line")
        
        # Validate indices
        if delete_start < 0 or delete_end >= len(lines):
            raise WriteUtilsError(f"Line range {delete_start + 1}-{delete_end + 1} is out of bounds")
        
        # Delete the lines
        new_lines = lines[:delete_start] + lines[delete_end + 1:]
        
        # Write back to file
        write_file_lines(file_path, new_lines)
        
        return f"Successfully deleted lines {delete_start + 1}-{delete_end + 1} from {file_path}"
    
    except Exception as e:
        # Restore backup on error
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        raise WriteUtilsError(f"Failed to delete code: {e}")


def cleanup_backups(directory: str) -> None:
    """Remove all .backup files in the specified directory"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.backup'):
                os.remove(os.path.join(root, file))



# Example Usage:

# test_file = "../example-codebase/main.py"



# this is how you add a function after a function
# print(add_code(test_file, "def new_function():\n    print('New function')\n\n", after_function="subtract"))

# this is how you add a class after a function
# print(add_code(test_file, "class new_class():\n    print('New function')\n\n", after_function="new_function"))

# this is how you add code after a class
# print(add_code(test_file, "num = 2\n\n", after_class = 'HelloWorld'))

# this is how you add code after a line, starts at line 3. because of \n, adds 'nums=2' to line 4
# print(add_code(test_file, "\nnum = 2", line_number = 3))



# this is how you replace a function
# print(replace_code(test_file, "def updated_new_function():\n    print('this is the updated_new_function')\n\n", function_name="new_function"))

# this is how you replace a class
# print(replace_code(test_file, "\nclass updated_new_function():\n    print('this is the updated_new_function')\n\n", class_name="HelloWorld"))

# this is how you replace a line
# print(replace_code(test_file, "num = 3", line_number=4))

# this is how you replace a range of lines
# print(replace_code(test_file, "def multiply(a, b):\n    print("Hi")\n    return a * b", start_line=9, end_line=10))



# this is how you delete a function
# print(delete_code(test_file, function_name="add"))

# this is how you delete a class
# print(delete_code(test_file, class_name="HelloWorld"))

# this is how you delete a line
# print(delete_code(test_file, line_number=15))

# this is how you delete a range of line
# print(delete_code(test_file, start_line=12, end_line=15))