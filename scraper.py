"""
Web Scraper Module
Handles Google search and text extraction using Playwright
"""

import time
import re
import sys
import asyncio
from html import unescape
from playwright.async_api import async_playwright

# Ensure Playwright works with subprocesses on Windows (Playwright needs subprocess support).
# Use ProactorEventLoop, as SelectorEventLoop lacks subprocess support on Windows.
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        # Fallback for older Python versions where Proactor policy is default
        pass


class GoogleScraper:
    """Handles Google search scraping and text extraction"""
    
    def __init__(self, headless=True, interactive=False):
        """
        Initialize the scraper with Playwright
        
        Args:
            headless (bool): Whether to run browser in headless mode (invisible)
            interactive (bool): Whether to enable interactive mode (manual control)
        """
        self.headless = headless
        self.interactive = interactive
        self.browser = None
        self.page = None
        self.base_url = "https://www.google.com/search"
        self.pause_flag = False
        self.stop_flag = False
    
    async def setup_browser(self):
        """Setup and configure the Playwright browser"""
        playwright = await async_playwright().start()
        
        # Launch browser with anti-detection measures
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # Create new context with realistic user agent
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        
        # Create new page
        self.page = await context.new_page()
        
        # Add stealth measures
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
    
    async def close_browser(self):
        """Close the browser safely"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    async def search_and_extract(self, keywords, max_pages, progress_callback=None):
        """
        Perform Google search and extract all visible text from result pages
        
        Args:
            keywords (str): Search keywords
            max_pages (int): Maximum number of pages to scrape
            progress_callback (callable): Function to update progress (page_num, total_pages)
            
        Returns:
            str: All extracted text from all pages
        """
        try:
            await self.setup_browser()
            all_text = ""
            
            for page_num in range(max_pages):
                # Check if stop flag is set
                if self.stop_flag:
                    print("Scraping stopped by user")
                    break
                
                # Handle pause
                while self.pause_flag:
                    await asyncio.sleep(0.5)
                
                try:
                    # Calculate start parameter for pagination (Google uses 10 results per page)
                    start_index = page_num * 10
                    
                    # Build search URL with pagination
                    search_url = f"{self.base_url}?q={keywords}&start={start_index}"
                    
                    print(f"\n--- Page {page_num + 1} ---")
                    print(f"Loading: {search_url}")
                    await self.page.goto(search_url, wait_until="networkidle")
                    
                    # Wait for JavaScript to execute and render content
                    print("Waiting for page to render...")
                    await asyncio.sleep(2)
                    
                    # Multiple strategies to wait for page load
                    page_loaded = False
                    try:
                        # Strategy 1: Wait for search results container
                        print("Checking for search results...")
                        await self.page.wait_for_selector("//div[@data-sokoban-container]", timeout=10000)
                        print("✓ Search results container found")
                        page_loaded = True
                    except Exception as e1:
                        print(f"Strategy 1 (container): {str(e1)[:40]}...")
                        
                        try:
                            # Strategy 2: Wait for individual result elements
                            print("Checking for individual results...")
                            await self.page.wait_for_selector("//div[@data-rank]", timeout=10000)
                            print("✓ Result elements found")
                            page_loaded = True
                        except Exception as e2:
                            print(f"Strategy 2 (results): {str(e2)[:40]}...")
                            
                            try:
                                # Strategy 3: Just wait for body with timeout
                                print("Waiting for page body...")
                                await self.page.wait_for_selector("body", timeout=8000)
                                await asyncio.sleep(2)
                                print("✓ Page loaded (basic)")
                                page_loaded = True
                            except Exception as e3:
                                print(f"Strategy 3 (body): {str(e3)[:40]}...")
                    
                    # Extract content regardless of load strategy
                    print("Extracting content from page...")
                    
                    # Try to get body text (visible text)
                    try:
                        page_text = await self.page.inner_text("body")
                        page_text = page_text.strip()
                        
                        if page_text and len(page_text) > 100:  # Meaningful content check
                            text_length = len(page_text)
                            print(f"✓ Extracted {text_length} characters from visible text")
                            all_text += page_text + "\n"
                        else:
                            print(f"⚠ Low content from visible text ({len(page_text)} chars), trying HTML extraction...")
                            raise Exception("Insufficient visible text")
                    
                    except Exception as e:
                        print(f"Visible text extraction failed: {str(e)[:40]}, trying HTML parsing...")
                        try:
                            # Fallback: Extract from page content
                            page_content = await self.page.content()
                            
                            # Remove script and style elements
                            page_content = re.sub(r'<script[^>]*>.*?</script>', '', page_content, flags=re.DOTALL)
                            page_content = re.sub(r'<style[^>]*>.*?</style>', '', page_content, flags=re.DOTALL)
                            
                            # Remove HTML tags
                            text = re.sub(r'<[^>]+>', ' ', page_content)
                            
                            # Clean up whitespace
                            text = re.sub(r'\s+', ' ', text).strip()
                            text = unescape(text)
                            
                            if text and len(text) > 100:
                                text_length = len(text)
                                print(f"✓ Extracted {text_length} characters from HTML")
                                all_text += text + "\n"
                            else:
                                print(f"⚠ Warning: Very little content extracted ({len(text)} chars)")
                                # Still add what we got
                                if text:
                                    all_text += text + "\n"
                        
                        except Exception as e3:
                            print(f"❌ Both extraction methods failed: {str(e3)[:60]}")
                    
                    # In interactive mode, allow user to interact with the page
                    if self.interactive and not self.headless:
                        print(f"\n--- Interactive Mode ---")
                        print("Browser window is now visible and ready for interaction:")
                        print("  • View the search results in the browser window")
                        print("  • Select text: Click and drag, or use Ctrl+A")
                        print("  • Copy text: Press Ctrl+C")
                        print("  • Scroll: Use arrow keys or mouse wheel")
                        print("  • Click: Click any link or button")
                        print(f"\nWaiting 30 seconds or press Enter to proceed to next page...")
                        try:
                            import threading
                            input_event = threading.Event()
                            input_thread = threading.Thread(target=lambda: input_event.set())
                            input_thread.daemon = True
                            input_thread.start()
                            input_event.wait(timeout=30)
                        except:
                            await asyncio.sleep(30)
                    
                    # Update progress if callback provided
                    if progress_callback:
                        progress_callback(page_num + 1, max_pages)
                    
                    # Delay between pages to avoid rate limiting
                    if page_num < max_pages - 1:
                        print(f"Waiting 3 seconds before next page...")
                        await asyncio.sleep(3)
                
                except Exception as e:
                    print(f"❌ Error on page {page_num + 1}: {type(e).__name__}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n✓ Scraping completed. Total text extracted: {len(all_text)} characters")
            return all_text
        
        except Exception as e:
            print(f"❌ Fatal error during search: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        finally:
            await self.close_browser()
    
    async def select_all_text(self):
        """Select all text on the current page (Ctrl+A)"""
        if self.page:
            await self.page.keyboard.press("Control+A")
            print("All text selected")
            return True
        return False
    
    async def copy_selected_text(self):
        """Copy selected text to clipboard (Ctrl+C)"""
        if self.page:
            await self.page.keyboard.press("Control+C")
            print("Text copied to clipboard")
            return True
        return False
    
    async def scroll_down(self):
        """Scroll down on the current page"""
        if self.page:
            await self.page.keyboard.press("PageDown")
            await asyncio.sleep(1)
            return True
        return False
    
    async def scroll_up(self):
        """Scroll up on the current page"""
        if self.page:
            await self.page.keyboard.press("PageUp")
            await asyncio.sleep(1)
            return True
        return False
    
    async def get_current_page_text(self):
        """Get the text currently visible on the page"""
        if self.page:
            return await self.page.inner_text("body")
        return ""
    
    async def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        if self.page:
            await self.page.goto(url, wait_until="networkidle")
            await asyncio.sleep(2)
            return True
        return False
    
    async def go_back(self):
        """Go back to previous page"""
        if self.page:
            await self.page.go_back()
            await asyncio.sleep(2)
            return True
        return False
    
    async def go_forward(self):
        """Go forward to next page"""
        if self.page:
            await self.page.go_forward()
            await asyncio.sleep(2)
            return True
        return False
    
    async def refresh_page(self):
        """Refresh the current page"""
        if self.page:
            await self.page.reload()
            await asyncio.sleep(2)
            return True
        return False
    
    def pause(self):
        """Pause the scraping"""
        self.pause_flag = True
        print("Scraping paused")
    
    def resume(self):
        """Resume the scraping"""
        self.pause_flag = False
        print("Scraping resumed")
    
    def stop(self):
        """Stop the scraping"""
        self.stop_flag = True
        print("Scraping stop requested")


def _run_async(coro):
    """Run coroutine using SelectorEventLoop on Windows to avoid Proactor subprocess issue"""
    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            pass
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def scrape_google(keywords, max_pages, progress_callback=None, headless=True, interactive=False):
    """
    Convenience function to scrape Google search results
    
    Args:
        keywords (str): Search keywords
        max_pages (int): Maximum number of pages to scrape
        progress_callback (callable): Function to update progress
        headless (bool): Whether to run in headless mode
        interactive (bool): Whether to enable interactive mode
        
    Returns:
        str: Extracted text from all pages
    """
    scraper = GoogleScraper(headless=headless, interactive=interactive)
    return asyncio.run(scraper.search_and_extract(keywords, max_pages, progress_callback))
