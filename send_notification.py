#!/usr/bin/env python3
"""Sends a Gmail update email. Called by the GitHub Actions workflow."""
import os
import smtplib
from email.mime.text import MIMEText

pwd = os.environ.get("GMAIL_APP_PASSWORD", "")
if not pwd:
    print("GMAIL_APP_PASSWORD not set — skipping email.")
    raise SystemExit(0)

to = os.environ.get("NOTIFY_EMAIL", "iambzannah@gmail.com")
sender = "iambzannah@gmail.com"

body = (
    "Your Argos sentiment dashboard has just been updated.\n\n"
    "View it at: https://thefootballbuzz01-creator.github.io/sentiment-analysis-bot/\n\n"
    "— Argos Sentiment Bot"
)
msg = MIMEText(body, "plain")
msg["Subject"] = "Argos dashboard updated"
msg["From"] = sender
msg["To"] = to

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(sender, pwd)
    s.sendmail(sender, [to], msg.as_string())

print(f"Email sent to {to}")
