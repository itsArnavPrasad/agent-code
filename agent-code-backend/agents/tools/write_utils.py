import ast
import os
from typing import Optional, Dict, Any

def internal_write(file_path: str, operation: str, **kwargs) -> str:
    """
    Modify Python files in-place using AST manipulation.
    
    Args:
        file_path: Path to the Python file to modify
        operation: Type of modification ('add_function', 'modify_function', 'add_import', 'modify_class', etc.)
        **kwargs: Operation-specific parameters
    
    Returns:
        Status message indicating success or failure
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} does not exist"
    
    if not file_path.endswith('.py'):
        return f"Error: File {file_path} is not a Python file"
    
    try:
        # Read the original file
        with open(file_path, 'r') as f:
            original_content = f.read()
        
        # Parse the AST
        tree = ast.parse(original_content)
        
        # Apply the modification based on operation type
        if operation == "add_function":
            result = _add_function(tree, original_content, **kwargs)
        elif operation == "modify_function":
            result = _modify_function(tree, original_content, **kwargs)
        elif operation == "add_import":
            result = _add_import(tree, original_content, **kwargs)
        elif operation == "modify_class":
            result = _modify_class(tree, original_content, **kwargs)
        elif operation == "replace_line":
            result = _replace_line(original_content, **kwargs)
        elif operation == "insert_code":
            result = _insert_code(original_content, **kwargs)
        else:
            return f"Error: Unknown operation '{operation}'"
        
        if result.startswith("Error:"):
            return result
        
        # Write the modified content back to file
        with open(file_path, 'w') as f:
            f.write(result)
        
        return f"Success: Modified {file_path} with operation '{operation}'"
    
    except SyntaxError as e:
        return f"Error: Syntax error in {file_path}: {e}"
    except Exception as e:
        return f"Error: Failed to modify {file_path}: {e}"


def _add_function(tree: ast.AST, function_code: str, insert_after: Optional[str] = None) -> str:
    """Add a new function to the file."""
    try:
        # Parse the new function
        func_tree = ast.parse(function_code)
        if not func_tree.body or not isinstance(func_tree.body[0], ast.FunctionDef):
            return "Error: Invalid function code provided"
        
        new_func = func_tree.body[0]
        
        # Find insertion point
        if insert_after:
            for i, node in enumerate(tree.body):
                if (isinstance(node, ast.FunctionDef) and node.name == insert_after) or \
                   (isinstance(node, ast.ClassDef) and node.name == insert_after):
                    tree.body.insert(i + 1, new_func)
                    break
            else:
                return f"Error: Could not find function/class '{insert_after}' to insert after"
        else:
            # Add at the end
            tree.body.append(new_func)
        
        return ast.unparse(tree)
    except Exception as e:
        return f"Error: Failed to add function: {e}"


def _modify_function(tree: ast.AST, function_name: str, new_body: str) -> str:
    """Modify an existing function's body."""
    try:
        # Parse the new function body
        new_func_tree = ast.parse(new_body)
        if not new_func_tree.body or not isinstance(new_func_tree.body[0], ast.FunctionDef):
            return "Error: Invalid function code provided"
        
        new_func = new_func_tree.body[0]
        
        # Find and replace the function
        for i, node in enumerate(tree.body):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Keep the original function signature if new one doesn't specify
                if new_func.name != function_name:
                    new_func.name = function_name
                tree.body[i] = new_func
                return ast.unparse(tree)
        
        # Also check inside classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for i, method in enumerate(node.body):
                    if isinstance(method, ast.FunctionDef) and method.name == function_name:
                        if new_func.name != function_name:
                            new_func.name = function_name
                        node.body[i] = new_func
                        return ast.unparse(tree)
        
        return f"Error: Function '{function_name}' not found"
    except Exception as e:
        return f"Error: Failed to modify function: {e}"


def _add_import(tree: ast.AST, module: str, alias: Optional[str] = None, from_module: Optional[str] = None) -> str:
    """Add an import statement."""
    try:
        if from_module:
            # from module import name
            new_import = ast.ImportFrom(
                module=from_module,
                names=[ast.alias(name=module, asname=alias)],
                level=0
            )
        else:
            # import module
            new_import = ast.Import(
                names=[ast.alias(name=module, asname=alias)]
            )
        
        # Check if import already exists
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import) and not from_module:
                    for alias_node in node.names:
                        if alias_node.name == module:
                            return f"Import '{module}' already exists"
                elif isinstance(node, ast.ImportFrom) and from_module:
                    if node.module == from_module:
                        for alias_node in node.names:
                            if alias_node.name == module:
                                return f"Import 'from {from_module} import {module}' already exists"
        
        # Insert import at the beginning (after docstrings)
        insert_pos = 0
        for i, node in enumerate(tree.body):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                insert_pos = i + 1  # After docstring
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_pos = i + 1  # After existing imports
            else:
                break
        
        tree.body.insert(insert_pos, new_import)
        return ast.unparse(tree)
    except Exception as e:
        return f"Error: Failed to add import: {e}"


def _modify_class(tree: ast.AST, class_name: str, method_name: str, method_code: str) -> str:
    """Add or modify a method in a class."""
    try:
        # Parse the new method
        method_tree = ast.parse(method_code)
        if not method_tree.body or not isinstance(method_tree.body[0], ast.FunctionDef):
            return "Error: Invalid method code provided"
        
        new_method = method_tree.body[0]
        
        # Find the class
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Check if method already exists
                for i, method in enumerate(node.body):
                    if isinstance(method, ast.FunctionDef) and method.name == method_name:
                        node.body[i] = new_method
                        return ast.unparse(tree)
                # Method doesn't exist, add it
                node.body.append(new_method)
                return ast.unparse(tree)
        
        return f"Error: Class '{class_name}' not found"
    except Exception as e:
        return f"Error: Failed to modify class: {e}"


def _replace_line(original_content: str, line_number: int, new_content: str) -> str:
    """Replace a specific line number with new content."""
    try:
        lines = original_content.split('\n')
        if line_number < 1 or line_number > len(lines):
            return f"Error: Line number {line_number} is out of range (1-{len(lines)})"
        
        lines[line_number - 1] = new_content
        return '\n'.join(lines)
    except Exception as e:
        return f"Error: Failed to replace line: {e}"


def _insert_code(original_content: str, line_number: int, code: str) -> str:
    """Insert code at a specific line number."""
    try:
        lines = original_content.split('\n')
        if line_number < 1 or line_number > len(lines) + 1:
            return f"Error: Line number {line_number} is out of range (1-{len(lines) + 1})"
        
        lines.insert(line_number - 1, code)
        return '\n'.join(lines)
    except Exception as e:
        return f"Error: Failed to insert code: {e}"


# Example usage functions for your agents:

def add_function_example():
    """Example: Add a new function to a file"""
    new_function = '''def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b'''
    
    result = internal_write(
        file_path="../example-codebase/main.py",
        operation="add_function",
        function_name="calculate_sum",
        function_code=new_function,
        # insert_after="existing_function"  # Optional
    )
    print('done')
    return result

def modify_function_example():
    """Example: Modify an existing function"""
    modified_function = '''def existing_function(x: int) -> int:
    """Modified function with new logic."""
    print(f"Processing {x}")
    return x * 2 + 1'''
    
    result = internal_write(
        file_path="../example-codebase/main.py",
        operation="modify_function",
        function_name="calculate_sum",
        new_body=modified_function
    )
    return result

def add_import_example():
    """Example: Add import statements"""
    # Regular import
    result1 = internal_write(
        file_path="../example-codebase/main.py",
        operation="add_import",
        module="json"
    )
    
    # From import
    result2 = internal_write(
        file_path="../example-codebase/main.py",
        operation="add_import",
        module="Dict",
        from_module="typing"
    )
    
    return result1, result2

# print(add_function_example())
# print(modify_function_example())
# print(add_import_example())
