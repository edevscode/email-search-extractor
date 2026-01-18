# Email Extractor from Google Search

A standalone web application for extracting email addresses from Google search results automatically.

## Features

- **Automated Google Search**: Perform keyword searches and scrape Google results
- **Multi-page Scraping**: Extract content from multiple search result pages
- **Email Extraction**: Automatically find and extract all email addresses using regex
- **Deduplication**: Remove duplicate emails automatically
- **Excel Generation**: Create formatted Excel files ready for use
- **Multiple Export Formats**: Download as Excel, CSV, or TXT
- **Rate Limiting**: Includes delays to avoid Google blocking
- **Domain Filtering**: Optional filtering of free email domains

## Project Structure

```
email-extractor/
├── server.py               # FastAPI server (custom UI)
├── run_app.py              # EXE-friendly launcher
├── scraper.py              # Google search scraping module
├── email_extractor.py      # Email extraction and validation module
├── excel_generator.py      # Excel file generation module
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser (required for Selenium)

### Setup

1. **Navigate to the project directory**:
   ```bash
   cd email-extractor
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ChromeDriver** (optional):
   - The app uses `webdriver-manager` which automatically downloads the correct ChromeDriver version
   - Ensure Google Chrome is installed on your system

## Usage

### Running the Application

```bash
python run_app.py
```

This will open the app in your default browser at `http://localhost:8501`

### Using the App

1. **Enter Search Keywords**: Type the keywords you want to search for
2. **Set Number of Pages**: Use the slider to select how many search result pages to scrape (1-10)
3. **Optional Settings**: 
   - Toggle headless mode to see the browser in action
   - Enable domain filtering to exclude free email providers
4. **Click "Start Searching"**: The app will:
   - Open a browser and perform the Google search
   - Scrape the specified number of pages
   - Extract all email addresses
   - Generate an Excel file
5. **Download Results**: Download as Excel (.xlsx), CSV, or plain text (.txt)

## Module Documentation

### scraper.py
Handles web scraping of Google search results.

**Main Class: GoogleScraper**
- `setup_driver()`: Initialize Selenium WebDriver with Chrome
- `search_and_extract()`: Perform search and extract text from pages
- `close_driver()`: Safely close the WebDriver

**Key Features**:
- Automatic page pagination
- Configurable delays between requests
- Progress tracking callback
- Error handling for failed pages

### email_extractor.py
Extracts and validates email addresses.

**Main Class: EmailExtractor**
- `extract_emails()`: Extract emails using regex pattern
- `validate_email()`: Validate email format
- `filter_emails()`: Filter by domain exclusion

**Features**:
- Comprehensive email regex pattern
- Automatic deduplication
- Case normalization (convert to lowercase)
- Domain-based filtering

### excel_generator.py
Creates formatted Excel files with email data.

**Main Class: ExcelGenerator**
- `create_workbook()`: Create new Excel workbook
- `add_headers()`: Add formatted header row
- `add_emails()`: Add emails to worksheet
- `add_emails_with_metadata()`: Add emails with additional columns
- `save_to_bytes()`: Export as bytes (for Streamlit download)
- `save_to_file()`: Save to local file

**Features**:
- Professional formatting (bold headers, colors)
- Auto-fit column widths
- Frozen header row
- Support for metadata columns

### app.py
Main application UI is served from `server.py`.

**Features**:
- Streamlit-like UI with sidebar configuration
- Real-time progress tracking
- Multiple download formats
- Responsive error handling

## Configuration Options

### Sidebar Settings

**Headless Mode** (Default: ON)
- When enabled: Browser runs invisibly in the background (faster)
- When disabled: See the browser window as it scrapes (slower but helps debugging)

**Exclude Free Email Domains** (Default: OFF)
- When enabled: Filters out gmail.com, yahoo.com, outlook.com, etc.
- Useful for finding business/corporate email addresses

## Performance Tips

1. **Optimal Page Count**: Start with 1-2 pages (10-20 results), increase as needed
2. **Keywords**: More specific keywords yield better results
3. **Delays**: The app includes 2-3 second delays between pages to avoid blocking
4. **Chrome**: Ensure Chrome is fully closed if you encounter driver errors
5. **Network**: Better internet connection = faster scraping

## Troubleshooting

### "No emails found"
- Try different/more specific keywords
- Increase the number of pages to scrape
- Verify the search results contain emails

### "Google is blocking requests"
- Wait 5-10 minutes before retrying
- Reduce the number of pages
- Enable headless mode (helps avoid detection)

### "Chrome driver not found"
- The app auto-downloads ChromeDriver via webdriver-manager
- Ensure you have an active internet connection for the first run
- Verify Chrome browser is installed

### "Browser won't open"
- Check that no other Chrome instances are running
- Try disabling headless mode to see errors
- Restart the application

## Important Notes

### Legal & Ethical Considerations
- Use for legitimate business purposes (lead generation, research)
- Respect website Terms of Service
- Include appropriate delays between requests
- Don't overload servers with excessive requests
- Don't use for spam or malicious purposes
- Always verify data before using

### Data Privacy
- Email addresses are extracted from public search results
- No personal data beyond email addresses is collected
- Data is only processed locally in this application
- Downloaded files are stored on your computer

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | (see requirements.txt) | Web server |
| uvicorn | (see requirements.txt) | ASGI server |
| jinja2 | (see requirements.txt) | HTML templates |
| openpyxl | 3.11.0 | Excel file generation |
| playwright | (see requirements.txt) | Browser automation |

## Examples

### Example 1: Finding Web Developer Contacts
```
Keywords: "web developer contact email"
Pages: 3
Result: ~30-50 email addresses
```

### Example 2: Business Lead Generation
```
Keywords: "marketing manager email company.com"
Pages: 2
Result: Domain-specific email addresses
```

### Example 3: Filtered Business Emails
```
Keywords: "CEO email technology companies"
Pages: 3
Exclude Free Emails: ON
Result: Only business email addresses
```

## Future Enhancements

Potential features for future versions:
- [ ] LinkedIn profile scraping
- [ ] Email validation/verification
- [ ] Name and company extraction
- [ ] Database storage support
- [ ] Scheduled/automated scraping
- [ ] Proxy support for large-scale scraping
- [ ] API integration for email verification

## Support & Contributing

For issues, feature requests, or improvements:
1. Check the troubleshooting section
2. Ensure all dependencies are correctly installed
3. Try running with headless mode disabled for more detailed errors

## License

This project is provided as-is for educational and legitimate business purposes.

## Disclaimer

Users are solely responsible for:
- Complying with applicable laws and regulations
- Respecting website Terms of Service
- Using extracted data responsibly and ethically
- Verifying data accuracy before use

The creator assumes no liability for misuse of this tool.
