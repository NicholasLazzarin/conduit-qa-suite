# Conduit QA Suite

End-to-end and API-assisted test suite built with Playwright and TypeScript, testing the [RealWorld](https://github.com/realworld-apps/realworld) app (a Medium clone). The app runs locally with Docker, and also inside the CI pipeline.

This is a learning and portfolio project, built step by step. The app under test is not mine; the tests, fixtures, CI pipeline and project structure are.

## What is covered so far

- Sign up through the UI
- Login through the UI, with the user created via API beforehand
- Create an article as a logged-in user
- Open an article created through the API
- Edit the content of an article
- Delete an article, verified through the API (the article must return 404)
- CI with GitHub Actions: the pipeline starts the RealWorld app (Docker backend + React frontend) and runs the suite on Chromium
- API tests: wrong password (401), missing token, missing required field (422), editing another user's article (403), duplicate titles get a unique slug, public article listing
- Results pipeline: Playwright JSON output imported into SQLite by a Python script, with a report of runs, success rate per test and slowest tests

## How the tests are organized

- `tests/fixtures.ts` holds reusable fixtures:
  - `newUser`: creates a unique user through the API
  - `authToken`: logs that user in through the API
  - `loggedInPage`: a browser page with the auth token already set, so UI tests skip the login screen
  - `newArticle`: creates an article through the API, so edit and delete tests start with data ready
- Every test creates its own data with unique names, so tests do not depend on each other.

## Stack

- Playwright + TypeScript
- App under test: [realworld-django-ninja](https://github.com/c4ffein/realworld-django-ninja) backend (Django Ninja + PostgreSQL) and its React frontend
- Docker, GitHub Actions

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

## Planned

- Storing test results in a database and showing them in a dashboard
- An AI layer to summarize test failures

## Known limitations

- Tests are only run against Chromium, locally and in CI.
- The app sometimes shows an empty feed right after loading: in a 10-run sample, 3 runs needed a second attempt to open the Global Feed. The article test retries this step with `toPass`.
- Expired JWT tokens make `GET /api/user` return 500 instead of 401, and the frontend freezes on the login page until `localStorage` is cleared.
- The profile link (`/@username`) shows a blank page, and the browser console reports that no route matched it.
- The edit and article tests were unstable in earlier runs; waiting for the network to be idle before interacting made them stable in the samples I ran, but those samples were small.