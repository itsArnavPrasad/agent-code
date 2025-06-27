import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class SearchMode(Enum):
    CONTAINS = "contains"
    REGEX = "regex"
    EXACT = "exact"
    FUNCTION_DEF = "function_def"
    CLASS_DEF = "class_def"
    IMPORT = "import"
    VARIABLE_ASSIGNMENT = "variable_assignment"


@dataclass
class SearchMatch:
    file_path: str
    line_number: int
    line_content: str
    context_before: List[str]
    context_after: List[str]
    match_type: str
    confidence: float = 1.0


class CodebaseSearcher:
    def __init__(self, codebase_dir: str, file_extensions: List[str] = None):
        self.codebase_dir = codebase_dir
        self.file_extensions = file_extensions or ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h']
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', 'dist', 'build'}
        self.ignore_files = {'.pyc', '.pyo', '.pyd', '.so', '.dll'}
    
    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed based on extension and ignore patterns"""
        path_obj = Path(file_path)
        
        # Check if any parent directory should be ignored
        for part in path_obj.parts:
            if part in self.ignore_dirs:
                return False
        
        # Check file extension
        if not any(file_path.endswith(ext) for ext in self.file_extensions):
            return False
            
        # Check if file itself should be ignored
        if any(file_path.endswith(ignore) for ignore in self.ignore_files):
            return False
            
        return True
    
    def get_context_lines(self, lines: List[str], match_idx: int, context_size: int = 3) -> Tuple[List[str], List[str]]:
        """Get context lines before and after the match"""
        start = max(0, match_idx - context_size)
        end = min(len(lines), match_idx + context_size + 1)
        
        context_before = [lines[i].rstrip() for i in range(start, match_idx)]
        context_after = [lines[i].rstrip() for i in range(match_idx + 1, end)]
        
        return context_before, context_after
    
    def search_contains(self, query: str, content: str, case_sensitive: bool = False) -> bool:
        """Basic contains search"""
        if case_sensitive:
            return query in content
        return query.lower() in content.lower()
    
    def search_regex(self, pattern: str, content: str, flags: int = re.IGNORECASE) -> bool:
        """Regex search"""
        try:
            return bool(re.search(pattern, content, flags))
        except re.error:
            return False
    
    def search_function_def(self, query: str, content: str) -> bool:
        """Search for function definitions"""
        patterns = [
            rf'def\s+{re.escape(query)}\s*\(',  # Python
            rf'function\s+{re.escape(query)}\s*\(',  # JavaScript
            rf'{re.escape(query)}\s*\([^)]*\)\s*{{',  # Java/C++/C
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def search_class_def(self, query: str, content: str) -> bool:
        """Search for class definitions"""
        patterns = [
            rf'class\s+{re.escape(query)}[\s\(:]',  # Python
            rf'class\s+{re.escape(query)}\s*{{',  # Java/C++
            rf'interface\s+{re.escape(query)}\s*{{',  # Java/TypeScript
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def search_import(self, query: str, content: str) -> bool:
        """Search for import statements"""
        patterns = [
            rf'import\s+.*{re.escape(query)}',
            rf'from\s+.*{re.escape(query)}',
            rf'#include\s*[<"]{re.escape(query)}',
            rf'require\s*\(\s*[\'"{re.escape(query)}]',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def search_variable_assignment(self, query: str, content: str) -> bool:
        """Search for variable assignments"""
        patterns = [
            rf'{re.escape(query)}\s*=',
            rf'let\s+{re.escape(query)}\s*=',
            rf'const\s+{re.escape(query)}\s*=',
            rf'var\s+{re.escape(query)}\s*=',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def calculate_relevance_score(self, match: SearchMatch, query: str) -> float:
        """Calculate relevance score for ranking results"""
        score = 1.0
        line = match.line_content.lower()
        query_lower = query.lower()
        
        # Exact match gets highest score
        if query_lower == line.strip():
            score = 5.0
        # Function/class definitions get high scores
        elif 'def ' in line or 'class ' in line:
            score = 4.0
        # Beginning of line matches are more relevant
        elif line.strip().startswith(query_lower):
            score = 3.0
        # Word boundary matches are more relevant than substring matches
        elif re.search(rf'\b{re.escape(query_lower)}\b', line):
            score = 2.5
        # Multiple occurrences of query
        score += line.count(query_lower) * 0.1
        
        return score


def search_internal(codebase_dir: str, query: str, mode: SearchMode = SearchMode.CONTAINS,
                   context_lines: int = 3, max_results: int = 50, 
                   case_sensitive: bool = False, file_extensions: List[str] = None,
                   include_context: bool = True, sort_by_relevance: bool = True) -> str:
    """
    Enhanced search function for codebase analysis.
    
    Args:
        codebase_dir: Directory to search in
        query: Search query/pattern
        mode: Search mode (contains, regex, exact, function_def, class_def, import, variable_assignment)
        context_lines: Number of context lines to include before/after match
        max_results: Maximum number of results to return
        case_sensitive: Whether search should be case sensitive
        file_extensions: List of file extensions to search (default: common code files)
        include_context: Whether to include context lines in output
        sort_by_relevance: Whether to sort results by relevance score
    
    Returns:
        Formatted search results as string
    """
    if not os.path.exists(codebase_dir):
        return f"Error: Directory {codebase_dir} does not exist"
    
    searcher = CodebaseSearcher(codebase_dir, file_extensions)
    matches = []
    
    # Search through all files
    for root, dirs, files in os.walk(codebase_dir):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in searcher.ignore_dirs]
        
        for fname in files:
            fpath = os.path.join(root, fname)
            
            if not searcher.should_process_file(fpath):
                continue
            
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for idx, line in enumerate(lines):
                    line_content = line.rstrip()
                    match_found = False
                    match_type = mode.value
                    
                    # Apply search based on mode
                    if mode == SearchMode.CONTAINS:
                        match_found = searcher.search_contains(query, line_content, case_sensitive)
                    elif mode == SearchMode.REGEX:
                        match_found = searcher.search_regex(query, line_content)
                    elif mode == SearchMode.EXACT:
                        if case_sensitive:
                            match_found = query == line_content.strip()
                        else:
                            match_found = query.lower() == line_content.strip().lower()
                    elif mode == SearchMode.FUNCTION_DEF:
                        match_found = searcher.search_function_def(query, line_content)
                    elif mode == SearchMode.CLASS_DEF:
                        match_found = searcher.search_class_def(query, line_content)
                    elif mode == SearchMode.IMPORT:
                        match_found = searcher.search_import(query, line_content)
                    elif mode == SearchMode.VARIABLE_ASSIGNMENT:
                        match_found = searcher.search_variable_assignment(query, line_content)
                    
                    if match_found:
                        context_before, context_after = searcher.get_context_lines(lines, idx, context_lines)
                        
                        match = SearchMatch(
                            file_path=fpath,
                            line_number=idx + 1,
                            line_content=line_content,
                            context_before=context_before,
                            context_after=context_after,
                            match_type=match_type
                        )
                        
                        # Calculate relevance score
                        match.confidence = searcher.calculate_relevance_score(match, query)
                        matches.append(match)
                        
                        # Stop if we hit max results (before sorting)
                        if len(matches) >= max_results * 2:  # Get more for better sorting
                            break
            
            except Exception as e:
                print(f'Error reading {fpath}: {e}')
                continue
    
    if not matches:
        return f'No matches found for: "{query}" (mode: {mode.value})'
    
    # Sort by relevance if requested
    if sort_by_relevance:
        matches.sort(key=lambda x: x.confidence, reverse=True)
    
    # Limit results
    matches = matches[:max_results]
    
    # Format output
    result_lines = []
    result_lines.append(f"Found {len(matches)} matches for '{query}' (mode: {mode.value})")
    result_lines.append("=" * 60)
    
    for i, match in enumerate(matches, 1):
        # Make file path relative to codebase_dir for cleaner output
        rel_path = os.path.relpath(match.file_path, codebase_dir)
        
        result_lines.append(f"\n[{i}] {rel_path}:{match.line_number} (score: {match.confidence:.1f})")
        
        if include_context and match.context_before:
            result_lines.append("  Context before:")
            for j, ctx_line in enumerate(match.context_before):
                line_num = match.line_number - len(match.context_before) + j
                result_lines.append(f"  {line_num:4d}: {ctx_line}")
        
        # Highlight the matching line
        result_lines.append(f"➤ {match.line_number:4d}: {match.line_content}")
        
        if include_context and match.context_after:
            result_lines.append("  Context after:")
            for j, ctx_line in enumerate(match.context_after):
                line_num = match.line_number + j + 1
                result_lines.append(f"  {line_num:4d}: {ctx_line}")
    
    return '\n'.join(result_lines)


# Convenience functions for common search patterns
def find_functions(codebase_dir: str, function_name: str, **kwargs) -> str:
    """Find function definitions"""
    return search_internal(codebase_dir, function_name, SearchMode.FUNCTION_DEF, **kwargs)


def find_classes(codebase_dir: str, class_name: str, **kwargs) -> str:
    """Find class definitions"""
    return search_internal(codebase_dir, class_name, SearchMode.CLASS_DEF, **kwargs)


def find_imports(codebase_dir: str, import_name: str, **kwargs) -> str:
    """Find import statements"""
    return search_internal(codebase_dir, import_name, SearchMode.IMPORT, **kwargs)


def find_variables(codebase_dir: str, variable_name: str, **kwargs) -> str:
    """Find variable assignments"""
    return search_internal(codebase_dir, variable_name, SearchMode.VARIABLE_ASSIGNMENT, **kwargs)


def search_code_patterns(codebase_dir: str, regex_pattern: str, **kwargs) -> str:
    """Search using regex patterns"""
    return search_internal(codebase_dir, regex_pattern, SearchMode.REGEX, **kwargs)


def get_file_content(file_path: str, with_line_numbers: bool = True, 
                    start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Get the complete content of a file or a specific range.
    
    Args:
        file_path: Path to the file
        with_line_numbers: Whether to include line numbers
        start_line: Start line number (1-based, inclusive)
        end_line: End line number (1-based, inclusive)
    
    Returns:
        File content as formatted string
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} does not exist"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Apply line range if specified
        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            lines = lines[start_idx:end_idx]
            line_offset = start_idx
        else:
            line_offset = 0
        
        result_lines = []
        result_lines.append(f"File: {file_path}")
        if start_line or end_line:
            result_lines.append(f"Lines: {start_line or 1}-{end_line or len(lines) + line_offset}")
        result_lines.append("=" * 60)
        
        for i, line in enumerate(lines):
            line_num = i + 1 + line_offset
            if with_line_numbers:
                result_lines.append(f"{line_num:4d}: {line.rstrip()}")
            else:
                result_lines.append(line.rstrip())
        
        return '\n'.join(result_lines)
    
    except Exception as e:
        return f"Error reading file {file_path}: {e}"


def list_files(codebase_dir: str, file_extensions: List[str] = None, 
               include_hidden: bool = False, max_depth: Optional[int] = None) -> str:
    """
    List all files in the codebase with their relative paths and sizes.
    
    Args:
        codebase_dir: Directory to search
        file_extensions: File extensions to include (default: common code files)
        include_hidden: Whether to include hidden files/directories
        max_depth: Maximum directory depth to traverse
    
    Returns:
        Formatted list of files
    """
    if not os.path.exists(codebase_dir):
        return f"Error: Directory {codebase_dir} does not exist"
    
    searcher = CodebaseSearcher(codebase_dir, file_extensions)
    files_info = []
    
    for root, dirs, files in os.walk(codebase_dir):
        # Calculate current depth
        if max_depth is not None:
            current_depth = root[len(codebase_dir):].count(os.sep)
            if current_depth >= max_depth:
                dirs.clear()  # Don't go deeper
                continue
        
        # Filter directories
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in searcher.ignore_dirs]
        else:
            dirs[:] = [d for d in dirs if d not in searcher.ignore_dirs]
        
        for fname in files:
            if not include_hidden and fname.startswith('.'):
                continue
                
            fpath = os.path.join(root, fname)
            
            if searcher.should_process_file(fpath):
                rel_path = os.path.relpath(fpath, codebase_dir)
                try:
                    file_size = os.path.getsize(fpath)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                    
                    files_info.append({
                        'path': rel_path,
                        'size': file_size,
                        'lines': line_count
                    })
                except Exception:
                    files_info.append({
                        'path': rel_path,
                        'size': 0,
                        'lines': 0
                    })
    
    if not files_info:
        return "No files found matching criteria"
    
    # Sort by path
    files_info.sort(key=lambda x: x['path'])
    
    result_lines = []
    result_lines.append(f"Files in {codebase_dir} ({len(files_info)} files)")
    result_lines.append("=" * 60)
    result_lines.append(f"{'Path':<50} {'Lines':<8} {'Size':<10}")
    result_lines.append("-" * 70)
    
    for file_info in files_info:
        size_str = f"{file_info['size']} B" if file_info['size'] < 1024 else f"{file_info['size']//1024} KB"
        result_lines.append(f"{file_info['path']:<50} {file_info['lines']:<8} {size_str:<10}")
    
    return '\n'.join(result_lines)


def analyze_file_structure(file_path: str) -> str:
    """
    Analyze the structure of a file (functions, classes, imports, etc.)
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        Structured analysis of the file
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} does not exist"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        analysis = {
            'imports': [],
            'functions': [],
            'classes': [],
            'variables': [],
            'comments': [],
            'total_lines': len(lines)
        }
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Imports
            if (stripped.startswith('import ') or stripped.startswith('from ') or 
                stripped.startswith('#include') or stripped.startswith('require(')):
                analysis['imports'].append({'line': i, 'content': stripped})
            
            # Functions
            elif (stripped.startswith('def ') or stripped.startswith('function ') or 
                  re.match(r'^\w+\s*\([^)]*\)\s*{', stripped)):
                analysis['functions'].append({'line': i, 'content': stripped})
            
            # Classes
            elif (stripped.startswith('class ') or stripped.startswith('interface ') or
                  re.match(r'^class\s+\w+', stripped)):
                analysis['classes'].append({'line': i, 'content': stripped})
            
            # Variable assignments (simple detection)
            elif ('=' in stripped and not any(op in stripped for op in ['==', '!=', '<=', '>=', '=>'])):
                if not stripped.startswith(('#', '//', '/*')):
                    analysis['variables'].append({'line': i, 'content': stripped})
            
            # Comments
            elif (stripped.startswith('#') or stripped.startswith('//') or 
                  stripped.startswith('/*') or stripped.startswith('"""') or stripped.startswith("'''")):
                analysis['comments'].append({'line': i, 'content': stripped[:50] + '...' if len(stripped) > 50 else stripped})
        
        # Format output
        result_lines = []
        result_lines.append(f"File Structure Analysis: {file_path}")
        result_lines.append("=" * 60)
        result_lines.append(f"Total Lines: {analysis['total_lines']}")
        result_lines.append("")
        
        for category, items in analysis.items():
            if category == 'total_lines' or not items:
                continue
            
            result_lines.append(f"{category.upper()} ({len(items)}):")
            result_lines.append("-" * 30)
            for item in items[:10]:  # Limit to first 10 items
                result_lines.append(f"  Line {item['line']:4d}: {item['content']}")
            if len(items) > 10:
                result_lines.append(f"  ... and {len(items) - 10} more")
            result_lines.append("")
        
        return '\n'.join(result_lines)
    
    except Exception as e:
        return f"Error analyzing file {file_path}: {e}"


# Example usage
if __name__ == "__main__":
    # Test the enhanced search
    codebase = ".."
    
    # print("=== Function Search ===")
    # print(find_functions(codebase, "sum", max_results=5))

    # print("=== Classes Search ===")
    # print(find_classes(codebase, "HelloWorld", max_results=5))

    # print("=== Imports Search ===")
    # print(find_imports(codebase, "time", max_results=5))

    # print("=== Variables Search ===")
    # print(find_variables(codebase, "num", max_results=5))

    # print("=== Pattern Search ===")
    # print(search_code_patterns(codebase, r"async\s+def\s+\w+", max_results=2))
    
    # print("\n=== File Listing ===")
    # print(list_files(codebase, max_depth=2)) # remove max_depth to get all files
    
    # print("\n=== File Content ===")
    # print(get_file_content("../example-codebase/main.py", start_line=1, end_line=20)) # this will get only 1-20 lines
    # print(get_file_content("../example-codebase/main.py"))





def search_external(query: str) -> str:
    """
    Perform a simple web search using DuckDuckGo Instant Answer API or fallback to scraping.
    Returns a string summary or top search links.
    """
    try:
        url = f'https://api.duckduckgo.com/?q={query}&format=json&no_html=1'
        res = requests.get(url)
        data = res.json()
        if data.get('AbstractText'):
            return f"🔍 DuckDuckGo Summary:\n{data['AbstractText']}"
        elif data.get('RelatedTopics'):
            links = [item['FirstURL'] for item in data['RelatedTopics'] if 'FirstURL' in item][:3]
            return '🔗 Top Results:\n' + '\n'.join(links)
    except Exception as e:
        return f'Search failed: {str(e)}'
    return 'No useful results found.'

