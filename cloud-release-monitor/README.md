# Cloud Release Monitor

This repository provides an automated monitor that checks official release pages for multiple products (Workday, ServiceNow, Salesforce, Oracle ERP, Chrome, iOS, Android, Windows, macOS, Ubuntu) and **notifies** when a new release/version is detected.

## How it works
- `release_tracker.py` scrapes the configured URLs and extracts a release identifier.
- It stores the last known releases in `last_releases.json`.
- If changes are found, it writes `updates.json`.
- `send_email.py` will attempt to send an email if SMTP credentials are provided as secrets in GitHub Actions.
- If SMTP is not configured (or email fails), the workflow will create a **GitHub Issue** in the repository containing the update summary.

## Setup (GitHub Actions)
1. Create a GitHub repository (private recommended) and upload the files from this package.
2. In the repository, create Actions Secrets (optional for SMTP):
   - `EMAIL_SENDER` (e.g. `releasebot@yourdomain.com`)
   - `EMAIL_PASSWORD` (SMTP password / app password)
   - `SMTP_SERVER` (default: `smtp.gmail.com`)
   - `SMTP_PORT` (default: `465`)
   - `EMAIL_RECIPIENT` (default: `ahisome.roy@accelq.com`)
3. The workflow is scheduled to run daily at **08:00 IST** (02:30 UTC).
4. On the first run the script will create `last_releases.json`. It will not send any emails until it detects a change.

## Notes
- If you prefer emails without SMTP setup, the workflow will auto-create a GitHub Issue instead when updates are detected.
- You can extend the `URLS` map in `release_tracker.py` to add more checks.

