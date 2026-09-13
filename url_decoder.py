import re
import base64
from concurrent.futures import ThreadPoolExecutor
import requests
from config import USER_AGENT

try:
    import googlenewsdecoder
except ImportError:
    googlenewsdecoder = None

def _try_decode_googlenewsdecoder(google_url: str) -> str | None:
    """Uses googlenewsdecoder library to reverse the Google News 2024+ redirect format."""
    if not googlenewsdecoder:
        return None
    try:
        res = googlenewsdecoder.new_decoderv1(google_url)
        if isinstance(res, dict) and res.get("status") and res.get("decoded_url"):
            decoded = res["decoded_url"]
            if decoded.startswith("http") and "google.com" not in decoded:
                return decoded
    except Exception:
        pass
    return None

def _try_decode_base64(google_url: str) -> str | None:
    """
    Attempts to extract publisher URL if the article ID contains
    standard base64 encoded payload.
    """
    try:
        match = re.search(r"/articles/([a-zA-Z0-9_-]+)", google_url)
        if not match:
            return None
        encoded = match.group(1)
        padding = len(encoded) % 4
        if padding:
            encoded += "=" * (4 - padding)
        decoded = base64.urlsafe_b64decode(encoded.encode("utf-8"))
        urls = re.findall(rb"https?://[a-zA-Z0-9\-._~:/?#[\]@!$&'()*+,;=%]+", decoded)
        for u in urls:
            decoded_url = u.decode("utf-8", errors="ignore")
            if "google.com" not in decoded_url and len(decoded_url) > 12:
                return decoded_url
    except Exception:
        pass
    return None

def resolve_single_url(google_url: str, timeout: int = 8) -> str:
    """
    Resolves a Google News redirect URL to the direct publisher URL.
    Order of resolution:
    1. googlenewsdecoder (modern 2024+ format)
    2. Base64 payload decoding
    3. HTTP redirect & HTML metadata inspection
    4. Fallback to original URL
    """
    if not google_url or not google_url.startswith("http"):
        return google_url

    # If it's already a direct non-Google URL, return as is
    if "news.google.com" not in google_url and "google.com" not in google_url:
        return google_url

    # Attempt 1: Modern googlenewsdecoder (Primary & most reliable)
    modern_decoded = _try_decode_googlenewsdecoder(google_url)
    if modern_decoded:
        return modern_decoded

    # Attempt 2: Legacy Base64 decode
    b64_res = _try_decode_base64(google_url)
    if b64_res:
        return b64_res

    # Attempt 3: Follow HTTP redirects and inspect response
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        session = requests.Session()
        res = session.get(google_url, headers=headers, allow_redirects=True, timeout=timeout)
        
        if res.url and "google.com" not in res.url:
            return res.url

        html = res.text
        
        canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](https?://[^"\']+)["\']', html, re.IGNORECASE)
        if canonical and "google.com" not in canonical.group(1):
            return canonical.group(1)

        og_url = re.search(r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\'](https?://[^"\']+)["\']', html, re.IGNORECASE)
        if og_url and "google.com" not in og_url.group(1):
            return og_url.group(1)

        match_links = re.findall(r'<a[^>]+href=["\'](https?://(?!news\.google\.com|www\.google\.com)[^"\']+)["\']', html)
        for link in match_links:
            if not link.startswith("https://support.google.com") and not link.startswith("https://policies.google.com"):
                return link

    except Exception:
        pass

    # Safe fallback: Original Google News link
    return google_url

def resolve_articles_urls(articles: list[dict], max_workers: int = 8) -> list[dict]:
    """
    Resolves links for a list of articles concurrently using ThreadPoolExecutor.
    Updates each article dictionary in-place with 'direct_link'.
    """
    def _worker(article: dict) -> dict:
        orig_link = article.get("original_link") or article.get("link", "")
        resolved = resolve_single_url(orig_link)
        article["direct_link"] = resolved
        return article

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_worker, articles))
