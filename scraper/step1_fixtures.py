# Phase 1 - get into bha api and grab fixtures

import json
import logging
from contextlib import suppress
from datetime import datetime, timedelta
from pathlib import Path

from playwright.async_api import TimeoutError, async_playwright

headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.britishhorseracing.com",
    "Referer": "https://www.britishhorseracing.com/",
}


# API URL templates
API_BASE: dict[str, str] = {
    "User-Agent": "Mozilla/5.0",
    "api_base": "api09.horseracing.software",
    "token_url": "https://www.britishhorseracing.com/racing/results/",
    # Fixtures overview (pagination and filtering via querystring)
    "fixtures": "https://api09.horseracing.software/bha/v1/fixtures/?fields=courseId,courseName,fixtureDate,fixtureType,fixtureSession,abandonedReasonCode,highlightTitle&month={month}&order=desc&page=1&per_page=250&resultsAvailable=1&year={year}",
    # Races in a fixture: /bha/v1/fixtures/{year}/{fixture_id}/races
    "races": "https://api09.horseracing.software/bha/v1/fixtures/{year}/{fixture_id}/races",
    # Results for a race: /bha/v1/races/{year}/{race_id}/0/results
    "results": "https://api09.horseracing.software/bha/v1/races/{year}/{race_id}/0/results",
    # Horse data
    "horses": "https://api09.horseracing.software/bha/v1/racehorses/{animal_id}",
    # Fixtures listed on page
    "fixture_list": "https://api09.horseracing.software/bha/v1/racecourses/",
}

DEFAULT_CACHE_DIR = Path("cache")
CACHE_DIR = Path("DEFAULT_CACHE_DIR")
CACHE_DIR.mkdir(exist_ok=True, parents=True)
TOKEN_FILE = Path(f"{DEFAULT_CACHE_DIR}/token.json")

REQUEST_TIMEOUT: int = 15
MAX_RETRIES: int = 3
BACKOFF_FACTOR: int = 2
TIMEOUT_MS: int = 60000

logger = logging.getLogger(__name__)


def _load_file_from_cache(body: str) -> dict | None:
    """Loads data from cached file"""
    cached_file = CACHE_DIR / f"{body}.json"

    if cached_file.exists():
        with open(cached_file) as f:
            return json.load(f)
    else:
        return None


def _save_to_cache(body: str, data: dict) -> None:
    """Saves data to cache file"""
    cached_file = CACHE_DIR / f"{body}.json"
    with open(cached_file, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _generate_daily_date_strings(start_date_string: str, end_date_string: str):
    """
    Generate ISO-formatted date strings for each day in a date range.

    Yields one date string at a time from start_date to end_date (inclusive).
    Both input dates should be in "YYYY-MM-DD" format.

    Args:
        start_date_string: First date in range, e.g. "2024-01-01"
        end_date_string: Last date in range, e.g. "2024-01-31"

    Yields:
        str: Date strings in "YYYY-MM-DD" format for each day in range

    Example:
        for date_str in generate_daily_date_strings("2024-01-01", "2024-01-03"):
            print(date_str)
        # Outputs:
        # 2024-01-01
        # 2024-01-02
        # 2024-01-03
    """
    try:
        # Convert ISO-formatted strings to datetime objects for date arithmetic
        range_start = datetime.fromisoformat(start_date_string)
        range_end = datetime.fromisoformat(end_date_string)
    except ValueError as error:
        raise ValueError(
            f"Invalid date format. Expected 'YYYY-MM-DD', "
            f"got start='{start_date_string}', end='{end_date_string}'"
        ) from error

    if range_start > range_end:
        raise ValueError(f"Start date {start_date_string} is after end date {end_date_string}")

    # Initialize our current position to the start of the range
    current_date = range_start

    # Iterate through each day until we pass the end date
    while current_date <= range_end:
        # Convert current datetime back to ISO string format and yield it
        formatted_date_string = current_date.strftime("%Y-%m-%d")
        yield formatted_date_string

        # Move forward by one day for the next iteration
        current_date = current_date + timedelta(days=1)


class TokenCapture:
    """
    Captures bearer tokens from HTTP requests.

    Designed to be used as a Playwright request event handler.
    Stores the first valid bearer token it finds.
    """

    def __init__(self, target_domain: str):
        """Initialize the TokenCapture class."""
        self.target_domain = target_domain
        self.captured_token: str | None = None

    async def handle_request(self, request) -> None:
        if self.captured_token:
            return

        url = self._get_request_url(request)
        if not url or self.target_domain not in url:
            return

        author_header = self._get_auth_header(request)
        if not author_header:
            return

        if self._is_valid_bearer_token(author_header):
            self.captured_token = author_header

    def _get_request_url(self, request) -> str | None:
        try:
            return getattr(request, "url", None)
        except AttributeError:
            return None

    def _get_auth_header(self, request) -> str | None:
        pass

    def _is_valid_bearer_token(self, auth_header: str) -> bool:
        pass

    def get_token(self) -> str | None:
        return self.captured_token


async def _fetch_token_via_playwright(
    target_url: str = API_BASE["token_url"],
    api_domain: str = API_BASE["api_base"],
    page_load_timeout_ms: int = TIMEOUT_MS,
    wait_for_request_ms: int = REQUEST_TIMEOUT,
) -> str:
    "Capture token by interacting with BHA API"
    # Token capture handler
    token_capture_handler = TokenCapture(api_domain)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            context = await browser.new_context()
            page = await context.new_page()

            page.on("request", token_capture_handler.handle_request)

            with suppress(TimeoutError):
                await page.goto(target_url, timeout=page_load_timeout_ms)

            await page.wait_for_timeout(wait_for_request_ms)
        finally:
            await browser.close()

    captured_token = token_capture_handler.get_token()
    if not captured_token:
        raise Exception("Failed to capture token")

    return captured_token


def _fetch_json_payload(url: str, token: str) -> dict[str, str | int] | None:
    pass
