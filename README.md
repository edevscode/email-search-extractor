# Email Extractor from Google Search

A standalone desktop application that automatically extracts email addresses from Google search results. Built with a custom web interface that looks and feels like Streamlit, but runs entirely on your machine with a single click.

## What Makes This Special?

- **One-Click Desktop App**: Double-click `EmailExtractor.exe` and it opens in your browser
- **Dark Mode**: Switch between light and dark themes in the sidebar
- **Smart Scraping**: Handles multiple Google search pages with built-in delays to avoid blocking
- **Clean Results**: Removes duplicates, filters free email providers, exports to Excel/CSV/TXT
- **Privacy-First**: Everything runs locally. No cloud services, no data leaves your computer

---

## Quick Start

### Option 1: Download & Run the EXE (Recommended)
1. Get `EmailExtractor.exe` from the latest release
2. Double-click it
3. Your browser opens at `http://localhost:8501`
4. Start searching

### Option 2: Run from Source
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python run_app.py`
4. Your browser opens automatically

---

## How to Use

Ready to find emails? Here's how it works:

1. **Type what you're looking for** in the search box (try "web developer contact email" or "marketing manager startup")
2. **Pick how deep to dig** - use the slider to choose 1-10 pages of Google results
3. **Fine-tune your search**:
   - **Headless Mode**: Keep the browser hidden (faster) or watch it work (great for debugging)
   - **Dark Mode**: Switch to dark theme for comfortable viewing
   - **Skip Free Emails**: Ignore gmail/yahoo/outlook to focus on business addresses
4. **Hit "Start Searching"** and watch the progress bar
5. **Download your results** as Excel, CSV, or plain text when done

---

## What's Inside?

Here's what makes it work:

```
email-extractor/
├── server.py               # Web server that powers the UI
├── run_app.py              # Launcher that opens your browser
├── scraper_playwright.py   # Google search automation
├── email_extractor.py      # Email finding and cleaning
├── excel_generator.py      # Creates Excel files
├── templates/index.html    # The interface you see
├── static/styles.css       # Styling with dark mode
├── static/app.js           # Interactive features
├── requirements.txt        # Python dependencies
└── README.md              # This guide
```

---

## Installation (Source Only)

### Requirements
- Python 3.8 or newer
- Google Chrome (for browser automation)

### Setup

1. **Clone the repo**:
   ```bash
   git clone https://github.com/edevscode/email-search-extractor.git
   cd email-search-extractor
   ```

2. **Create virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**:
   ```bash
   python run_app.py
   ```

Your browser should open automatically.

---

## Interface Features

### Sidebar Controls
- **Keywords**: What you're searching for
- **Pages**: How many Google results pages to scrape (1-10)
- **Headless Mode**: Run invisibly (faster) or watch the browser work
- **Dark Mode**: Switch between light and dark themes
- **Skip Free Emails**: Filter out gmail.com, yahoo.com, etc.

### Main Area
- **Progress Bar**: Real-time scraping progress
- **Live Logs**: See what's happening
- **Results Counter**: How many emails found so far
- **Download Buttons**: Excel (.xlsx), CSV, or plain text

---

## Tech Stack

| Tool | Why We Use It |
|------|---------------|
| **FastAPI** | Fast, lightweight web server |
| **Jinja2** | Clean HTML templates |
| **Vanilla JavaScript** | Simple, reliable interactivity |
| **Playwright** | Modern browser automation |
| **OpenPyXL** | Professional Excel files |
| **CSS Variables** | Smooth dark mode transitions |

---

## Pro Tips

1. **Start Small**: Test with 1-2 pages first to see if your keywords work
2. **Be Specific**: "web developer contact" works better than just "developer"
3. **Use Dark Mode**: Easier on the eyes during long scraping sessions
4. **Business Focus**: Toggle "Skip Free Emails" for professional contacts only
5. **Be Patient**: Built-in delays prevent Google from blocking - don't rush it

---

## Quick Fixes

### "No emails found?"
- Try different keywords
- Increase page count
- Check if the search results actually contain emails

### "Google is blocking requests?"
- Wait 5-10 minutes
- Use fewer pages
- Keep headless mode on

### "Browser won't start?"
- Close all Chrome windows
- Try disabling headless mode to see errors
- Restart the application

---

## Legal & Ethics

- **Use Responsibly**: This tool is for legitimate business research and lead generation
- **Respect Limits**: Built-in delays help avoid overwhelming servers
- **Verify Data**: Always double-check email addresses before using them
- **Stay Legal**: Follow applicable laws and website terms

---

## Real-World Examples

### Freelancers Finding Clients
```
Search: "small business web design contact"
Pages: 3
Skip Free Emails: ON
Result: 20-40 business email addresses
```

### Sales Lead Generation
```
Search: "marketing manager email software company"
Pages: 5
Result: 50-80 potential leads
```

### Academic Research
```
Search: "researcher email university"
Pages: 4
Skip Free Emails: OFF
Result: University email addresses
```

---

## Future Enhancements

Ideas for future versions:
- [ ] Email verification API integration
- [ ] Name and company extraction
- [ ] Bulk keyword processing
- [ ] Proxy support for large-scale scraping
- [ ] Scheduled/automated scraping

---

## Support

Found a bug or have an idea?
1. Check the troubleshooting section above
2. Make sure you're using the latest version
3. Open an issue on GitHub with details

---

## License & Disclaimer

This tool is provided as-is for educational and legitimate business purposes. You're responsible for:
- Following applicable laws and regulations
- Respecting website Terms of Service
- Using extracted data responsibly and ethically
- Verifying data accuracy before use

The creator assumes no liability for misuse of this tool.
