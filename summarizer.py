import json
import re
import requests
from config import GEMINI_API_KEY

def _call_gemini_rest(prompt: str, api_key: str, model: str = "gemini-3.6-flash") -> str:
    """
    Direct REST API fallback for Gemini API.
    Works independently of SDK version compatibility.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def _call_gemini_sdk(prompt: str, api_key: str, model: str = "gemini-3.6-flash") -> str:
    """Calls Gemini using the official google-genai SDK."""
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    return response.text

def curate_and_summarize(category_title: str, candidates: list[dict], target_count: int = 5) -> list[dict]:
    """
    Uses Gemini LLM to select the top 5 distinct stories from candidates,
    deduplicate coverage, and generate a 3-4 line paragraph summary for each.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your environment or .env file.")

    if not candidates:
        print(f"⚠️ No candidates to summarize for category: {category_title}")
        return []

    # Prepare candidate payload for the prompt
    candidates_text = ""
    for c in candidates:
        candidates_text += (
            f"ID: {c['id']}\n"
            f"Title: {c['title']}\n"
            f"Publisher: {c['publisher']}\n"
            f"Link: {c['link']}\n"
            f"Snippet: {c['snippet']}\n"
            f"---\n"
        )

    prompt = f"""
You are an expert executive news editor preparing a morning intelligence briefing on '{category_title}'.

Below is a list of candidate news stories fetched today from RSS feeds:

{candidates_text}

TASK:
1. Select the top {target_count} most important and impactful news stories for this category.
2. DEDUPLICATE: If multiple stories cover the same event or announcement, pick only the best one.
3. For each of the {target_count} stories:
   - "headline": Write a crisp, informative, and engaging headline (do NOT include publisher name).
   - "summary": Write a well-crafted, informative 3 to 4 line paragraph (approx 50-70 words). It must clearly explain what happened, the context, and why it matters or its future implications.
   - "publisher": The publisher name.
   - "original_link": The exact original Link string from the selected candidate.

OUTPUT FORMAT:
Return ONLY a valid JSON array of {target_count} objects with keys: "headline", "summary", "publisher", "original_link".
Do not include any conversational preamble or surrounding text.
"""

    raw_response = ""
    # Try official SDK first, fallback to REST
    try:
        raw_response = _call_gemini_sdk(prompt, GEMINI_API_KEY)
    except Exception as sdk_err:
        try:
            raw_response = _call_gemini_rest(prompt, GEMINI_API_KEY)
        except Exception as rest_err:
            print(f"❌ Failed calling Gemini API: SDK error: {sdk_err} | REST error: {rest_err}")
            raise rest_err

    # Clean JSON output
    cleaned_json = raw_response.strip()
    if cleaned_json.startswith("```"):
        cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json)
        cleaned_json = re.sub(r"\s*```$", "", cleaned_json)

    try:
        curated_stories = json.loads(cleaned_json)
        if isinstance(curated_stories, list):
            return curated_stories[:target_count]
        elif isinstance(curated_stories, dict) and "stories" in curated_stories:
            return curated_stories["stories"][:target_count]
    except Exception as parse_err:
        print(f"❌ Error parsing Gemini JSON response: {parse_err}\nRaw text: {raw_response[:300]}")

    return []
