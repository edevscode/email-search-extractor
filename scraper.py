"""
Web Scraper Module
<<<<<<< HEAD
Handles Google search and text extraction using Playwright
=======
Handles Google search and text extraction using Selenium
>>>>>>> 0c7f6bb (Initial commit)
"""

import time
import re
<<<<<<< HEAD
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
=======
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
>>>>>>> 0c7f6bb (Initial commit)


class GoogleScraper:
    """Handles Google search scraping and text extraction"""
    
    def __init__(self, headless=True, interactive=False):
        """
<<<<<<< HEAD
        Initialize the scraper with Playwright
=======
        Initialize the scraper with Selenium WebDriver
>>>>>>> 0c7f6bb (Initial commit)
        
        Args:
            headless (bool): Whether to run browser in headless mode (invisible)
            interactive (bool): Whether to enable interactive mode (manual control)
        """
        self.headless = headless
        self.interactive = interactive
<<<<<<< HEAD
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
=======
        self.driver = None
        self.base_url = "https://www.google.com/search"
        self.pause_flag = False
        self.stop_flag = False
        
    def setup_driver(self):
        """Setup and configure the Chrome WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        else:
            # Make browser window visible and focused
            chrome_options.add_argument("--start-maximized")
        
        # Advanced anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Professional user agent that looks like a real browser
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional stealth options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-resources")
        chrome_options.add_argument("--disable-extensions")
        
        # Disable notifications and prompts
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Add experimental features for better compatibility
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Set window size for better visibility (if not already maximized)
        self.driver.set_window_size(1400, 900)
        
        # Add undetected execution
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def close_driver(self):
        """Close the WebDriver safely"""
        if self.driver:
            self.driver.quit()
    
    def search_and_extract(self, keywords, max_pages, progress_callback=None):
>>>>>>> 0c7f6bb (Initial commit)
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
<<<<<<< HEAD
            await self.setup_browser()
=======
            self.setup_driver()
>>>>>>> 0c7f6bb (Initial commit)
            all_text = ""
            
            for page_num in range(max_pages):
                # Check if stop flag is set
                if self.stop_flag:
                    print("Scraping stopped by user")
                    break
                
                # Handle pause
                while self.pause_flag:
<<<<<<< HEAD
                    await asyncio.sleep(0.5)
=======
                    time.sleep(0.5)
>>>>>>> 0c7f6bb (Initial commit)
                
                try:
                    # Calculate start parameter for pagination (Google uses 10 results per page)
                    start_index = page_num * 10
                    
                    # Build search URL with pagination
                    search_url = f"{self.base_url}?q={keywords}&start={start_index}"
                    
                    print(f"\n--- Page {page_num + 1} ---")
                    print(f"Loading: {search_url}")
<<<<<<< HEAD
                    await self.page.goto(search_url, wait_until="networkidle")
                    
                    # Wait for JavaScript to execute and render content
                    print("Waiting for page to render...")
                    await asyncio.sleep(2)
=======
                    self.driver.get(search_url)
                    
                    # Wait for JavaScript to execute and render content
                    print("Waiting for page to render...")
                    time.sleep(4)  # Let JavaScript render
>>>>>>> 0c7f6bb (Initial commit)
                    
                    # Multiple strategies to wait for page load
                    page_loaded = False
                    try:
<<<<<<< HEAD
                        # Strategy 1: Wait for search results container
                        print("Checking for search results...")
                        await self.page.wait_for_selector("//div[@data-sokoban-container]", timeout=10000)
                        print("✓ Search results container found")
=======
                        # Strategy 1: Wait for result container
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-sokoban-container]"))
                        )
                        print("Search results container found")
>>>>>>> 0c7f6bb (Initial commit)
                        page_loaded = True
                    except Exception as e1:
                        print(f"Strategy 1 (container): {str(e1)[:40]}...")
                        
                        try:
                            # Strategy 2: Wait for individual result elements
                            print("Checking for individual results...")
<<<<<<< HEAD
                            await self.page.wait_for_selector("//div[@data-rank]", timeout=10000)
                            print("✓ Result elements found")
=======
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, "//div[@data-rank]"))
                            )
                            print("Result elements found")
>>>>>>> 0c7f6bb (Initial commit)
                            page_loaded = True
                        except Exception as e2:
                            print(f"Strategy 2 (results): {str(e2)[:40]}...")
                            
                            try:
                                # Strategy 3: Just wait for body with timeout
                                print("Waiting for page body...")
<<<<<<< HEAD
                                await self.page.wait_for_selector("body", timeout=8000)
                                await asyncio.sleep(2)
                                print("✓ Page loaded (basic)")
=======
                                WebDriverWait(self.driver, 8).until(
                                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                                )
                                time.sleep(2)
                                print("Page loaded (basic)")
>>>>>>> 0c7f6bb (Initial commit)
                                page_loaded = True
                            except Exception as e3:
                                print(f"Strategy 3 (body): {str(e3)[:40]}...")
                    
                    # Extract content regardless of load strategy
                    print("Extracting content from page...")
                    
                    # Try to get body text (visible text)
                    try:
<<<<<<< HEAD
                        page_text = await self.page.inner_text("body")
                        page_text = page_text.strip()
                        
                        if page_text and len(page_text) > 100:  # Meaningful content check
                            text_length = len(page_text)
                            print(f"✓ Extracted {text_length} characters from visible text")
                            all_text += page_text + "\n"
                        else:
                            print(f"⚠ Low content from visible text ({len(page_text)} chars), trying HTML extraction...")
=======
                        body_element = self.driver.find_element(By.TAG_NAME, "body")
                        page_text = body_element.text.strip()
                        
                        if page_text and len(page_text) > 100:  # Meaningful content check
                            text_length = len(page_text)
                            print(f"Extracted {text_length} characters from visible text")
                            all_text += page_text + "\n"
                        else:
                            print(f"Low content from visible text ({len(page_text)} chars), trying HTML extraction...")
>>>>>>> 0c7f6bb (Initial commit)
                            raise Exception("Insufficient visible text")
                    
                    except Exception as e:
                        print(f"Visible text extraction failed: {str(e)[:40]}, trying HTML parsing...")
                        try:
<<<<<<< HEAD
                            # Fallback: Extract from page content
                            page_content = await self.page.content()
                            
                            # Remove script and style elements
                            page_content = re.sub(r'<script[^>]*>.*?</script>', '', page_content, flags=re.DOTALL)
                            page_content = re.sub(r'<style[^>]*>.*?</style>', '', page_content, flags=re.DOTALL)
                            
                            # Remove HTML tags
                            text = re.sub(r'<[^>]+>', ' ', page_content)
=======
                            # Fallback: Extract from page source
                            page_source = self.driver.page_source
                            
                            # Extract all text from HTML
                            import re
                            from html import unescape
                            
                            # Remove script and style elements
                            page_source = re.sub(r'<script[^>]*>.*?</script>', '', page_source, flags=re.DOTALL)
                            page_source = re.sub(r'<style[^>]*>.*?</style>', '', page_source, flags=re.DOTALL)
                            
                            # Remove HTML tags
                            text = re.sub(r'<[^>]+>', ' ', page_source)
>>>>>>> 0c7f6bb (Initial commit)
                            
                            # Clean up whitespace
                            text = re.sub(r'\s+', ' ', text).strip()
                            text = unescape(text)
                            
                            if text and len(text) > 100:
                                text_length = len(text)
<<<<<<< HEAD
                                print(f"✓ Extracted {text_length} characters from HTML")
                                all_text += text + "\n"
                            else:
                                print(f"⚠ Warning: Very little content extracted ({len(text)} chars)")
=======
                                print(f"Extracted {text_length} characters from HTML")
                                all_text += text + "\n"
                            else:
                                print(f"Warning: Very little content extracted ({len(text)} chars)")
>>>>>>> 0c7f6bb (Initial commit)
                                # Still add what we got
                                if text:
                                    all_text += text + "\n"
                        
                        except Exception as e3:
<<<<<<< HEAD
                            print(f"❌ Both extraction methods failed: {str(e3)[:60]}")
=======
                            print(f"Both extraction methods failed: {str(e3)[:60]}")
>>>>>>> 0c7f6bb (Initial commit)
                    
                    # In interactive mode, allow user to interact with the page
                    if self.interactive and not self.headless:
                        print(f"\n--- Interactive Mode ---")
                        print("Browser window is now visible and ready for interaction:")
<<<<<<< HEAD
                        print("  • View the search results in the browser window")
                        print("  • Select text: Click and drag, or use Ctrl+A")
                        print("  • Copy text: Press Ctrl+C")
                        print("  • Scroll: Use arrow keys or mouse wheel")
                        print("  • Click: Click any link or button")
=======
                        print("  - View the search results in the browser window")
                        print("  - Select text: Click and drag, or use Ctrl+A")
                        print("  - Copy text: Press Ctrl+C")
                        print("  - Scroll: Use arrow keys or mouse wheel")
                        print("  - Click: Click any link or button")
>>>>>>> 0c7f6bb (Initial commit)
                        print(f"\nWaiting 30 seconds or press Enter to proceed to next page...")
                        try:
                            import threading
                            input_event = threading.Event()
                            input_thread = threading.Thread(target=lambda: input_event.set())
                            input_thread.daemon = True
                            input_thread.start()
                            input_event.wait(timeout=30)
                        except:
<<<<<<< HEAD
                            await asyncio.sleep(30)
=======
                            time.sleep(30)
>>>>>>> 0c7f6bb (Initial commit)
                    
                    # Update progress if callback provided
                    if progress_callback:
                        progress_callback(page_num + 1, max_pages)
                    
                    # Delay between pages to avoid rate limiting
                    if page_num < max_pages - 1:
                        print(f"Waiting 3 seconds before next page...")
<<<<<<< HEAD
                        await asyncio.sleep(3)
                
                except Exception as e:
                    print(f"❌ Error on page {page_num + 1}: {type(e).__name__}: {str(e)}")
=======
                        time.sleep(3)
                
                except Exception as e:
                    print(f"Error on page {page_num + 1}: {type(e).__name__}: {str(e)}")
>>>>>>> 0c7f6bb (Initial commit)
                    import traceback
                    traceback.print_exc()
                    continue
            
<<<<<<< HEAD
            print(f"\n✓ Scraping completed. Total text extracted: {len(all_text)} characters")
            return all_text
        
        except Exception as e:
            print(f"❌ Fatal error during search: {type(e).__name__}: {str(e)}")
=======
            print(f"\nScraping completed. Total text extracted: {len(all_text)} characters")
            return all_text
        
        except Exception as e:
            print(f"Fatal error during search: {type(e).__name__}: {str(e)}")
>>>>>>> 0c7f6bb (Initial commit)
            import traceback
            traceback.print_exc()
            raise
        
        finally:
<<<<<<< HEAD
            await self.close_browser()
    
    async def select_all_text(self):
        """Select all text on the current page (Ctrl+A)"""
        if self.page:
            await self.page.keyboard.press("Control+A")
=======
            self.close_driver()
    
    def select_all_text(self):
        """Select all text on the current page (Ctrl+A)"""
        if self.driver:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.CONTROL + "a")
>>>>>>> 0c7f6bb (Initial commit)
            print("All text selected")
            return True
        return False
    
<<<<<<< HEAD
    async def copy_selected_text(self):
        """Copy selected text to clipboard (Ctrl+C)"""
        if self.page:
            await self.page.keyboard.press("Control+C")
=======
    def copy_selected_text(self):
        """Copy selected text to clipboard (Ctrl+C)"""
        if self.driver:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "c")
>>>>>>> 0c7f6bb (Initial commit)
            print("Text copied to clipboard")
            return True
        return False
    
<<<<<<< HEAD
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
=======
    def scroll_down(self):
        """Scroll down on the current page"""
        if self.driver:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            return True
        return False
    
    def scroll_up(self):
        """Scroll up on the current page"""
        if self.driver:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
            time.sleep(1)
            return True
        return False
    
    def get_current_page_text(self):
        """Get the text currently visible on the page"""
        if self.driver:
            return self.driver.find_element(By.TAG_NAME, "body").text
        return ""
    
    def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        if self.driver:
            self.driver.get(url)
            time.sleep(2)
            return True
        return False
    
    def go_back(self):
        """Go back to previous page"""
        if self.driver:
            self.driver.back()
            time.sleep(2)
            return True
        return False
    
    def go_forward(self):
        """Go forward to next page"""
        if self.driver:
            self.driver.forward()
            time.sleep(2)
            return True
        return False
    
    def refresh_page(self):
        """Refresh the current page"""
        if self.driver:
            self.driver.refresh()
            time.sleep(2)
>>>>>>> 0c7f6bb (Initial commit)
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


<<<<<<< HEAD
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


=======
>>>>>>> 0c7f6bb (Initial commit)
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
<<<<<<< HEAD
    return asyncio.run(scraper.search_and_extract(keywords, max_pages, progress_callback))
=======
    return scraper.search_and_extract(keywords, max_pages, progress_callback)
>>>>>>> 0c7f6bb (Initial commit)
