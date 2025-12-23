"""
Web Scraper Module - Google Search Automation
Handles automated Google search and text extraction using Selenium.

This module provides:
- Automated browser control via Selenium WebDriver
- Google search query execution
- Multi-page result pagination
- Visible text extraction from search results
- Rate limiting and delays to avoid blocking
"""

import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Try to import webdriver_manager for automatic driver management
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False


class GoogleScraper:
    """
    Automated Google Search Scraper using Selenium.
    
    This class handles:
    - Browser initialization and configuration
    - Google search execution
    - Multi-page navigation
    - Text extraction from search results
    - Automatic delays to avoid rate limiting
    
    Example:
        >>> scraper = GoogleScraper(headless=False)
        >>> text = scraper.search_and_extract("python programming", max_pages=2)
        >>> print(f"Extracted: {len(text)} characters")
    """
    
    def __init__(self, headless=False):
        """
        Initialize the Google Scraper.
        
        Args:
            headless (bool): If True, run browser invisibly. 
                           If False, show browser window for monitoring.
                           Default: False (show browser)
        """
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.google.com/search"
        
        # User agent to appear as a real browser
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    def setup_driver(self):
        """
        Configure and initialize the Chrome WebDriver.
        
        Sets up:
        - Chrome options (headless mode, window size)
        - Professional user agent
        - Disables notifications and popups
        - Sets appropriate timeouts
        """
        print("Setting up Chrome WebDriver...")
        
        options = Options()
        
        # User agent
        options.add_argument(f"user-agent={self.user_agent}")
        
        # Headless mode (runs without visible window)
        if self.headless:
            options.add_argument("--headless=new")
            print("✓ Headless mode enabled (browser hidden)")
        else:
            print("✓ Browser window will be visible")
        
        # Common options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-default-apps")
        
        # Window size
        options.add_argument("--window-size=1400,900")
        
        # Disable images for faster loading (optional)
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        # Initialize WebDriver
        try:
            if HAS_WEBDRIVER_MANAGER:
                # Use webdriver-manager for automatic driver download
                print("✓ Using webdriver-manager for ChromeDriver")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Use system ChromeDriver
                print("✓ Using system ChromeDriver")
                self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✓ Chrome WebDriver initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing WebDriver: {str(e)}")
            raise
    
    def close_driver(self):
        """Close the WebDriver safely"""
        if self.driver:
            try:
                self.driver.quit()
                print("✓ WebDriver closed")
            except Exception as e:
                print(f"⚠ Error closing WebDriver: {str(e)}")
    
    def search_and_extract(self, keywords, max_pages, progress_callback=None):
        """
        Perform Google search and extract all visible text from result pages.
        
        This function:
        1. Opens the browser
        2. Searches Google with the provided keywords
        3. Iterates through specified number of pages
        4. Extracts visible text from each page
        5. Implements delays to avoid rate limiting
        
        Args:
            keywords (str): Search keywords (e.g., "python programming")
            max_pages (int): Maximum number of pages to scrape (1-10 recommended)
            progress_callback (callable): Optional function to track progress
                                        Called with (current_page, total_pages)
            
        Returns:
            str: All extracted text from all pages
            
        Raises:
            Exception: If search fails or WebDriver encounters issues
        """
        try:
            self.setup_driver()
            all_text = ""
            
            for page_num in range(max_pages):
                try:
                    # Calculate start parameter for pagination (Google uses 10 results per page)
                    start_index = page_num * 10
                    
                    # Build search URL with pagination
                    search_url = f"{self.base_url}?q={keywords}&start={start_index}"
                    
                    print(f"\n{'='*60}")
                    print(f"PAGE {page_num + 1} of {max_pages}")
                    print(f"{'='*60}")
                    print(f"Loading: {search_url}")
                    
                    # Load the page
                    self.driver.get(search_url)
                    
                    # Wait for JavaScript to execute and render content
                    print("⏳ Waiting for page to render (4 seconds)...")
                    time.sleep(4)
                    
                    # Multiple strategies to wait for page load
                    page_loaded = False
                    
                    # Strategy 1: Wait for search results container
                    try:
                        print("📍 Strategy 1: Checking for search results container...")
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-sokoban-container]"))
                        )
                        print("✓ Search results container found")
                        page_loaded = True
                    except Exception as e:
                        print(f"⚠ Strategy 1 failed: {str(e)[:50]}...")
                    
                    # Strategy 2: Wait for individual result elements (if strategy 1 failed)
                    if not page_loaded:
                        try:
                            print("📍 Strategy 2: Checking for individual result elements...")
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, "//div[@data-rank]"))
                            )
                            print("✓ Result elements found")
                            page_loaded = True
                        except Exception as e:
                            print(f"⚠ Strategy 2 failed: {str(e)[:50]}...")
                    
                    # Strategy 3: Basic wait for page body (if strategies 1-2 failed)
                    if not page_loaded:
                        try:
                            print("📍 Strategy 3: Basic page load check...")
                            WebDriverWait(self.driver, 8).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                            time.sleep(2)
                            print("✓ Page loaded (basic)")
                            page_loaded = True
                        except Exception as e:
                            print(f"⚠ Strategy 3 failed: {str(e)[:50]}...")
                    
                    # Extract content
                    print("\n📄 Extracting content from page...")
                    page_text = ""
                    
                    # Method 1: Try to get visible body text
                    try:
                        body_element = self.driver.find_element(By.TAG_NAME, "body")
                        page_text = body_element.text.strip()
                        
                        if page_text and len(page_text) > 100:
                            print(f"✓ Extracted {len(page_text)} characters from visible text")
                        else:
                            print(f"⚠ Low content from visible text ({len(page_text)} chars)")
                            raise Exception("Insufficient visible text")
                    
                    except Exception as e:
                        print(f"ℹ Visible text extraction limited: {str(e)[:40]}...")
                        print("🔄 Attempting HTML parsing...")
                        
                        try:
                            # Fallback: Extract from page source via HTML
                            page_source = self.driver.page_source
                            
                            # Remove script and style elements (they don't contain visible text)
                            page_source = re.sub(r'<script[^>]*>.*?</script>', '', page_source, flags=re.DOTALL)
                            page_source = re.sub(r'<style[^>]*>.*?</style>', '', page_source, flags=re.DOTALL)
                            
                            # Remove HTML tags
                            text = re.sub(r'<[^>]+>', ' ', page_source)
                            
                            # Clean up whitespace
                            text = re.sub(r'\s+', ' ', text).strip()
                            
                            # Decode HTML entities
                            from html import unescape
                            text = unescape(text)
                            
                            if text and len(text) > 100:
                                print(f"✓ Extracted {len(text)} characters from HTML parsing")
                                page_text = text
                            else:
                                print(f"⚠ Very little content extracted ({len(text)} chars)")
                                page_text = text
                        
                        except Exception as e2:
                            print(f"❌ HTML parsing also failed: {str(e2)[:50]}...")
                    
                    # Add to collection
                    if page_text:
                        all_text += page_text + "\n"
                    
                    # Update progress if callback provided
                    if progress_callback:
                        try:
                            progress_callback(page_num + 1, max_pages)
                        except Exception as e:
                            print(f"⚠ Progress callback error: {str(e)[:40]}...")
                    
                    # Delay between pages to avoid rate limiting
                    if page_num < max_pages - 1:
                        delay = 3 + (page_num * 0.5)  # Slightly longer delays for later pages
                        print(f"⏳ Waiting {delay:.1f}s before next page (rate limiting)...")
                        time.sleep(delay)
                
                except Exception as e:
                    print(f"❌ Error on page {page_num + 1}: {type(e).__name__}: {str(e)}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"✓ SCRAPING COMPLETED")
            print(f"  Total characters extracted: {len(all_text)}")
            print(f"{'='*60}\n")
            
            return all_text
        
        except Exception as e:
            print(f"❌ Fatal error during search: {type(e).__name__}: {str(e)}")
            raise
        
        finally:
            self.close_driver()


def scrape_google(keywords, max_pages, progress_callback=None, headless=False):
    """
    Convenience function to perform Google search and extract text.
    
    This is a simple wrapper around the GoogleScraper class.
    
    Args:
        keywords (str): Search keywords (e.g., "python programming")
        max_pages (int): Number of pages to scrape (1-10 recommended)
        progress_callback (callable): Optional progress tracking function
        headless (bool): Whether to run in headless mode (browser hidden)
        
    Returns:
        str: Extracted text from all pages
        
    Example:
        >>> text = scrape_google("machine learning", max_pages=2, headless=False)
        >>> print(f"Found {len(text)} characters")
    """
    scraper = GoogleScraper(headless=headless)
    return scraper.search_and_extract(keywords, max_pages, progress_callback)


if __name__ == "__main__":
    # Example usage
    print("Google Search Scraper - Example Usage")
    print("=====================================\n")
    
    # Test keywords
    test_keywords = "python data science"
    test_pages = 2
    
    print(f"Searching for: '{test_keywords}'")
    print(f"Number of pages: {test_pages}\n")
    
    # Show progress
    def progress(current, total):
        print(f"Progress: Page {current}/{total} ✓")
    
    # Run scraper
    try:
        text = scrape_google(test_keywords, test_pages, progress_callback=progress, headless=False)
        print(f"\n✓ Successfully extracted {len(text)} characters")
        print(f"\nFirst 500 characters of extracted text:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
