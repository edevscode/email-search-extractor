"""
Cloud-compatible scraper using requests and BeautifulSoup
This version works on Streamlit Cloud without Selenium
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import Optional
import random


class CloudScraper:
    """Lightweight scraper for Streamlit Cloud using requests"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.base_url = "https://www.google.com/search"
        self.session = requests.Session()
        
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Better headers to avoid detection
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
        })
    
    def search_and_extract(self, keywords, max_pages, progress_callback=None):
        """
        Perform Google search and extract text using requests
        
        Args:
            keywords (str): Search keywords
            max_pages (int): Maximum number of pages to scrape
            progress_callback (callable): Function to update progress
            
        Returns:
            str: All extracted text from all pages
        """
        all_text = ""
        
        for page_num in range(max_pages):
            try:
                # Calculate start parameter for pagination
                start_index = page_num * 10
                
                # Build search URL with additional parameters to look more natural
                search_url = f"{self.base_url}?q={keywords}&start={start_index}&hl=en&gl=us"
                
                print(f"\n--- Page {page_num + 1} ---")
                print(f"Fetching: {search_url}")
                
                # Update user agent for this request
                self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
                # Make request with timeout and retries
                response = None
                for attempt in range(3):
                    try:
                        response = self.session.get(search_url, timeout=15)
                        if response.status_code == 200:
                            break
                        elif response.status_code == 429:  # Too many requests
                            print(f"⚠️ Rate limited (429), retrying in 5 seconds...")
                            time.sleep(5)
                        else:
                            print(f"⚠️ Got status {response.status_code}, retrying...")
                            time.sleep(2)
                    except requests.exceptions.Timeout:
                        print(f"⚠️ Timeout on attempt {attempt+1}, retrying...")
                        time.sleep(3)
                
                if not response or response.status_code != 200:
                    print(f"❌ Failed to fetch page (status: {response.status_code if response else 'No response'})")
                    print("⚠️ Google may be blocking requests. Try again later or use different keywords.")
                    continue
                
                print(f"✓ Got response (status {response.status_code})")
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple extraction methods
                page_text = ""
                
                # Method 1: Extract from specific search result divs
                try:
                    results = soup.find_all('div', {'class': ['g', 'yuRUbf']})
                    if results:
                        for result in results:
                            page_text += result.get_text(separator=' ', strip=True) + " "
                        print(f"✓ Extracted from search results divs ({len(page_text)} chars)")
                except:
                    pass
                
                # Method 2: If little content, try full page text
                if not page_text or len(page_text) < 100:
                    page_text = soup.get_text(separator=' ', strip=True)
                    print(f"✓ Extracted from full page ({len(page_text)} chars)")
                
                # Remove excessive whitespace
                page_text = ' '.join(page_text.split())
                
                # Check if we got meaningful content
                if page_text and len(page_text) > 100:
                    text_length = len(page_text)
                    print(f"✓ Final extraction: {text_length} characters")
                    all_text += page_text + "\n"
                else:
                    print(f"⚠️ Warning: Low content ({len(page_text)} chars)")
                    print("💡 Hint: Google may be blocking or the results are empty")
                    # Still add what we got
                    if page_text:
                        all_text += page_text + "\n"
                
                # Update progress
                if progress_callback:
                    progress_callback(page_num + 1, max_pages)
                
                # Random delay between pages (3-7 seconds)
                if page_num < max_pages - 1:
                    delay = random.randint(3, 7)
                    print(f"Waiting {delay} seconds before next page...")
                    time.sleep(delay)
            
            except Exception as e:
                print(f"❌ Error on page {page_num + 1}: {str(e)}")
                print("Try:")
                print("  • Using more specific keywords")
                print("  • Waiting a few minutes (Google may have rate limited)")
                print("  • Using a VPN or different network")
                continue
        
        print(f"\n✓ Scraping complete. Total: {len(all_text)} characters")
        return all_text
        return all_text


def scrape_google_cloud(keywords, max_pages, progress_callback=None):
    """

        Cloud-compatible Google search scraper using requests
    Works reliably on Streamlit Cloud without browser automation
    
    Args:
        keywords (str): Search keywords
        max_pages (int): Maximum pages to scrape
        progress_callback (callable): Progress callback function
        
    Returns:
        str: Extracted text from all pages
    """
    scraper = CloudScraper()
    return scraper.search_and_extract(keywords, max_pages, progress_callback)
