# agents/tools/search_external.py
import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse, quote_plus
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import html2text
from fake_useragent import UserAgent


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    domain: str
    score: float = 0.0


@dataclass
class ScrapedContent:
    url: str
    title: str
    content: str
    links: List[str]
    images: List[str]
    metadata: Dict
    status_code: int
    error: Optional[str] = None


class WebSearcher:
    """Enhanced web search with multiple search engines and rate limiting"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.ua = UserAgent()
        
        # Search engine configurations
        self.search_engines = {
            'duckduckgo': {
                'api_url': 'https://api.duckduckgo.com/',
                'instant_url': 'https://api.duckduckgo.com/',
                'html_url': 'https://html.duckduckgo.com/html/'
            },
            'searx': {
                'instances': [
                    'https://searx.be/',
                    'https://search.sapti.me/',
                    'https://searx.space/'
                ]
            }
        }
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with rotating user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search_duckduckgo_instant(self, query: str) -> Dict:
        """Search using DuckDuckGo Instant Answer API"""
        self._rate_limit()
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.search_engines['duckduckgo']['instant_url'],
                params=params,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            return {'error': str(e)}
    
    def search_duckduckgo_html(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using DuckDuckGo HTML interface"""
        self._rate_limit()
        
        try:
            params = {
                'q': query,
                'b': '',  # Start index
                'kl': 'us-en',  # Region
                'df': '',  # Date filter
            }
            
            response = requests.get(
                self.search_engines['duckduckgo']['html_url'],
                params=params,
                headers=self._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results
            for result_div in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_link = result_div.find('a', class_='result__a')
                    snippet_div = result_div.find('a', class_='result__snippet')
                    
                    if title_link and snippet_div:
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        snippet = snippet_div.get_text(strip=True)
                        domain = urlparse(url).netloc
                        
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            domain=domain
                        ))
                
                except Exception:
                    continue
            
            return results
        
        except Exception as e:
            return [SearchResult(
                title="Search Error",
                url="",
                snippet=f"Error searching DuckDuckGo: {str(e)}",
                domain=""
            )]
    
    def search_searx(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using SearX instances"""
        for instance in self.search_engines['searx']['instances']:
            try:
                self._rate_limit()
                
                params = {
                    'q': query,
                    'categories': 'general',
                    'engines': 'google,bing,yahoo',
                    'format': 'json',
                    'pageno': 1
                }
                
                response = requests.get(
                    f"{instance}search",
                    params=params,
                    headers=self._get_headers(),
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get('results', [])[:max_results]:
                    results.append(SearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        snippet=item.get('content', ''),
                        domain=urlparse(item.get('url', '')).netloc,
                        score=item.get('score', 0.0)
                    ))
                
                return results
            
            except Exception:
                continue  # Try next instance
        
        return [SearchResult(
            title="Search Error",
            url="",
            snippet="All SearX instances failed",
            domain=""
        )]


class WebScraper:
    """Enhanced web scraper with content extraction and rate limiting"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.ua = UserAgent()
        
        # Configure html2text properly
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.ignore_images = True
        self.html2text.body_width = 0  # Don't wrap lines
        self.html2text.unicode_snob = True
        self.html2text.decode_errors = 'ignore'
        
        # Common selectors for content extraction - improved order
        self.content_selectors = [
            'main',
            'article', 
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.article-body',
            '.story-body',
            '.post',
            '.entry',
            '.page-content',
            'section.content'
        ]
        
        # Selectors to remove (ads, navigation, etc.)
        self.remove_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.sidebar', '.navigation', '.nav',
            '.advertisement', '.ads', '.ad',
            '.social', '.social-share',
            '.comments', '.comment',
            '.related', '.recommended',
            '.popup', '.modal',
            'script', 'style', 'noscript',
            '.cookie-notice', '.cookie-banner',
            '.newsletter', '.subscription'
        ]
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with rotating user agent"""
        try:
            user_agent = self.ua.random
        except:
            # Fallback if fake_useragent fails
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    
    def _clean_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted elements from parsed HTML"""
        # Remove unwanted elements
        for selector in self.remove_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        # Remove elements with common ad/tracking attributes
        for element in soup.find_all(attrs={'class': re.compile(r'ad|advertisement|banner|popup|modal', re.I)}):
            element.decompose()
        
        for element in soup.find_all(attrs={'id': re.compile(r'ad|advertisement|banner|popup|modal', re.I)}):
            element.decompose()
        
        return soup
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content using various strategies"""
        # Strategy 1: Look for common content containers
        for selector in self.content_selectors:
            try:
                content_elements = soup.select(selector)
                for content_div in content_elements:
                    if content_div:
                        text = content_div.get_text(strip=True)
                        if len(text) > 300:  # Minimum meaningful content length
                            # Convert to markdown and clean up
                            markdown_content = self.html2text.handle(str(content_div))
                            # Clean up excessive whitespace
                            cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
                            cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)
                            return cleaned_content.strip()
            except Exception:
                continue
        
        # Strategy 2: Find paragraphs with substantial content
        paragraphs = soup.find_all('p')
        if paragraphs:
            content_blocks = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Skip very short paragraphs
                    content_blocks.append(text)
            
            if content_blocks:
                return '\n\n'.join(content_blocks)
        
        # Strategy 3: Find the largest text containers
        text_containers = []
        for tag in ['div', 'section', 'article', 'main']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if len(text) > 200:
                    # Avoid nested containers by checking if this text is mostly unique
                    is_unique = True
                    for existing_text in [t[1] for t in text_containers]:
                        if text in existing_text or existing_text in text:
                            is_unique = False
                            break
                    
                    if is_unique:
                        text_containers.append((len(text), text))
        
        if text_containers:
            text_containers.sort(reverse=True, key=lambda x: x[0])
            return text_containers[0][1]
        
        # Strategy 4: Fall back to body content, cleaned
        body = soup.find('body')
        if body:
            # Remove common noise elements from body
            for noise in body.select('script, style, nav, header, footer, .ad, .advertisement'):
                noise.decompose()
            
            text = body.get_text(separator='\n', strip=True)
            # Clean up excessive whitespace
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            return text
        
        # Strategy 5: Everything as last resort
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    def scrape_url(self, url: str, extract_links: bool = True, 
                   extract_images: bool = True, max_content_length: int = 50000) -> ScrapedContent:
        """Scrape a single URL and return structured content"""
        self._rate_limit()
        
        try:
            # Add session for better handling
            session = requests.Session()
            session.headers.update(self._get_headers())
            
            response = session.get(
                url,
                timeout=20,
                allow_redirects=True,
                verify=True
            )
            
            # Handle different status codes
            if response.status_code != 200:
                return ScrapedContent(
                    url=url,
                    title="",
                    content="",
                    links=[],
                    images=[],
                    metadata={},
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}: {response.reason}"
                )
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return ScrapedContent(
                    url=url,
                    title="",
                    content="",
                    links=[],
                    images=[],
                    metadata={},
                    status_code=response.status_code,
                    error=f"Non-HTML content type: {content_type}"
                )
            
            # Parse HTML with better encoding handling
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
            
            # Clean the content
            soup = self._clean_content(soup)
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Also try og:title as fallback
            if not title:
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    title = og_title.get('content', '').strip()
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Limit content length
            if len(content) > max_content_length:
                content = content[:max_content_length] + "\n\n[Content truncated due to length...]"
            
            # Extract links
            links = []
            if extract_links:
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()
                    if href:
                        if href.startswith('http'):
                            links.append(href)
                        elif href.startswith('/'):
                            links.append(urljoin(url, href))
                        elif not href.startswith('#') and not href.startswith('mailto:'):
                            # Relative link
                            links.append(urljoin(url, href))
            
            # Extract images
            images = []
            if extract_images:
                for img in soup.find_all('img', src=True):
                    src = img['src'].strip()
                    if src:
                        if src.startswith('http'):
                            images.append(src)
                        elif src.startswith('/'):
                            images.append(urljoin(url, src))
                        else:
                            images.append(urljoin(url, src))
            
            # Extract metadata
            metadata = {}
            
            # Meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content_attr = meta.get('content')
                if name and content_attr:
                    metadata[name] = content_attr.strip()
            
            # Add some basic page info
            metadata['scraped_url'] = url
            metadata['content_length'] = len(content)
            metadata['links_found'] = len(links)
            metadata['images_found'] = len(images)
            
            return ScrapedContent(
                url=url,
                title=title,
                content=content,
                links=list(dict.fromkeys(links))[:20],  # Remove duplicates and limit
                images=list(dict.fromkeys(images))[:10],  # Remove duplicates and limit
                metadata=metadata,
                status_code=response.status_code
            )
        
        except requests.RequestException as e:
            return ScrapedContent(
                url=url,
                title="",
                content="",
                links=[],
                images=[],
                metadata={},
                status_code=0,
                error=f"Request error: {str(e)}"
            )
        except Exception as e:
            return ScrapedContent(
                url=url,
                title="",
                content="",
                links=[],
                images=[],
                metadata={},
                status_code=0,
                error=f"Scraping error: {str(e)}"
            )


# Main interface functions
def search_external(query: str, max_results: int = 1, search_engine: str = 'duckduckgo') -> str:
    """
    Perform external web search and return formatted results.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        search_engine: Search engine to use ('duckduckgo', 'searx', 'all')
    
    Returns:
        Formatted search results as string
    """
    searcher = WebSearcher()
    all_results = []
    
    if search_engine == 'duckduckgo' or search_engine == 'all':
        # Try instant answer first
        instant_result = searcher.search_duckduckgo_instant(query)
        
        if not instant_result.get('error') and instant_result.get('AbstractText'):
            return f"🔍 Quick Answer for '{query}':\n{instant_result['AbstractText']}\n\nSource: {instant_result.get('AbstractURL', 'DuckDuckGo')}"
        
        # Fall back to HTML search
        ddg_results = searcher.search_duckduckgo_html(query, max_results)
        all_results.extend(ddg_results)
    
    if search_engine == 'searx' or search_engine == 'all':
        searx_results = searcher.search_searx(query, max_results)
        all_results.extend(searx_results)
    
    if not all_results:
        return f"No search results found for: {query}"
    
    # Remove duplicates and sort by relevance
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result.url not in seen_urls:
            seen_urls.add(result.url)
            unique_results.append(result)
    
    # Limit results
    unique_results = unique_results[:max_results]
    
    # Format output
    result_lines = []
    result_lines.append(f"🌐 Search Results for '{query}' ({len(unique_results)} results)")
    result_lines.append("=" * 60)
    
    for i, result in enumerate(unique_results, 1):
        result_lines.append(f"\n[{i}] {result.title}")
        result_lines.append(f"    URL: {result.url}")
        result_lines.append(f"    Domain: {result.domain}")
        if result.snippet:
            snippet = result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet
            result_lines.append(f"    Summary: {snippet}")
    
    return '\n'.join(result_lines)


def scrape_website(url: str, include_links: bool = False, include_metadata: bool = False) -> str:
    """
    Scrape a website and return formatted content.
    
    Args:
        url: URL to scrape
        include_links: Whether to include extracted links
        include_metadata: Whether to include page metadata
    
    Returns:
        Formatted scraped content as string
    """
    scraper = WebScraper()
    scraped = scraper.scrape_url(url, extract_links=include_links, extract_images=False)
    
    if scraped.error:
        return f"❌ Error scraping {url}: {scraped.error}"
    
    result_lines = []
    result_lines.append(f"📄 Scraped Content from: {url}")
    result_lines.append("=" * 60)
    
    if scraped.title:
        result_lines.append(f"Title: {scraped.title}")
        result_lines.append("")
    
    if scraped.content:
        # Show more content but still limit for display
        content = scraped.content[:8000] + "\n\n[Content truncated for display...]" if len(scraped.content) > 8000 else scraped.content
        result_lines.append("Content:")
        result_lines.append("-" * 30)
        result_lines.append(content)
    else:
        result_lines.append("⚠️  No content extracted")
    
    if include_metadata and scraped.metadata:
        result_lines.append("\nMetadata:")
        result_lines.append("-" * 30)
        for key, value in list(scraped.metadata.items())[:15]:  # Show more metadata
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            result_lines.append(f"{key}: {value}")
    
    if include_links and scraped.links:
        result_lines.append(f"\nExtracted Links ({len(scraped.links)}):")
        result_lines.append("-" * 30)
        for link in scraped.links[:15]:  # Show more links
            result_lines.append(f"• {link}")
    
    return '\n'.join(result_lines)


def search_and_scrape(query: str, max_results: int = 1, scrape_top_results: int = 1) -> str:
    """
    Search and then scrape top results for comprehensive information.
    
    Args:
        query: Search query
        max_results: Maximum search results to get
        scrape_top_results: Number of top results to scrape
    
    Returns:
        Combined search and scrape results
    """
    # First search
    search_results = search_external(query, max_results)
    
    if "No search results found" in search_results:
        return search_results
    
    # Extract URLs from search results
    urls = []
    for line in search_results.split('\n'):
        if line.strip().startswith('URL: '):
            url = line.strip()[5:]
            urls.append(url)
    
    if not urls:
        return search_results + "\n\n❌ No URLs found to scrape"
    
    # Scrape top results
    combined_results = [search_results]
    combined_results.append("\n" + "="*60)
    combined_results.append("📄 SCRAPED CONTENT FROM TOP RESULTS")
    combined_results.append("="*60)
    
    for i, url in enumerate(urls[:scrape_top_results], 1):
        combined_results.append(f"\n--- Result {i}: Scraping {url} ---")
        scraped_content = scrape_website(url, include_links=False, include_metadata=False)
        combined_results.append(scraped_content)
    
    return '\n'.join(combined_results)


# Example usage and testing
if __name__ == "__main__":
    # print("=== Testing Website Scraping ===")
    # scraped = scrape_website("https://docs.python.org/3/library/asyncio.html", include_metadata=True)
    # print(scraped[:2000] + "..." if len(scraped) > 2000 else scraped)
    
    # print(search_external("how to impletement a calculator in python")) # this is how you search for websites 

    print(search_and_scrape("how to make a calculator in python"))