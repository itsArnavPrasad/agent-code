import os
from pathlib import Path
import requests

def search_internal(codebase_dir: str, query: str) -> str:
    """
    Perform a basic grep-like search over files in the codebase.
    Returns the matching lines with file references.
    """
    matches = []
    for root, _, files in os.walk(codebase_dir):
        for fname in files:
            if fname.endswith('.py'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r') as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if query.lower() in line.lower():
                            matches.append(f'{fpath}:{idx + 1}: {line.strip()}')
                except Exception as e:
                    print(f'Error reading {fpath}: {e}')
    if not matches:
        return f'No internal matches found for: {query}'
    return '\n'.join(matches)

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

