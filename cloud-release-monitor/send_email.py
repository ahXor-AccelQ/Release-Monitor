import json, os, smtplib, sys
from email.mime.text import MIMEText

UPDATES_FILE = "updates.json"

def load_updates():
    if not os.path.exists(UPDATES_FILE):
        print("NO_UPDATES_FILE")
        sys.exit(0)
    with open(UPDATES_FILE) as f:
        return json.load(f)

def build_body(updates):
    body = "Hi Ahisome,\n\nThe following platform updates were detected:\n\n"
    for k,v in updates.items():
        body += f"🔹 {k}\nOld: {v.get('old')}\nNew: {v.get('new')}\nLink: {v.get('url')}\n\n"
    body += "Best regards,\nReleaseBot\n"
    return body

def send_via_smtp(sender, password, smtp_server, smtp_port, recipient, body, subject):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    try:
        server = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        print("SENT")
    except Exception as e:
        print("SMTP_ERROR:", e)
        raise

def main():
    updates = load_updates()
    body = build_body(updates)
    subject = "[Update Alert] Platform Release Detected"
    # read env vars - if EMAIL_SENDER not set we will not send SMTP
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "465")
    recipient = os.getenv("EMAIL_RECIPIENT", "ahisome.roy@accelq.com")

    if sender and password:
        send_via_smtp(sender, password, smtp_server, smtp_port, recipient, body, subject)
    else:
        # No SMTP configured - exit with non-zero so workflow can create an issue instead
        print("NO_SMTP_CONFIGURED")
        print(body)
        sys.exit(2)

if __name__ == '__main__':
    main()
