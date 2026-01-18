"""
Web Scraper Module (Playwright version)
Handles Google search and text extraction using Playwright instead of Selenium
"""

import time
import re
from html import unescape
from typing import Callable, Optional

# Fix for Windows: Streamlit sets a SelectorEventLoop which breaks subprocesses required by Playwright.
# Force the ProactorEventLoop which supports subprocesses.
import sys, asyncio
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        # If Streamlit already created a loop, we ignore; Playwright will still attempt.
        pass

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Page


def _clean_html_text(html: str) -> str:
    """Remove scripts/styles/tags and return plain text."""
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return unescape(text)


class GoogleScraper:
    """Handles Google search scraping and text extraction using Playwright"""

    _USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, headless: bool = True, interactive: bool = False):
        self.headless = headless
        self.interactive = interactive
        self._playwright = None  # type: ignore
        self._browser = None  # type: ignore
        self.page: Optional[Page] = None
        self.base_url = "https://www.google.com/search"
        self.pause_flag = False
        self.stop_flag = False

    # ---------------------------------------------------------------------
    # Setup / Teardown
    # ---------------------------------------------------------------------
    def _setup(self) -> None:
        """Launch browser and open a new page."""
        self._playwright = sync_playwright().start()
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-notifications",
            "--disable-popup-blocking",
        ]
        self._browser = self._playwright.chromium.launch(headless=self.headless, args=launch_args)
        context = self._browser.new_context(user_agent=self._USER_AGENT, viewport={"width": 1400, "height": 900})
        self.page = context.new_page()

    def _close(self) -> None:
        """Close Playwright resources."""
        try:
            if self.page:
                self.page.close()
        finally:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def search_and_extract(
        self,
        keywords: str,
        max_pages: int,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Perform Google searches and extract visible text across pages."""
        try:
            self._setup()
            assert self.page is not None  # for type checker
            all_text: str = ""

            for page_num in range(max_pages):
                if self.stop_flag:
                    print("Scraping stopped by user")
                    break

                while self.pause_flag:
                    time.sleep(0.5)

                start_idx = page_num * 10  # Google paginates 10 results per page
                url = f"{self.base_url}?q={keywords}&start={start_idx}"

                print(f"\n--- Page {page_num + 1} ---")
                print(f"Loading: {url}")
                try:
                    self.page.goto(url, timeout=60000)
                except PlaywrightTimeoutError:
                    print("Timeout loading page, continuing...")
                    continue

                # Basic wait for JS-rendered content
                print("Waiting for page to render...")
                self.page.wait_for_timeout(4000)

                # Attempt to ensure search results have appeared
                try:
                    self.page.wait_for_selector("div[data-sokoban-container]", timeout=10000)
                    print("Search results container found")
                except PlaywrightTimeoutError:
                    # Fallback but proceed; sometimes Google changes attributes.
                    print("Could not confirm results container, proceeding anyway")

                # Extract visible text
                print("Extracting content from page...")
                page_text = self.page.evaluate("document.body.innerText").strip()

                if page_text and len(page_text) > 100:
                    print(f"Extracted {len(page_text)} characters from visible text")
                    all_text += page_text + "\n"
                else:
                    print(f"Low content ({len(page_text)} chars), trying HTML extraction...")
                    html = self.page.content()
                    text = _clean_html_text(html)
                    print(f"Extracted {len(text)} characters from HTML")
                    all_text += text + "\n"

                if progress_callback:
                    progress_callback(page_num + 1, max_pages)

                if page_num < max_pages - 1:
                    print("Waiting 3 seconds before next page...")
                    self.page.wait_for_timeout(3000)

            print(f"\nScraping completed. Total text extracted: {len(all_text)} characters")
            return all_text
        finally:
            self._close()

    # ---------------------------------------------------------------------
    # Optional Interaction Helpers
    # ---------------------------------------------------------------------
    def scroll_down(self) -> bool:
        if self.page:
            self.page.keyboard.press("PageDown")
            time.sleep(1)
            return True
        return False

    def scroll_up(self) -> bool:
        if self.page:
            self.page.keyboard.press("PageUp")
            time.sleep(1)
            return True
        return False

    def select_all_text(self) -> bool:
        if self.page:
            self.page.keyboard.press("Control+A")
            print("All text selected")
            return True
        return False

    def copy_selected_text(self) -> bool:
        # Clipboard integration isn't universally supported without extra flags.
        # Provided for API parity; does nothing significant here.
        if self.page:
            self.page.keyboard.press("Control+C")
            print("Text copy shortcut sent (clipboard access not verified)")
            return True
        return False

    def pause(self):
        self.pause_flag = True
        print("Scraping paused")

    def resume(self):
        self.pause_flag = False
        print("Scraping resumed")

    def stop(self):
        self.stop_flag = True
        print("Scraping stop requested")


def scrape_google(
    *,
    keywords: str,
    max_pages: int,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    headless: bool = True,
    interactive: bool = False,
) -> str:
    """Convenience wrapper to match previous Selenium-based API."""
    scraper = GoogleScraper(headless=headless, interactive=interactive)
    return scraper.search_and_extract(keywords, max_pages, progress_callback)
