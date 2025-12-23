"""
Email Extractor from Google Search - Standalone Streamlit Application
A modular automation workflow for extracting emails from Google search results.

Components:
- Frontend: Streamlit UI with keyword input and scraping controls
- Scraping: Selenium-based Google search automation
- Extraction: Regex-based email extraction with deduplication
- Output: Excel file generation with download capability
"""

import streamlit as st
import os
from scraper import GoogleScraper
from email_extractor import extract_emails_from_text, get_sorted_emails
from excel_generator import generate_excel_from_emails


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Email Extractor from Google Search",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton > button { width: 100%; }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# APPLICATION HEADER
# ============================================================================

st.title("🔍 Email Extractor from Google Search")
st.markdown("---")
st.markdown("""
**Automated Email Extraction Workflow**

This application automates the process of searching Google and extracting email 
addresses from search results. It uses Selenium to open a real browser, performs 
Google searches, extracts visible text, identifies emails using regex patterns, 
and generates a downloadable Excel file.
""")


# ============================================================================
# SIDEBAR CONFIGURATION & USER INPUTS
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Instructions
    st.markdown("""
    <div style="background-color: #1a472a; border: 2px solid #2d7a4a; border-radius: 8px; padding: 20px; margin: 10px 0;">
    <h3 style="color: #ffffff; margin-top: 0;">💡 How it works:</h3>
    <ol style="color: #e8f5e9; font-size: 14px; line-height: 1.8;">
    <li>Enter search keywords</li>
    <li>Set number of pages to scrape</li>
    <li>Click "Start Searching"</li>
    <li>Watch browser open automatically</li>
    <li>Download extracted emails as Excel</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Search Settings**")
    
    # Headless mode toggle
    headless_mode = st.toggle(
        "🔍 Run browser in headless mode",
        value=False,
        help="If OFF: See browser open and search in real-time | If ON: Faster but no visual feedback"
    )

# ============================================================================
# MAIN INPUT SECTION
# ============================================================================

st.subheader("🔎 Search Parameters")

col1, col2 = st.columns([3, 1])

with col1:
    # Search keywords input
    keywords = st.text_input(
        "Enter Search Keywords",
        placeholder='e.g., "web developer" "contact email" australia',
        help="Enter the keywords to search for on Google"
    )

with col2:
    # Number of pages to scrape
    max_pages = st.number_input(
        "Pages to Scrape",
        min_value=1,
        max_value=10,
        value=2,
        help="Number of Google result pages (each page ≈ 10 results)"
    )

# Action buttons
col1, col2, col3 = st.columns([1.5, 1.5, 2])

with col1:
    start_button = st.button(
        "▶️ Start Searching",
        use_container_width=True,
        type="primary"
    )

with col2:
    clear_button = st.button(
        "🗑️ Clear Results",
        use_container_width=True
    )

st.markdown("---")


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "scraping_complete" not in st.session_state:
    st.session_state.scraping_complete = False
if "emails_found" not in st.session_state:
    st.session_state.emails_found = []
if "scraped_text" not in st.session_state:
    st.session_state.scraped_text = ""
if "page_count" not in st.session_state:
    st.session_state.page_count = 0


# ============================================================================
# CLEAR RESULTS HANDLER
# ============================================================================

if clear_button:
    st.session_state.scraping_complete = False
    st.session_state.emails_found = []
    st.session_state.scraped_text = ""
    st.session_state.page_count = 0
    st.success("✅ Results cleared!")
    st.rerun()


# ============================================================================
# MAIN WORKFLOW EXECUTION
# ============================================================================

if start_button:
    # Input validation
    if not keywords.strip():
        st.error("❌ Please enter search keywords")
    else:
        # Create UI containers for progress tracking
        progress_bar = st.progress(0)
        status_container = st.container()
        logs_container = st.container()
        
        with status_container:
            status_text = st.empty()
        
        with logs_container:
            st.info("📋 Scraping Log")
            log_output = st.empty()
        
        logs = []
        
        def log_message(message):
            """Helper function to add and display log messages"""
            logs.append(message)
            log_display = "\n".join(logs[-15:])
            log_output.text_area(
                label="Progress",
                value=log_display,
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )
        
        try:
            # ================================================================
            # PHASE 1: GOOGLE SEARCH SCRAPING
            # ================================================================
            
            status_text.info(f"🌐 Starting search for: '{keywords}'")
            log_message(f"Keywords: {keywords}")
            log_message(f"Pages: {max_pages}")
            log_message(f"Headless: {headless_mode}")
            log_message("-" * 50)
            
            # Initialize scraper
            log_message("Initializing Selenium browser...")
            scraper = GoogleScraper(headless=headless_mode)
            
            def progress_callback(page_num, total_pages):
                """Update progress bar during scraping"""
                progress = int((page_num / total_pages) * 50)
                progress_bar.progress(progress)
                status_text.info(f"🔄 Scraping page {page_num} of {total_pages}...")
                log_message(f"✓ Page {page_num} completed")
            
            # Perform scraping
            log_message("Opening browser and performing search...")
            scraped_text = scraper.search_and_extract(
                keywords=keywords,
                max_pages=max_pages,
                progress_callback=progress_callback
            )
            
            st.session_state.scraped_text = scraped_text
            st.session_state.page_count = max_pages
            progress_bar.progress(50)
            
            log_message(f"✓ Scraping complete ({len(scraped_text)} characters)")
            log_message("-" * 50)
            
            # ================================================================
            # PHASE 2: EMAIL EXTRACTION
            # ================================================================
            
            status_text.info("📧 Extracting email addresses...")
            log_message("Extracting emails from text...")
            
            # Extract emails
            emails = extract_emails_from_text(scraped_text)
            log_message(f"✓ Found {len(emails)} unique emails")
            
            # Sort emails
            sorted_emails = get_sorted_emails(emails)
            st.session_state.emails_found = sorted_emails
            progress_bar.progress(75)
            
            log_message(f"✓ Email extraction complete")
            
            # ================================================================
            # PHASE 3: EXCEL GENERATION
            # ================================================================
            
            status_text.info("📁 Generating Excel file...")
            log_message("Creating Excel workbook...")
            
            excel_bytes = generate_excel_from_emails(sorted_emails)
            progress_bar.progress(100)
            
            log_message("✓ Excel file generated successfully")
            log_message("-" * 50)
            log_message("✅ WORKFLOW COMPLETE")
            
            st.session_state.scraping_complete = True
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            progress_bar.empty()
            log_message(f"❌ ERROR: {str(e)}")
            st.error(f"❌ An error occurred: {str(e)}")
            status_text.empty()


# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.scraping_complete and st.session_state.emails_found:
    st.markdown("---")
    st.success("✅ Scraping and extraction complete!")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Emails Found", len(st.session_state.emails_found))
    with col2:
        st.metric("Pages Scraped", st.session_state.page_count)
    with col3:
        st.metric("Text Length", f"{len(st.session_state.scraped_text):,} chars")
    with col4:
        st.metric("Unique Count", len(st.session_state.emails_found))
    
    # Email preview
    with st.expander("📧 View Extracted Emails"):
        email_text = "\n".join(st.session_state.emails_found)
        st.text_area(
            "Emails:",
            value=email_text,
            height=300,
            disabled=True,
            label_visibility="collapsed"
        )
    
    # Download section
    st.markdown("---")
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel download
        excel_bytes = generate_excel_from_emails(st.session_state.emails_found)
        st.download_button(
            label="📊 Download Excel (XLSX)",
            data=excel_bytes,
            file_name=f"emails_{st.session_state.page_count}_pages.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # CSV download
        csv_data = "\n".join(st.session_state.emails_found)
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"emails_{st.session_state.page_count}_pages.csv",
            mime="text/csv",
            use_container_width=True
        )

elif st.session_state.scraping_complete and not st.session_state.emails_found:
    st.warning("""
    ⚠️ No emails found in the search results.
    
    This can happen because:
    - **No emails in results**: The search didn't return pages with emails
    - **Google blocked the request**: Try again later or use different keywords
    - **Limited content**: Try more pages or more specific search terms
    
    **Tips:**
    - Use more specific keywords (e.g., "contact email", "email address")
    - Try searching for specific companies or domains
    - Search with quotation marks: `"email" "contact"`
    """)


# ============================================================================
# FOOTER & DOCUMENTATION
# ============================================================================

st.markdown("---")

with st.expander("ℹ️ About This Application"):
    st.markdown("""
    ### Overview
    This is a **standalone Streamlit automation workflow** for extracting emails 
    from Google search results. It combines web scraping, regex-based text processing, 
    and Excel generation into a single, easy-to-use application.
    
    ### How It Works
    
    **Phase 1: Web Scraping**
    - Opens a Chrome browser using Selenium WebDriver
    - Performs Google searches using your keywords
    - Navigates through multiple result pages
    - Extracts all visible text from each page
    - Includes delays to avoid Google blocking (rate limiting)
    
    **Phase 2: Email Extraction**
    - Uses regex pattern matching to find email addresses
    - Pattern: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}`
    - Automatically removes duplicate emails
    - Normalizes all emails to lowercase
    
    **Phase 3: Excel Generation**
    - Creates a formatted Excel workbook (XLSX)
    - Header row with "Email" column in blue
    - Auto-fit column widths
    - Frozen header row for easy scrolling
    - Professional formatting
    
    ### Modular Architecture
    
    The application is built with clean separation of concerns:
    
    - **`scraper.py`**: Google search automation using Selenium
    - **`email_extractor.py`**: Regex-based email extraction and validation
    - **`excel_generator.py`**: Excel file creation and formatting
    - **`app.py`**: Streamlit UI and workflow orchestration
    
    ### Requirements
    
    - **Python 3.8+**
    - **Chrome browser** (must be installed for Selenium)
    - **Dependencies**: See `requirements.txt`
    
    ### Local vs Cloud
    
    **✅ Works Great Locally:**
    - Selenium with real browser automation
    - Full control over browser behavior
    - Best for personal/development use
    
    **⚠️ Cloud Limitations:**
    - Streamlit Cloud doesn't support browser automation
    - Limited to HTTP requests (which Google blocks frequently)
    - Consider using cloud API-based alternatives
    
    ### Best Practices
    
    1. **Keywords**: Be specific (e.g., "web developer contact" vs just "web")
    2. **Pages**: Start with 1-2 pages, increase if needed
    3. **Delays**: App includes automatic delays to be respectful
    4. **Verification**: Always verify extracted emails before use
    5. **Legal**: Ensure compliance with Google ToS and local laws
    """)

with st.expander("🛠️ Troubleshooting"):
    st.markdown("""
    **Problem: Chrome driver not found**
    - Ensure Google Chrome is installed
    - The app uses `webdriver-manager` to auto-download ChromeDriver
    - Try restarting the application
    
    **Problem: Browser opens but doesn't search**
    - Check your internet connection
    - Try simpler keywords
    - Google may be blocking - wait 10 minutes and try again
    
    **Problem: No emails found**
    - Your search terms may not return pages with email addresses
    - Try more specific keywords like "contact email" or "email address"
    - Increase the number of pages to scrape
    - Search for specific companies with email keywords
    
    **Problem: Slow performance**
    - Reduce the number of pages
    - Close other applications
    - Try during off-peak hours
    - Check your internet connection
    
    **Problem: App crashes**
    - Check the log output for error messages
    - Ensure Chrome is fully closed before restarting
    - Try in headless mode for better stability
    """)

st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.85em; margin-top: 2rem;'>
<strong>Email Extractor v2.0</strong> | Streamlit + Selenium | Local Automation Workflow
</div>
""", unsafe_allow_html=True)


# Page configuration
st.set_page_config(
    page_title="Email Extractor from Google Search",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# APPLICATION HEADER
# ============================================================================
st.title("🔍 Email Extractor from Google Search")
st.markdown("---")

st.markdown("""
This application helps you extract email addresses from Google search results.
It performs automated web scraping, extracts emails using regex patterns, 
and generates a downloadable Excel file.
""")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Information box with better visibility
    st.markdown("""
    <div style="background-color: #1a472a; border: 2px solid #2d7a4a; border-radius: 8px; padding: 20px; margin: 10px 0;">
    <h3 style="color: #ffffff; margin-top: 0;">💡 How it works:</h3>
    <ol style="color: #e8f5e9; font-size: 16px; line-height: 1.8;">
    <li>Enter search keywords</li>
    <li>Set the number of pages to scrape</li>
    <li>Click "Start Searching"</li>
    <li>Wait for the process to complete</li>
    <li>Download the Excel file</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Browser Options**")
    
    # Headless mode toggle
    headless_mode = st.toggle("🔍 Run browser in headless mode (invisible)", value=True)
    st.caption("Uncheck to see the browser window with search results in real-time")
    
    st.markdown("---")
    st.markdown("**Content Filtering**")
    
    # Option to exclude common domains
    exclude_free_emails = st.toggle("Exclude free email domains", value=False)
    st.caption("Filters out gmail.com, yahoo.com, outlook.com, etc.")

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Create columns for input
col1, col2 = st.columns([3, 1])

with col1:
    # Search keywords input
    keywords = st.text_input(
        "🔑 Enter Search Keywords",
        placeholder="e.g., web developer contact email",
        help="Enter the keywords you want to search for on Google"
    )

with col2:
    # Number of pages slider
    max_pages = st.number_input(
        "📄 Max Pages to Scrape",
        min_value=1,
        max_value=10,
        value=2,
        help="Number of Google search result pages to scrape (1 page = ~10 results)"
    )

st.markdown("---")

# Start searching button
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    start_button = st.button(
        "▶️ Start Searching",
        use_container_width=True,
        type="primary"
    )

with col2:
    clear_button = st.button(
        "🗑️ Clear Results",
        use_container_width=True
    )

# Initialize session state
if "scraping_complete" not in st.session_state:
    st.session_state.scraping_complete = False
if "emails_found" not in st.session_state:
    st.session_state.emails_found = []
if "scraped_text" not in st.session_state:
    st.session_state.scraped_text = ""

# Clear results
if clear_button:
    st.session_state.scraping_complete = False
    st.session_state.emails_found = []
    st.session_state.scraped_text = ""
    st.success("✅ Results cleared!")
    st.rerun()

# ============================================================================
# WORKFLOW ORCHESTRATION
# ============================================================================

if start_button:
    # Validate input
    if not keywords.strip():
        st.error("❌ Please enter search keywords")
    else:
        # Create progress tracking and logging
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.container()
        
        with log_container:
            st.info("📋 Live Scraping Log:")
            log_output = st.empty()
        
        # Capture logs for display
        logs = []
        
        try:
            # ================================================================
            # STEP 1: SCRAPE GOOGLE SEARCH RESULTS
            # ================================================================
            
            def log_message(message):
                """Add message to logs"""
                logs.append(message)
                # Show last 20 log entries
                log_display = "\n".join(logs[-20:])
                log_output.text_area(
                    label="Scraping Progress",
                    value=log_display,
                    height=250,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            status_text.info(f"🌐 Scraping Google search results for '{keywords}'...")
            log_message(f"Starting search for: {keywords}")
            log_message(f"Max pages: {max_pages}")
            log_message(f"Headless mode: {headless_mode}")
            log_message("-" * 50)
            
            def progress_callback(current_page, total_pages):
                progress = int((current_page / total_pages) * 50)  # First 50% for scraping
                progress_bar.progress(progress)
                status_text.info(f"🌐 Scraping page {current_page} of {total_pages}...")
                log_message(f"Page {current_page}/{total_pages} completed")
            
            # Perform the scraping
            # On Streamlit Cloud, headless_mode is ignored and uses cloud scraper instead
            scraped_text = scrape_google(
                keywords=keywords,
                max_pages=max_pages,
                progress_callback=progress_callback
            )
            
            st.session_state.scraped_text = scraped_text
            progress_bar.progress(50)
            log_message("-" * 50)
            log_message(f"✓ Scraping complete. Extracted {len(scraped_text)} characters")
            
            # ================================================================
            # STEP 2: EXTRACT EMAILS FROM SCRAPED TEXT
            # ================================================================
            status_text.info("📧 Extracting email addresses...")
            log_message("Starting email extraction...")
            
            # Extract emails
            emails = extract_emails_from_text(scraped_text)
            log_message(f"Found {len(emails)} unique emails")
            
            # Apply filters if requested
            if exclude_free_emails:
                log_message("Filtering free email domains...")
                free_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
                               'aol.com', 'mail.com', 'protonmail.com', 'icloud.com']
                original_count = len(emails)
                emails = {email for email in emails if not any(
                    email.endswith(f"@{domain}") for domain in free_domains
                )}
                log_message(f"Filtered: {original_count} → {len(emails)} (removed {original_count - len(emails)} free domains)")
            
            # Sort emails
            sorted_emails = get_sorted_emails(emails)
            st.session_state.emails_found = sorted_emails
            progress_bar.progress(75)
            log_message(f"Email extraction complete. Final count: {len(sorted_emails)}")
            
            # ================================================================
            # STEP 3: GENERATE EXCEL FILE
            # ================================================================
            status_text.info("📁 Generating Excel file...")
            log_message("Generating Excel file...")
            
            excel_bytes = generate_excel_from_emails(sorted_emails)
            progress_bar.progress(100)
            log_message("✓ Excel file generated successfully")
            log_message("-" * 50)
            
            st.session_state.scraping_complete = True
            
            # Clear status messages
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            progress_bar.empty()
            log_message(f"❌ ERROR: {str(e)}")
            st.error(f"❌ An error occurred: {str(e)}")
            status_text.empty()

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.scraping_complete and st.session_state.emails_found:
    st.markdown("---")
    st.success("✅ Scraping and extraction complete!")
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Emails Found", len(st.session_state.emails_found))
    
    with col2:
        st.metric("Text Length (chars)", len(st.session_state.scraped_text))
    
    with col3:
        st.metric("Pages Scraped", max_pages)
    
    with col4:
        st.metric("Keywords", keywords)
    
    # Display emails in a collapsible section
    with st.expander("📊 View All Extracted Emails"):
        # Create a column for copying
        col1, col2 = st.columns([3, 1])
        
        with col1:
            email_text = "\n".join(st.session_state.emails_found)
            st.text_area(
                "Emails:",
                value=email_text,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
        
        with col2:
            st.info("📋 Use Ctrl+A then Ctrl+C to copy all emails from the text area above")
    
    # Download section
    st.markdown("---")
    st.subheader("📥 Download Results")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Generate Excel file for download
        excel_bytes = generate_excel_from_emails(st.session_state.emails_found)
        
        st.download_button(
            label="📊 Download Excel (XLSX)",
            data=excel_bytes,
            file_name=f"emails_{keywords.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Generate CSV for download
        csv_data = "\n".join(st.session_state.emails_found)
        
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"emails_{keywords.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Generate TXT for download
        txt_data = "\n".join(st.session_state.emails_found)
        
        st.download_button(
            label="📝 Download TXT",
            data=txt_data,
            file_name=f"emails_{keywords.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

elif st.session_state.scraping_complete and not st.session_state.emails_found:
    st.warning("""
    ⚠️ No emails found in the search results.
    
    Try:
    - Using different keywords
    - Increasing the number of pages to scrape
    - Searching for more specific terms (e.g., "contact email" or "email address")
    """)

# ============================================================================
# FOOTER / ADDITIONAL INFO
# ============================================================================

st.markdown("---")

with st.expander("ℹ️ About This App"):
    st.markdown("""
    ### Features
    - 🌐 **Automated Google Search**: Scrapes search results without manual clicking
    - 📧 **Email Extraction**: Uses regex patterns to find all email addresses
    - 📊 **Excel Generation**: Creates formatted, downloadable spreadsheets
    - 🚫 **Deduplication**: Automatically removes duplicate emails
    - ⚡ **Rate Limiting**: Includes delays to avoid Google blocking
    
    ### Technical Details
    - **Scraping**: Selenium WebDriver for browser automation
    - **Email Extraction**: Regex pattern matching for email validation
    - **Excel Generation**: OpenPyXL for creating formatted spreadsheets
    - **Frontend**: Streamlit for interactive UI
    
    ### Important Notes
    - ⏱️ Scraping may take a few seconds per page
    - 🔒 Please respect Google's Terms of Service and use responsibly
    - 🚫 Excessive scraping may result in temporary blocks
    - 📧 Always verify extracted emails before use
    
    ### Disclaimer
    This tool is for educational and legitimate business purposes only. 
    Users are responsible for complying with applicable laws and website terms of service.
    """)

with st.expander("🛠️ Troubleshooting"):
    st.markdown("""
    **Issue: No emails found**
    - Try different keywords
    - Increase the number of pages
    - Check if results actually contain emails
    
    **Issue: Google blocking requests**
    - The app includes delays between pages to avoid blocking
    - Wait a few minutes before trying again
    - Use a VPN if available
    
    **Issue: Browser won't open**
    - Make sure Chrome is installed
    - Try unchecking "headless mode" in the sidebar
    - Check that no other Chrome instances are running
    
    **Issue: Slow performance**
    - Reduce the number of pages
    - Disable other applications
    - Try again later if server is busy
    
    **Issue: Can't see the browser window**
    - Uncheck "Run browser in headless mode" in the sidebar
    - The browser window should appear on your screen
    - It may appear behind other windows - check your taskbar
    
    **Issue: Text not being extracted**
    - The app uses multiple extraction methods (visible text + HTML parsing)
    - Check the Live Scraping Log to see what's being extracted
    - Try with a different search term that typically yields more results
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.85em;'>
<strong>Email Extractor v1.1</strong> | Interactive Browser Controls | Last Updated: Dec 2025
</div>
""", unsafe_allow_html=True)
