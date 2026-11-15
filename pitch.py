"""Step 3 of the workflow: write the 3-line pitch and the two emails."""

import config
import llm

GOPRATLE = "GoPratle connects event hosts with vetted event planners, DJs and on-ground crew."


def first_name(lead_name):
    return lead_name.split()[0] if lead_name else "there"


def write_pitch(lead, company, city):
    prompt = f"""Write a cold outreach pitch from GoPratle to {lead['name']},
{lead.get('title', '')} at {company} in {city}.

About GoPratle: {GOPRATLE}

Rules:
- Exactly 3 lines, one sentence each, under 60 words total.
- Line 1: personal hook about their role or {company}'s team events / offsites / launches in {city}.
- Line 2: what GoPratle does and why it saves them time.
- Line 3: a soft call to action (a quick 10-minute call).
- No greeting, no sign-off, no emojis, no placeholders.
Return only the 3 lines."""
    lines = [line.strip() for line in llm.ask(prompt).splitlines() if line.strip()]
    return "\n".join(lines[:3])


def first_email(lead_name, company, pitch_text):
    subject = f"Events at {company}? A quick idea from GoPratle"
    body = f"Hi {first_name(lead_name)},\n\n{pitch_text}\n\nBest,\n{config.FROM_NAME}\nGoPratle"
    return subject, body


def followup_email(lead_name, company, city):
    subject = f"Re: Events at {company}? A quick idea from GoPratle"
    body = (
        f"Hi {first_name(lead_name)},\n\n"
        f"Just bumping this up in case it got buried. If {company} has any offsites, "
        f"team parties or launches coming up in {city}, GoPratle can line up vetted "
        f"planners, DJs and crew quickly.\n\n"
        f"Would a 10-minute call this week work?\n\n"
        f"Best,\n{config.FROM_NAME}\nGoPratle"
    )
    return subject, body
