"""
Cloud-compatible scraper using requests and BeautifulSoup
This version works on Streamlit Cloud without Selenium
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import Optional


class CloudScraper:
    """Lightweight scraper for Streamlit Cloud using requests"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.base_url = "https://www.google.com/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
                
                # Build search URL
                search_url = f"{self.base_url}?q={keywords}&start={start_index}"
                
                print(f"\n--- Page {page_num + 1} ---")
                print(f"Fetching: {search_url}")
                
                # Make request with timeout
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                print(f"✓ Got response (status {response.status_code})")
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all text
                page_text = soup.get_text(separator=' ', strip=True)
                
                if page_text and len(page_text) > 100:
                    text_length = len(page_text)
                    print(f"✓ Extracted {text_length} characters")
                    all_text += page_text + "\n"
                else:
                    print(f"⚠ Warning: Low content ({len(page_text)} chars)")
                
                # Update progress
                if progress_callback:
                    progress_callback(page_num + 1, max_pages)
                
                # Delay between pages
                if page_num < max_pages - 1:
                    print("Waiting 2 seconds...")
                    time.sleep(2)
            
            except Exception as e:
                print(f"❌ Error on page {page_num + 1}: {str(e)}")
                continue
        
        print(f"\n✓ Scraping complete. Total: {len(all_text)} characters")
        return all_text


def scrape_google_cloud(keywords, max_pages, progress_callback=None):
    """
    Cloud-compatible Google search scraper
    
    Args:
        keywords (str): Search keywords
        max_pages (int): Maximum pages to scrape
        progress_callback (callable): Progress callback
        
    Returns:
        str: Extracted text
    """
    scraper = CloudScraper()
    return scraper.search_and_extract(keywords, max_pages, progress_callback)
