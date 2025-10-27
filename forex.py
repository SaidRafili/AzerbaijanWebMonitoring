# forex.py
import os
import re
import time
import math
import random
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

summarizer = LexRankSummarizer()

# --- Load first 300 domains ---
with open("azurl.txt", "r", encoding="utf-8") as f:
    domains = [line.strip() for line in f if line.strip()]
domains_subset = domains[:5]

# --- Fetch and clean visible text ---
def fetch_homepage(domain):
    url = f"http://{domain}" if not domain.startswith("http") else domain
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            homepage_kb = len(r.content) / 1024
            internal_links = len(
                [a for a in soup.find_all("a", href=True) if domain in a["href"] or a["href"].startswith("/")]
            )
            load_time = r.elapsed.total_seconds()
            return text, homepage_kb, internal_links, load_time
    except Exception:
        pass
    return "", 0, 0, 0


# --- Visitor estimation ---
def estimate_visitors(domain, homepage_kb, internal_links, load_time):
    base = homepage_kb * (internal_links + 1) * 2
    indexed = 100
    try:
        r = requests.get(
            f"https://www.google.com/search?q=site:{domain}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        m = re.search(r"About ([\d,]+) results", r.text)
        if m:
            indexed = int(m.group(1).replace(",", ""))
    except Exception:
        pass
    visitors = base + math.log1p(indexed) * 200 + (1 / (load_time + 0.5)) * 100
    visitors = int(min(visitors * random.uniform(0.9, 1.1), 200000))
    return visitors, indexed


# --- Summarization (2–4 sentences) ---
def generate_summary(text):
    if not text or len(text.split()) < 20:
        return "Website could not be accessed or has insufficient text for summarization."
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        sent_count = 2 if len(text.split()) < 400 else 3 if len(text.split()) < 800 else 4
        summary_sentences = summarizer(parser.document, sent_count)
        return " ".join(str(s) for s in summary_sentences)
    except Exception as e:
        return f"Summarization failed: {str(e)}"


# --- Forex-style bar ---
def forex_bar(value, max_value=200000, width=30):
    ratio = min(value / max_value, 1.0)
    fill = int(ratio * width)
    bar = "█" * fill + "-" * (width - fill)
    return f"[{bar}]"


# --- Save file ---
out_path = "/data/website_ai_summaries.csv"  # shared folder for Render worker & dashboard
os.makedirs(os.path.dirname(out_path), exist_ok=True)

results = []
for i, domain in enumerate(domains_subset, 1):
    text, homepage_kb, internal_links, load_time = fetch_homepage(domain)

    if not text:
        summary = "Website could not be accessed or has no visible text."
        visitors, indexed = 0, 0
    else:
        summary = generate_summary(text)
        visitors, indexed = estimate_visitors(domain, homepage_kb, internal_links, load_time)

    record = {
        "index": i,
        "domain": domain,
        "summary": summary,
        "homepage_kb": round(homepage_kb, 2),
        "internal_links": internal_links,
        "google_indexed_pages": indexed,
        "estimated_visitors": visitors,
        "timestamp": datetime.utcnow().isoformat()
    }

    results.append(record)
    pd.DataFrame(results).to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[{i:03}/{len(domains_subset)}] {domain:<25} | {forex_bar(visitors)} {visitors:>6} | {summary[:90]}")
    time.sleep(1)

print(f"\n✅ Done! Results saved to: {out_path}")
