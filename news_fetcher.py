import re
import urllib.parse
import feedparser
import requests
from config import USER_AGENT

def clean_html(raw_html: str) -> str:
    """Removes HTML tags and entities from raw RSS snippets."""
    if not raw_html:
        return ""
    clean = re.sub(r"<.*?>", "", raw_html)
    clean = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean)
    return " ".join(clean.split()).strip()

def fetch_category_candidates(query: str, max_candidates: int = 25) -> list[dict]:
    """
    Fetches raw candidate articles from Google News RSS for a given query.
    Returns a list of structured article dictionaries.
    """
    params = {
        "q": query,
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en"
    }
    rss_url = f"https://news.google.com/rss/search?{urllib.parse.urlencode(params)}"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=12)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"⚠️ Error fetching RSS feed for query '{query}': {e}")
        return []
    
    candidates = []
    for idx, entry in enumerate(feed.entries[:max_candidates]):
        raw_title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()
        published = getattr(entry, "published", "").strip()
        raw_summary = getattr(entry, "summary", "")
        
        # Google News RSS titles usually end with " - Publisher Name"
        if " - " in raw_title:
            parts = raw_title.rsplit(" - ", 1)
            title = parts[0].strip()
            publisher = parts[1].strip()
        else:
            title = raw_title
            publisher = entry.get("source", {}).get("title", "Unknown Publisher")
        
        snippet = clean_html(raw_summary)
        
        candidates.append({
            "id": idx + 1,
            "title": title,
            "publisher": publisher,
            "link": link,
            "published": published,
            "snippet": snippet
        })
        
    return candidates
