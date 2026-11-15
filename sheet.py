"""Reads and writes the Google Sheet. The sheet is the agent's memory and dashboard."""

import re

import gspread

import config

HEADERS = [
    "Company", "City", "Status", "Lead Name", "Lead Title", "LinkedIn",
    "Email", "Email Source", "Pitch", "Outreach Sent At", "Follow-up Due",
    "Follow-up Sent At", "Notes",
]


def open_sheet():
    """Connects with the service account and makes sure row 1 has our headers."""
    if not config.GOOGLE_SHEET_ID:
        raise RuntimeError("GOOGLE_SHEET_ID is missing in .env")
    client = gspread.service_account(filename=config.GOOGLE_CREDENTIALS_FILE)
    worksheet = client.open_by_key(config.GOOGLE_SHEET_ID).sheet1

    first_row = worksheet.row_values(1)
    if first_row != HEADERS:
        # Only write headers if row 1 is empty or a start of ours (e.g. just "Company, City").
        if first_row != HEADERS[: len(first_row)]:
            raise RuntimeError(f"Row 1 of the sheet must be these headers: {HEADERS}")
        worksheet.update(values=[HEADERS], range_name="A1")
    return worksheet


def get_rows(worksheet):
    """Returns a list of (row_number, row_dict). Row 2 is the first data row."""
    records = worksheet.get_all_records(expected_headers=HEADERS, numericise_ignore=["all"])
    return [(i + 2, record) for i, record in enumerate(records)]


def update_row(worksheet, row_number, row):
    values = [str(row.get(h, "")) for h in HEADERS]
    worksheet.update(values=[values], range_name=f"A{row_number}")


def add_row(worksheet, company, city):
    """Used by the Telegram trigger. Returns the new row number."""
    response = worksheet.append_row([company, city], table_range="A1")
    updated_range = response["updates"]["updatedRange"]  # e.g. "Sheet1!A5:B5"
    return int(re.search(r"![A-Z]+(\d+)", updated_range).group(1))
