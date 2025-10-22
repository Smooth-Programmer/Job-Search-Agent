import os
import smtplib
from email.mime.text import MIMEText
import requests
from datetime import datetime

# ========== CONFIG ==========
QUERY = "Full Stack Developer site:linkedin.com OR site:naukri.com OR site:indeed.com OR site:foundit.in"
MAX_RESULTS = 15
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Gmail App Password
BING_API_KEY = os.getenv("BING_API_KEY")  # optional
# =============================

def web_search(query):
    if BING_API_KEY:
        url = f"https://api.bing.microsoft.com/v7.0/search?q={query}&count={MAX_RESULTS}"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = [
            f"{item['name']}\n{item['url']}"
            for item in data.get("webPages", {}).get("value", [])
        ]
        return results

    # fallback simple Google query (less reliable)
    print("⚠️ No Bing key found. Using Google fallback.")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    lines = []
    for line in resp.text.split("<a href="):
        if "https://" in line and "google" not in line:
            link = line.split('"')[1]
            if link.startswith("http") and not any(
                b in link for b in ["youtube", "wikipedia"]
            ):
                lines.append(link)
    return lines[:MAX_RESULTS]

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_FROM, EMAIL_PASS)
        s.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())

if __name__ == "__main__":
    results = web_search(QUERY)
    if not results:
        body = "No results found today."
    else:
        body = "\n\n".join(results)

    now = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    subject = f"Daily MNC Full Stack Developer Jobs - {now}"
    send_email(subject, body)
    print("✅ Email sent successfully.")
