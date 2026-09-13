import sys
import argparse
import time
from datetime import datetime

from config import CATEGORIES, GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
from news_fetcher import fetch_category_candidates
from summarizer import curate_and_summarize
from url_decoder import resolve_articles_urls
from email_formatter import format_email_content
from sender import send_email

SAMPLE_MOCK_STORIES = {
    "ai": [
        {
            "headline": "OpenAI Unveils Next-Generation Reasoning Architecture",
            "summary": "OpenAI has officially launched a new class of reasoning models engineered specifically for complex mathematics and multi-step software engineering workflows. The architecture demonstrates dramatic benchmark improvements and reduced hallucination rates across enterprise codebases. Early access is currently rolling out to select partners, with broader API integration planned for next month.",
            "publisher": "TechCrunch",
            "direct_link": "https://techcrunch.com"
        },
        {
            "headline": "Google DeepMind Announces Breakthrough in Materials Science AI",
            "summary": "Google DeepMind researchers have introduced an updated foundation model capable of predicting novel crystalline structures with atomic precision. The breakthrough promises to accelerate discovery cycles for solid-state batteries and next-generation semiconductors by orders of magnitude. The research team has made the primary dataset open-source for academic researchers worldwide.",
            "publisher": "VentureBeat",
            "direct_link": "https://venturebeat.com"
        }
    ],
    "tech": [
        {
            "headline": "TCS and Infosys Accelerate Cloud & Enterprise AI Re-Skilling",
            "summary": "India's top IT service multinationals are aggressively scaling comprehensive AI and cloud certification programs across their engineering workforces. The initiative aims to pivot away from traditional maintenance contracts toward high-margin generative AI system deployments for global Fortune 500 enterprises. Industry analysts note this marks one of the largest corporate training transitions in Indian tech history.",
            "publisher": "The Economic Times",
            "direct_link": "https://economictimes.indiatimes.com"
        },
        {
            "headline": "Nvidia Partners with Global Chipmakers on Advanced Packaging Standards",
            "summary": "Nvidia has forged new collaborative pacts with major semiconductor fabrication facilities to standardize next-generation chiplet packaging architectures. The move is designed to alleviate severe silicon packaging bottlenecks and sustain accelerated computing roadmap delivery through 2027. Market reaction was broadly positive across global semiconductor equities.",
            "publisher": "Reuters",
            "direct_link": "https://www.reuters.com"
        }
    ],
    "politics": [
        {
            "headline": "India Expands Bilateral Trade and Technology Dialogues at Regional Summit",
            "summary": "External affairs ministers convened for high-level bilateral discussions focusing on resilient regional supply chains, digital public infrastructure, and strategic maritime cooperation. Officials emphasized the critical need for diversified critical minerals trade corridors and secure digital identity frameworks. Joint communiqués signed at the summit signal deepened economic integration across key partner nations.",
            "publisher": "The Hindu",
            "direct_link": "https://www.thehindu.com"
        },
        {
            "headline": "Parliamentary Standing Committee Reviews National Semiconductor Roadmap",
            "summary": "A high-level parliamentary committee met in New Delhi to review progress across the India Semiconductor Mission and evaluate upcoming fab construction milestones. Lawmakers emphasized the strategic national security imperative of domestic chip fabrication alongside skilled workforce development. The panel recommended streamlining capital subsidy disbursements to fast-track construction timelines.",
            "publisher": "Livemint",
            "direct_link": "https://www.livemint.com"
        }
    ]
}

def run_test_email():
    """Sends a quick verification email to ensure SMTP credentials work."""
    print("🚀 Sending test email to verify credentials...")
    subject = f"Test Email - News Automation Setup ({datetime.now().strftime('%H:%M:%S')})"
    plain_text = "Congratulations! Your Gmail SMTP credentials are configured correctly."
    html = """
    <div style="font-family:sans-serif; padding:20px; max-width:500px; border:1px solid #e2e8f0; border-radius:10px;">
        <h2 style="color:#4f46e5; margin-top:0;">✅ Setup Verified!</h2>
        <p>Your Gmail credentials and automated sender are working properly.</p>
        <p style="color:#64748b; font-size:13px;">Daily news digests will be delivered to this address every morning at 8:00 AM IST.</p>
    </div>
    """
    send_email(subject, html, plain_text)

def main():
    parser = argparse.ArgumentParser(description="Automated Daily News Digest")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run fetch, summarize, and render without sending email. Generates preview_email.html."
    )
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Send a fast verification email to test SMTP credentials."
    )
    args = parser.parse_args()

    if args.test_email:
        run_test_email()
        return

    start_time = time.time()
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    print("=" * 60)
    print(f"📰 DAILY INTELLIGENCE BRIEFING PIPELINE")
    print(f"📅 Date: {today_str}")
    print(f"⚙️ Mode: {'DRY RUN (Preview Only)' if args.dry_run else 'LIVE PRODUCTION (Send Email)'}")
    print("=" * 60)

    # Check credentials
    if not args.dry_run:
        if not GEMINI_API_KEY:
            print("❌ Error: GEMINI_API_KEY is not set.")
            print("   Please add GEMINI_API_KEY to your .env file or GitHub Secrets.")
            sys.exit(1)
        if not GMAIL_USER or not GMAIL_APP_PASSWORD:
            print("❌ Error: Missing GMAIL_USER or GMAIL_APP_PASSWORD.")
            print("   Please check your .env file or GitHub Secrets.")
            sys.exit(1)

    has_gemini = bool(GEMINI_API_KEY)
    if not has_gemini and args.dry_run:
        print("ℹ️ Note: GEMINI_API_KEY is not set yet. Running dry-run with preview sample data.")

    digest_data = []

    for cat in CATEGORIES:
        cat_id = cat["id"]
        title = cat["title"]
        icon = cat["icon"]
        query = cat["query"]
        target_count = cat.get("target_count", 5)

        print(f"\n[{icon} {title}]")

        if not has_gemini and args.dry_run:
            print("  ⚡ Using curated sample stories for visual preview...")
            sample_stories = SAMPLE_MOCK_STORIES.get(cat_id, [])
            digest_data.append({
                "id": cat_id,
                "title": title,
                "icon": icon,
                "stories": sample_stories
            })
            continue

        print(f"  1. Fetching RSS candidate articles...")
        candidates = fetch_category_candidates(query, max_candidates=25)
        print(f"     Found {len(candidates)} raw candidates.")

        if not candidates:
            print(f"     ⚠️ No candidate stories found for {title}.")
            digest_data.append({"id": cat_id, "title": title, "icon": icon, "stories": []})
            continue

        print(f"  2. Curating and summarizing top {target_count} stories with Gemini...")
        curated_stories = curate_and_summarize(title, candidates, target_count=target_count)
        print(f"     Selected and summarized {len(curated_stories)} stories.")

        print(f"  3. Resolving direct publisher URLs...")
        resolved_stories = resolve_articles_urls(curated_stories)

        digest_data.append({
            "id": cat_id,
            "title": title,
            "icon": icon,
            "stories": resolved_stories
        })

    # Format email contents
    print("\n🎨 Formatting HTML and Plain Text newsletter...")
    html_content, plain_text_content = format_email_content(digest_data, today_str)

    total_stories = sum(len(c["stories"]) for c in digest_data)

    if args.dry_run:
        preview_file = "preview_email.html"
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n✅ Dry run completed successfully in {time.time() - start_time:.2f}s!")
        print(f"📄 Generated {total_stories} stories across {len(digest_data)} categories.")
        print(f"🌐 Email preview saved to: {preview_file} (Open this in your browser to inspect).")
    else:
        subject = f"📰 Daily Intelligence Briefing — {datetime.now().strftime('%b %d, %Y')}"
        print(f"\n📤 Sending email to {RECIPIENT_EMAIL}...")
        send_email(subject, html_content, plain_text_content)
        print(f"\n🎉 Pipeline complete! Total execution time: {time.time() - start_time:.2f}s.")

if __name__ == "__main__":
    main()
