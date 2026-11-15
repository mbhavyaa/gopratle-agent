"""Step 2 of the workflow: find the right person and their contact info.

1. Search the web (free, no API key) for Founder / HR / Events people at the company.
2. Give the search results to the AI and ask it to pick the single best lead.
3. Find their email (Hunter.io if you have a key, otherwise a guessed pattern).
"""

import re

import requests
from ddgs import DDGS

import config
import llm

SEARCH_QUERIES = [
    "{company} {city} events manager linkedin",
    "{company} {city} HR head linkedin",
    "{company} founder linkedin",
]


def web_search(query, max_results=6):
    """Free web search. Tries a few search engines because any one can fail at times."""
    for backend in ("google", "bing", "auto"):
        try:
            return DDGS().text(query, max_results=max_results, backend=backend)
        except Exception:
            continue
    return []


def search_people(company, city):
    results, seen_links = [], set()
    for template in SEARCH_QUERIES:
        query = template.format(company=company, city=city)
        for result in web_search(query):
            if result["href"] not in seen_links:
                seen_links.add(result["href"])
                results.append(result)
    return results


def pick_best_lead(company, city, results):
    if not results:
        return None

    numbered = "\n".join(
        f"{i}. {r['title']} | {r['href']} | {r['body']}" for i, r in enumerate(results, 1)
    )
    prompt = f"""You are a sales research assistant for GoPratle, a company that
connects event hosts with vetted event planners, DJs and crew.

From the web search results below, pick the ONE best person at "{company}" ({city})
to pitch event services to. Preference order:
1. Events / Employee Engagement / Employee Experience lead
2. HR / People / Culture head
3. Founder / CEO

Rules:
- Only choose a person who appears in the results. Never invent a name.
- The person must currently work at {company} (ignore people who left).
- If nobody fits, return an empty name.

Search results:
{numbered}

Reply with JSON only:
{{"name": "", "title": "", "linkedin_url": "", "company_domain": "", "why": ""}}
company_domain = the company's main email domain, e.g. zomato.com (use your knowledge)."""

    lead = llm.ask(prompt, want_json=True)
    return lead if lead.get("name") else None


def find_email(name, company, domain):
    """Returns (email, where_it_came_from)."""
    parts = [re.sub(r"[^a-z]", "", p.lower()) for p in name.split()]
    parts = [p for p in parts if p]
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""

    if config.HUNTER_API_KEY and first:
        try:
            params = {"first_name": first, "last_name": last, "api_key": config.HUNTER_API_KEY}
            params["domain" if domain else "company"] = domain or company
            data = requests.get("https://api.hunter.io/v2/email-finder", params=params, timeout=20).json()
            email = (data.get("data") or {}).get("email")
            if email:
                return email, "hunter.io"
        except Exception:
            pass  # fall back to the guess below

    if domain and first:
        guess = f"{first}.{last}@{domain}" if last else f"{first}@{domain}"
        return guess, "guessed pattern"
    return "", "not found"


def research(company, city):
    """Full research step. Returns a dict about the lead, or None."""
    results = search_people(company, city)
    lead = pick_best_lead(company, city, results)
    if not lead:
        return None
    lead["email"], lead["email_source"] = find_email(
        lead["name"], company, lead.get("company_domain", "")
    )
    return lead
