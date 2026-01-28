# Horse Racing Data Scraper
  
  Scrapes and analyzes British horse racing data.
  
  ## Setup
  
  1. Create virtual environment: `python3.14 -m venv .venv`
  2. Activate: `source .venv/bin/activate`
  3. Install dependencies: `pip install -e ".[dev]"`
  4. Install Playwright: `playwright install chromium`
  5. Create database: `createdb horseracing_dev`
  6. Run migrations: `python manage.py migrate`
  7. Create superuser: `python manage.py createsuperuser`
  
  ## Development
  
  - Run server: `python manage.py runserver`
  - Run tests: `pytest`
  - Format code: `ruff format .`
  - Type check: `basedpyright .`
