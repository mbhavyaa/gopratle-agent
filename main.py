"""GoPratle BDR Lead Enrichment & Outreach Agent.

Run modes:
  python main.py                       -> the agent: watches the Sheet + Telegram forever
  python main.py test "Zomato" "Gurgaon" -> research + pitch only, prints the result (no Sheet, no email)
"""

import sys
import time
from datetime import datetime, timedelta

import config
import outreach
import pitch
import research
import sheet
import telegram_bot

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def now_text():
    return datetime.now().strftime(TIME_FORMAT)


# ---------------------------------------------------------------- one lead
def process_row(worksheet, row_number, row):
    """The whole workflow for ONE company: research -> pitch -> log -> email -> schedule follow-up."""
    company, city = str(row["Company"]).strip(), str(row["City"]).strip()
    print(f"\n>> Processing row {row_number}: {company} / {city}")

    row["Status"] = "Processing"  # so the row is not picked up twice
    sheet.update_row(worksheet, row_number, row)

    try:
        lead = research.research(company, city)
        if not lead:
            row["Status"] = "No lead found"
            row["Notes"] = "Web search did not return a matching person"
        else:
            pitch_text = pitch.write_pitch(lead, company, city)
            row.update({
                "Lead Name": lead["name"],
                "Lead Title": lead.get("title", ""),
                "LinkedIn": lead.get("linkedin_url", ""),
                "Email": lead["email"],
                "Email Source": lead["email_source"],
                "Pitch": pitch_text,
            })

            subject, body = pitch.first_email(lead["name"], company, pitch_text)
            result = outreach.send_email(lead["email"], subject, body)

            followup_due = datetime.now() + timedelta(minutes=config.FOLLOWUP_DELAY_MINUTES)
            row.update({
                "Status": "Contacted",
                "Outreach Sent At": now_text(),
                "Follow-up Due": followup_due.strftime(TIME_FORMAT),
                "Notes": f"Outreach {result}",
            })
    except Exception as error:
        row["Status"] = "Error"
        row["Notes"] = str(error)[:300]

    sheet.update_row(worksheet, row_number, row)
    print(f"   -> {row['Status']}: {row.get('Lead Name', '')} | {row.get('Notes', '')}")
    return row


# ---------------------------------------------------------------- trigger 1: Google Sheet
def process_new_rows(worksheet):
    """A row is 'new' when it has Company + City and an empty Status."""
    for row_number, row in sheet.get_rows(worksheet):
        if row["Company"] and row["City"] and not row["Status"]:
            process_row(worksheet, row_number, row)


# ---------------------------------------------------------------- follow-ups
def send_due_followups(worksheet):
    """Sends the follow-up for rows still 'Contacted' whose Follow-up Due time has passed.
    Set Status to 'Replied' by hand in the Sheet to stop a follow-up."""
    for row_number, row in sheet.get_rows(worksheet):
        if row["Status"] != "Contacted" or not row["Follow-up Due"]:
            continue
        if datetime.strptime(row["Follow-up Due"], TIME_FORMAT) > datetime.now():
            continue
        try:
            subject, body = pitch.followup_email(row["Lead Name"], row["Company"], row["City"])
            result = outreach.send_email(row["Email"], subject, body)
            row["Status"] = "Followed Up"
            row["Follow-up Sent At"] = now_text()
            row["Notes"] = f"{row['Notes']} | Follow-up {result}"
        except Exception as error:
            row["Notes"] = f"{row['Notes']} | Follow-up failed: {error}"[:300]
        sheet.update_row(worksheet, row_number, row)
        print(f">> Follow-up for {row['Company']}: {row['Status']}")


# ---------------------------------------------------------------- trigger 2: Telegram
def handle_telegram(worksheet):
    for chat_id, text in telegram_bot.get_new_messages():
        parsed = telegram_bot.parse_command(text)
        if not parsed:
            telegram_bot.reply(chat_id, telegram_bot.HELP_TEXT)
            continue

        company, city = parsed
        telegram_bot.reply(chat_id, f"Searching for event leads at {company} in {city}...")
        row_number = sheet.add_row(worksheet, company, city)
        row = {header: "" for header in sheet.HEADERS}
        row.update({"Company": company, "City": city})
        row = process_row(worksheet, row_number, row)

        if row["Status"] == "Contacted":
            telegram_bot.reply(chat_id, (
                f"Lead: {row['Lead Name']} ({row['Lead Title']})\n"
                f"LinkedIn: {row['LinkedIn']}\n"
                f"Email: {row['Email']} ({row['Email Source']})\n\n"
                f"Pitch:\n{row['Pitch']}\n\n"
                f"Outreach sent. Follow-up scheduled for {row['Follow-up Due']}."
            ))
        else:
            telegram_bot.reply(chat_id, f"{row['Status']}: {row['Notes']}")


# ---------------------------------------------------------------- entry points
def run_agent():
    worksheet = sheet.open_sheet()
    print("Agent running. Add a row to the Sheet or message the Telegram bot. Ctrl+C to stop.")
    while True:
        try:
            if config.TELEGRAM_BOT_TOKEN:
                handle_telegram(worksheet)
            process_new_rows(worksheet)
            send_due_followups(worksheet)
        except Exception as error:  # e.g. network blip: log it and keep going
            print(f"[loop error] {error}")
        time.sleep(config.POLL_SECONDS)


def run_test(company, city):
    lead = research.research(company, city)
    if not lead:
        print("No lead found.")
        return
    print("\nLEAD:", lead)
    pitch_text = pitch.write_pitch(lead, company, city)
    print("\nFIRST EMAIL:\n" + "\n".join(pitch.first_email(lead["name"], company, pitch_text)))
    print("\nFOLLOW-UP:\n" + "\n".join(pitch.followup_email(lead["name"], company, city)))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "test":
        run_test(sys.argv[2], sys.argv[3])
    else:
        run_agent()
