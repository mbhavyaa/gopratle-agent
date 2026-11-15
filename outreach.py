"""Step 5 of the workflow: send an email.

- If TEST_RECIPIENT is set, every email goes there (never to the real lead).
- If SMTP is not configured, the email is only printed (dry run).
"""

import smtplib
from email.message import EmailMessage

import config


def send_email(to_address, subject, body):
    recipient = config.TEST_RECIPIENT or to_address
    if not recipient:
        raise ValueError("No email address for this lead and no TEST_RECIPIENT set")

    if not config.SMTP_HOST:
        print(f"\n[DRY RUN] To: {recipient}\nSubject: {subject}\n\n{body}\n")
        return f"dry run (printed, to {recipient})"

    msg = EmailMessage()
    msg["From"] = f"{config.FROM_NAME} <{config.FROM_EMAIL}>"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
        server.ehlo()
        if server.has_extn("starttls"):
            server.starttls()
            server.ehlo()
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
    return f"sent to {recipient}"
