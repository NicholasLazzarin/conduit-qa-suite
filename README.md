# Conduit QA Suite

Live results dashboard: https://nicholaslazzarin.github.io/conduit-qa-suite/ (updated by the CI pipeline after each run on `main`)

End-to-end and API-assisted test suite built with Playwright and TypeScript, testing the [RealWorld](https://github.com/realworld-apps/realworld) app (a Medium clone). The app runs locally with Docker, and also inside the CI pipeline.

This is a learning and portfolio project, built step by step. The app under test is not mine; the tests, fixtures, CI pipeline, results history and dashboard are.

## What is covered so far

- Sign up through the UI
- Login through the UI, with the user created via API beforehand
- Create an article as a logged-in user
- Open an article created through the API
- Edit the content of an article
- Delete an article, verified through the API (the article must return 404)
- API tests: wrong password (401), missing token, missing required field (422), editing another user's article (403), duplicate titles get a unique slug, public article listing
- CI with GitHub Actions: the pipeline starts the RealWorld app (Docker backend and React frontend) and runs the suite on Chromium and Firefox
- Results pipeline: after each run on `main`, the CI imports the Playwright JSON results into a SQLite history (committed to the repo), regenerates a static dashboard and publishes it on GitHub Pages
- Flakiness tracking: the article test records how many attempts its internal retry needed, and the dashboard shows how often it needed more than one

## How the tests are organized

- `tests/fixtures.ts` holds reusable fixtures:
  - `newUser`: creates a unique user through the API
  - `authToken`: logs that user in through the API
  - `loggedInPage`: a browser page with the auth token already set, so UI tests skip the login screen
  - `newArticle`: creates an article through the API, so edit and delete tests start with data ready
- Every test creates its own data with unique names, so tests do not depend on each other.
- `dashboard/ingest.py` reads the Playwright JSON output into SQLite, and `dashboard/build_html.py` generates the dashboard page in `docs/`.

## Stack

- Playwright + TypeScript
- Python + SQLite for the results history and the dashboard page
- App under test: [realworld-django-ninja](https://github.com/c4ffein/realworld-django-ninja) backend (Django Ninja + PostgreSQL) and its React frontend
- Docker, GitHub Actions, GitHub Pages

## How to run locally

1. Start the app under test (in the realworld-django-ninja folder):
```
   docker compose up -d
   make front-run-react
```
   The API runs at `http://localhost:8000` and the frontend at `http://localhost:4100`.

2. In this repo:
```
   npm install
   npx playwright install --with-deps
   npx playwright test --project=chromium
```

3. Open the report:
```
   npx playwright show-report
```

4. Update a local results history and dashboard (run the tests without `--reporter`, so the JSON file is generated):
```
   python3 dashboard/ingest.py
   python3 dashboard/build_html.py
```
   Locally, the history goes to `results/history.db`, which is git-ignored. In CI it goes to `data/ci-history.db`, selected with the `HISTORY_DB` environment variable, and that file is committed by the pipeline.

## Planned

- A possible AI layer to summarize failures, once the suite has real failures to analyze

## Known limitations

- Tests run on Chromium and Firefox, locally and in CI. WebKit is configured by Playwright but is not run.
- The dashboard shows CI runs only, so its history starts small and grows with each run on `main`.
- Pass rate counts the final result of each test. Retries done inside a test (for example with `toPass`) are only visible when the test records them, as the article test does.
- The app sometimes shows an empty feed right after loading: in a 10-run sample, 3 runs needed a second attempt to open the Global Feed. The article test retries this step with `toPass`.
- Expired JWT tokens make `GET /api/user` return 500 instead of 401, and the frontend freezes on the login page until `localStorage` is cleared.
- The profile link (`/@username`) shows a blank page, and the browser console reports that no route matched it.
- The edit and article tests were unstable in earlier runs; waiting for the network to be idle before interacting made them stable in the samples I ran, but those samples were small.