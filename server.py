from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from email_extractor import extract_emails_from_text, get_sorted_emails
from excel_generator import generate_excel_from_emails
from scraper_playwright import scrape_google


@dataclass
class JobState:
    status: str = "idle"  # idle|running|done|error
    progress: int = 0
    logs: list[str] = field(default_factory=list)
    keywords: str = ""
    max_pages: int = 0
    headless_mode: bool = True
    exclude_free_emails: bool = False
    scraped_text: str = ""
    emails_found: list[str] = field(default_factory=list)
    error: str | None = None


_jobs_lock = threading.Lock()
_jobs: dict[str, JobState] = {}


def _append_log(job: JobState, message: str) -> None:
    job.logs.append(message)
    if len(job.logs) > 200:
        job.logs = job.logs[-200:]


def _run_job(job_id: str) -> None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job.status = "running"
        job.progress = 0
        job.error = None
        job.scraped_text = ""
        job.emails_found = []
        job.logs = []

        keywords = job.keywords
        max_pages = job.max_pages
        headless_mode = job.headless_mode
        exclude_free_emails = job.exclude_free_emails

    def progress_callback(current_page: int, total_pages: int) -> None:
        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            progress = int((current_page / max(total_pages, 1)) * 50)
            j.progress = progress
            _append_log(j, f"Page {current_page}/{total_pages} completed")

    try:
        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            _append_log(j, f"Starting search for: {keywords}")
            _append_log(j, f"Max pages: {max_pages}")
            _append_log(j, f"Headless mode: {headless_mode}")
            _append_log(j, "-" * 50)

        scraped_text = scrape_google(
            keywords=keywords,
            max_pages=max_pages,
            progress_callback=progress_callback,
            headless=headless_mode,
            interactive=False,
        )

        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j.scraped_text = scraped_text
            j.progress = 50
            _append_log(j, "-" * 50)
            _append_log(j, f"Scraping complete. Extracted {len(scraped_text)} characters")
            _append_log(j, "Starting email extraction...")

        emails = extract_emails_from_text(scraped_text)

        if exclude_free_emails:
            free_domains = [
                "gmail.com",
                "yahoo.com",
                "outlook.com",
                "hotmail.com",
                "aol.com",
                "mail.com",
                "protonmail.com",
                "icloud.com",
            ]
            original_count = len(emails)
            emails = {email for email in emails if not any(email.endswith(f"@{d}") for d in free_domains)}
            with _jobs_lock:
                j = _jobs.get(job_id)
                if not j:
                    return
                _append_log(
                    j,
                    f"Filtered: {original_count} -> {len(emails)} (removed {original_count - len(emails)} free domains)",
                )

        sorted_emails = get_sorted_emails(emails)

        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j.emails_found = sorted_emails
            j.progress = 75
            _append_log(j, f"Email extraction complete. Final count: {len(sorted_emails)}")
            _append_log(j, "Generating Excel file...")

        _ = generate_excel_from_emails(sorted_emails)

        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j.progress = 100
            _append_log(j, "Excel file generated successfully")
            _append_log(j, "-" * 50)
            j.status = "done"

    except Exception as e:  # noqa: BLE001
        with _jobs_lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j.status = "error"
            j.error = str(e)
            _append_log(j, f"ERROR: {str(e)}")


app = FastAPI()

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.join(_BASE_DIR, "static")
_TEMPLATES_DIR = os.path.join(_BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/start")
def start(payload: dict[str, Any]) -> JSONResponse:
    keywords = str(payload.get("keywords", "")).strip()
    if not keywords:
        raise HTTPException(status_code=400, detail="Please enter search keywords")

    max_pages_raw = payload.get("max_pages", 2)
    try:
        max_pages = int(max_pages_raw)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid max_pages") from e

    if max_pages < 1 or max_pages > 10:
        raise HTTPException(status_code=400, detail="Max pages must be between 1 and 10")

    headless_mode = bool(payload.get("headless_mode", True))
    exclude_free_emails = bool(payload.get("exclude_free_emails", False))

    job_id = uuid.uuid4().hex
    job = JobState(
        status="idle",
        progress=0,
        keywords=keywords,
        max_pages=max_pages,
        headless_mode=headless_mode,
        exclude_free_emails=exclude_free_emails,
    )

    with _jobs_lock:
        _jobs[job_id] = job

    t = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    t.start()

    return JSONResponse({"job_id": job_id})


@app.get("/api/status/{job_id}")
def status(job_id: str) -> JSONResponse:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return JSONResponse(
            {
                "status": job.status,
                "progress": job.progress,
                "logs": job.logs[-20:],
                "keywords": job.keywords,
                "max_pages": job.max_pages,
                "headless_mode": job.headless_mode,
                "exclude_free_emails": job.exclude_free_emails,
                "scraped_text_length": len(job.scraped_text or ""),
                "emails_found": job.emails_found,
                "error": job.error,
            }
        )


@app.get("/download/{job_id}/xlsx")
def download_xlsx(job_id: str) -> Response:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        emails = list(job.emails_found)
        keywords = job.keywords

    if not emails:
        raise HTTPException(status_code=400, detail="No emails available")

    data = generate_excel_from_emails(emails)
    filename = f"emails_{keywords.replace(' ', '_')}.xlsx" if keywords else "emails.xlsx"

    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@app.get("/download/{job_id}/csv")
def download_csv(job_id: str) -> Response:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        emails = list(job.emails_found)
        keywords = job.keywords

    if not emails:
        raise HTTPException(status_code=400, detail="No emails available")

    data = "\n".join(emails).encode("utf-8")
    filename = f"emails_{keywords.replace(' ', '_')}.csv" if keywords else "emails.csv"

    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@app.get("/download/{job_id}/txt")
def download_txt(job_id: str) -> Response:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        emails = list(job.emails_found)
        keywords = job.keywords

    if not emails:
        raise HTTPException(status_code=400, detail="No emails available")

    data = "\n".join(emails).encode("utf-8")
    filename = f"emails_{keywords.replace(' ', '_')}.txt" if keywords else "emails.txt"

    return Response(
        content=data,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"ok": True, "time": int(time.time())})
