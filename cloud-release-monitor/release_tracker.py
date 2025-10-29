import requests
from bs4 import BeautifulSoup
import json, re, os
from datetime import datetime

STATE_FILE = "last_releases.json"
UPDATES_FILE = "updates.json"

URLS = {
    "Salesforce": "https://www.salesforce.com/releases/",
    "Workday": "https://explore.workday.com/workdayr1releases",
    "ServiceNow": "https://www.servicenow.com/now-platform/latest-release.html",
    "Oracle Fusion Cloud": "https://docs.oracle.com/en/cloud/saas/readiness/erp/",
    "Chrome": "https://chromereleases.googleblog.com/",
    "iOS": "https://developer.apple.com/news/releases/",
    "Android": "https://developer.android.com/about/versions",
    "Windows": "https://learn.microsoft.com/en-us/windows/release-health/",
    "macOS": "https://support.apple.com/en-in/macos",
    "Ubuntu": "https://wiki.ubuntu.com/Releases"
}

HEADERS = {
    "User-Agent": "Release-Monitor/1.0 (+https://github.com/)"
}

def fetch_title_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title")
        if title and title.text.strip():
            return title.text.strip()
        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            return h1.text.strip()
        # fallback: first 300 chars of body text
        return ' '.join(soup.get_text(" ", strip=True).split())[:300]
    except Exception as e:
        return f"Error fetching: {e}"

def parse_salesforce(text):
    m = re.search(r"(Spring|Summer|Winter)\s+[’']?\s?\d{2,4}", text, re.IGNORECASE)
    if m:
        return m.group(0).strip()
    return text[:200]

def parse_chrome(text):
    # look for "Stable Channel Update for desktop" lines or version patterns like 142.0.7444.59
    m = re.search(r"\b\d{2,3}\.\d+\.\d+\.\d+\b", text)
    if m:
        return m.group(0)
    return text[:200]

def parse_generic(text):
    # attempt to find a year+release token like 2025 R1 or 25B etc
    m = re.search(r"\b20\d{2}\s*R\d\b", text)
    if m:
        return m.group(0)
    m2 = re.search(r"\b2\d[B-C]\b", text)
    if m2:
        return m2.group(0)
    return text[:200]

def fetch_release(platform, url):
    text = fetch_title_text(url)
    if platform == "Salesforce":
        return parse_salesforce(text) 
    if platform == "Chrome":
        return parse_chrome(text)
    return parse_generic(text) or text

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def save_updates(updates):
    with open(UPDATES_FILE, "w") as f:
        json.dump(updates, f, indent=2)

def main():
    previous = load_state()
    results = {}
    updates = {}
    for platform, url in URLS.items():
        release = fetch_release(platform, url)
        results[platform] = {"version": release, "url": url, "checked_at": datetime.utcnow().isoformat()}
        prev = previous.get(platform, {}).get("version")
        if prev != release:
            updates[platform] = {"old": prev, "new": release, "url": url}
    save_state(results)
    if updates:
        save_updates(updates)
        print("UPDATES_FOUND")
        print(updates)
    else:
        # ensure no stale updates file remains
        if os.path.exists(UPDATES_FILE):
            os.remove(UPDATES_FILE)
        print("NO_UPDATES")

if __name__ == '__main__':
    main()
