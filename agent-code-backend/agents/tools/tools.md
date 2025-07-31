# Agentic IDE Tools


This toolkit (search_internal.py, write_utils.py, search_external.py) provides utilities for the agentic IDE enabling code discovery, modification, and external resource fetching.
## Overview

- search_internal.py: Searches and analyzes code within a local codebase.
- write_utils.py: Modifies code files by adding, replacing, or deleting code.
- search_external.py: Performs web searches and scrapes content from websites.


## Usage
1. Search Internal Codebase (search_internal.py)
Search and analyze code within a local codebase.

Search for code elements:
from search_internal import find_functions, find_classes, find_imports, find_variables, search_code_patterns

### Find functions named "sum"
```python
print(find_functions("./codebase", "sum", max_results=5))
```

### Find classes named "HelloWorld"
```python
print(find_classes("./codebase", "HelloWorld"))
```

### Find imports of "time"
```python
print(find_imports("./codebase", "time"))
```

### Find variable assignments for "num"
```python
print(find_variables("./codebase", "num"))
```

### Search with regex (e.g., async functions)
```python
print(search_code_patterns("./codebase", r"async\s+def\s+\w+"))
```


List files:
from search_internal import list_files
print(list_files("./codebase", max_depth=2))


Get file content:
from search_internal import get_file_content
print(get_file_content("./codebase/main.py", start_line=1, end_line=20))


Analyze file structure:
from search_internal import analyze_file_structure
print(analyze_file_structure("./codebase/main.py"))



2. Modify Codebase (write_utils.py)
Add, replace, or delete code in files with automatic backups.

Add code:
from write_utils import add_code

# Add function after another function
print(add_code("./codebase/main.py", "def new_function():\n    print('New function')\n\n", after_function="subtract"))

# Add code at specific line
print(add_code("./codebase/main.py", "num = 2\n\n", line_number=3))


Replace code:
from write_utils import replace_code

# Replace a function
print(replace_code("./codebase/main.py", "def updated_function():\n    print('Updated')\n\n", function_name="new_function"))

# Replace a line
print(replace_code("./codebase/main.py", "num = 3", line_number=4))


Delete code:
from write_utils import delete_code

# Delete a function
print(delete_code("./codebase/main.py", function_name="add"))

# Delete a line range
print(delete_code("./codebase/main.py", start_line=12, end_line=15))


Clean up backups:
from write_utils import cleanup_backups
cleanup_backups("./codebase")



3. Search and Scrape Web (search_external.py)
Fetch external resources via web search and scraping.

Search the web:
from search_external import search_external
print(search_external("how to make a calculator in python", max_results=3, search_engine="duckduckgo"))


Scrape a website:
from search_external import scrape_website
print(scrape_website("https://docs.python.org/3/library/asyncio.html", include_metadata=True))


Search and scrape:
from search_external import search_and_scrape
print(search_and_scrape("how to make a calculator in python", max_results=3, scrape_top_results=1))



Example Workflow
To implement a new calculator function:

Search for existing calculator functions:print(find_functions("./codebase", "calculator"))


Search the web for a sample implementation:print(search_and_scrape("python calculator function", max_results=1))


Add the new function to a file:print(add_code("./codebase/main.py", "def calculator(a, b):\n    return"a + b\n\n", after_function="existing_function"))



Notes

Ensure proper indentation in code strings for write_utils.py.
Use relative paths for file operations.
search_external.py requires an internet connection and respects rate limits.
Errors are handled gracefully with backups for file modifications.
