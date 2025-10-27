import os, re, math, random, time, requests, pandas as pd
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
summarizer = LexRankSummarizer()

def fetch_homepage(domain):
    url = f"http://{domain}" if not domain.startswith("http") else domain
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script","style","noscript","header","footer","nav"]): tag.decompose()
            text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
            kb = len(r.content) / 1024
            links = len([a for a in soup.find_all("a", href=True)
                         if domain in a["href"] or a["href"].startswith("/")])
            return text, kb, links, r.elapsed.total_seconds()
    except Exception:
        pass
    return "", 0, 0, 0

def estimate_visitors(domain, kb, links, load):
    base = kb * (links + 1) * 2
    indexed = 100
    try:
        r = requests.get(f"https://www.google.com/search?q=site:{domain}",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        m = re.search(r"About ([\d,]+) results", r.text)
        if m:
            indexed = int(m.group(1).replace(",", ""))
    except Exception:
        pass
    visitors = base + math.log1p(indexed)*200 + (1/(load+0.5))*100
    return int(min(visitors*random.uniform(0.9,1.1),200000)), indexed

def generate_summary(text):
    if not text or len(text.split()) < 20:
        return "No readable content."
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        sent_count = 2 if len(text.split())<400 else 3 if len(text.split())<800 else 4
        summary_sentences = summarizer(parser.document, sent_count)
        return " ".join(str(s) for s in summary_sentences)
    except Exception as e:
        return f"Summarization failed: {str(e)}"

def run_cycle():
    with open("azurl.txt","r",encoding="utf-8") as f:
        domains=[d.strip() for d in f if d.strip()]
    results=[]
    for i,domain in enumerate(domains[:100],1):
        text, kb, links, load = fetch_homepage(domain)
        summary = generate_summary(text)
        visitors, indexed = estimate_visitors(domain,kb,links,load)
        results.append({
            "domain": domain,
            "summary": summary,
            "homepage_kb": round(kb,2),
            "internal_links": links,
            "indexed_pages": indexed,
            "estimated_visitors": visitors,
            "timestamp": pd.Timestamp.now()
        })
        print(f"[{i:03}] {domain:<25} → {visitors:>6} visitors")
    pd.DataFrame(results).to_csv("website_ai_summaries.csv", index=False)

if __name__ == "__main__":
    while True:
        run_cycle()
        print("Cycle complete. Waiting 1 hour...")
        time.sleep(3600)
