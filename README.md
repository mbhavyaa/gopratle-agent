# GoPratle BDR Lead Enrichment & Outreach Agent

A small Python agent that does a sales rep's (BDR's) first steps automatically.

You type **Company + City** into a Google Sheet, or message a Telegram bot:

> Connect with event leads for Zomato in Gurgaon

The agent then:

1. Searches the web for the company's Events / HR / Founder person.
2. Uses AI to pick the best person and gets their LinkedIn, title and email.
3. Writes a tailored 3-line pitch for GoPratle.
4. Logs everything back into the Google Sheet.
5. Sends the outreach email (to a sandbox inbox) and schedules a follow-up.
6. Sends the follow-up when it is due, unless you mark the row "Replied".

**Full explanation of every step, the architecture, setup and interview prep:
[EXPLAINED.md](EXPLAINED.md)**

## Quick start

```bash
git clone https://github.com/m-bhavyaa/gopratle-agent.git
cd gopratle-agent
pip install -r requirements.txt
cp .env.example .env        # then fill in your keys (see EXPLAINED.md, section 7)

python main.py test "Zomato" "Gurgaon"   # try research + pitch only, nothing is sent
python main.py                           # run the agent (Sheet + Telegram + follow-ups)
```

## Files

| File | What it does |
|---|---|
| `main.py` | The agent loop and the workflow for one lead |
| `research.py` | Web search, AI picks the lead, email lookup |
| `pitch.py` | 3-line pitch, first email, follow-up email |
| `sheet.py` | Read/write the Google Sheet |
| `outreach.py` | Send email over SMTP (sandbox) |
| `telegram_bot.py` | Telegram trigger |
| `llm.py` | Talks to the AI model |
| `config.py` | Reads settings from `.env` |
| `sheet_template.csv` | Import into Google Sheets to get the right columns |
