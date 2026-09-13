from datetime import datetime

def format_email_content(digest_data: list[dict], date_str: str | None = None) -> tuple[str, str]:
    """
    Renders both a mobile-responsive HTML newsletter and a clean plain-text fallback.
    digest_data is expected to be a list of category dicts, each containing:
    - title: str
    - icon: str
    - stories: list of {headline, summary, publisher, direct_link}
    """
    if not date_str:
        date_str = datetime.now().strftime("%A, %B %d, %Y")

    total_stories = sum(len(cat.get("stories", [])) for cat in digest_data)

    # --- 1. Generate Plain Text Version ---
    text_lines = [
        f"DAILY INTELLIGENCE BRIEFING",
        f"{date_str}",
        f"Top {total_stories} Curated Stories Across AI, Tech & Geopolitics",
        "=" * 60,
        ""
    ]

    for cat in digest_data:
        text_lines.append(f"\n{cat['icon']} {cat['title'].upper()}")
        text_lines.append("-" * 40)
        stories = cat.get("stories", [])
        if not stories:
            text_lines.append("No stories available for this category today.\n")
            continue

        for i, s in enumerate(stories, 1):
            text_lines.append(f"{i}. {s['headline']}")
            text_lines.append(f"   {s['summary']}")
            text_lines.append(f"   Source ({s.get('publisher', 'Link')}): {s.get('direct_link') or s.get('original_link')}\n")

    text_lines.append("=" * 60)
    text_lines.append("Delivered automatically via GitHub Actions • Powered by Gemini AI")
    plain_text = "\n".join(text_lines)

    # --- 2. Generate HTML Version ---
    category_sections_html = ""
    for cat in digest_data:
        stories = cat.get("stories", [])
        stories_cards_html = ""

        if not stories:
            stories_cards_html = """
            <div style="background:#ffffff; padding:16px; border-radius:8px; color:#64748b; font-size:14px; border:1px solid #e2e8f0;">
                No stories available for this category today.
            </div>
            """
        else:
            for idx, story in enumerate(stories, 1):
                headline = story.get("headline", "Untitled Story")
                summary = story.get("summary", "")
                publisher = story.get("publisher", "Original Source")
                link = story.get("direct_link") or story.get("original_link", "#")

                stories_cards_html += f"""
                <div style="background:#ffffff; border-radius:12px; padding:20px 22px; margin-bottom:16px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="margin-bottom:8px;">
                        <span style="font-size:13px; font-weight:700; color:#4f46e5; margin-right:6px;">#{idx}</span>
                        <a href="{link}" target="_blank" style="font-size:17px; font-weight:700; color:#0f172a; text-decoration:none; line-height:1.4;">
                            {headline}
                        </a>
                    </div>
                    <p style="font-size:14.5px; line-height:1.65; color:#334155; margin:10px 0 14px 0;">
                        {summary}
                    </p>
                    <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; border-top:1px solid #f1f5f9; padding-top:12px; margin-top:12px;">
                        <span style="background-color:#eef2ff; color:#3730a3; font-size:12px; font-weight:600; padding:4px 10px; border-radius:6px; display:inline-block;">
                            {publisher}
                        </span>
                        <a href="{link}" target="_blank" style="display:inline-block; font-size:13px; font-weight:600; color:#2563eb; text-decoration:none;">
                            Read Full Story &rarr;
                        </a>
                    </div>
                </div>
                """

        category_sections_html += f"""
        <div style="margin-bottom:36px;">
            <div style="display:flex; align-items:center; margin-bottom:14px;">
                <span style="font-size:22px; margin-right:10px;">{cat['icon']}</span>
                <h2 style="font-size:20px; font-weight:700; color:#0f172a; margin:0; letter-spacing:-0.3px;">
                    {cat['title']}
                </h2>
            </div>
            {stories_cards_html}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Intelligence Briefing - {date_str}</title>
</head>
<body style="margin:0; padding:0; background-color:#f8fafc; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing:antialiased;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f8fafc; padding:32px 12px;">
        <tr>
            <td align="center">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:640px; text-align:left;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding-bottom:28px;">
                            <div style="display:inline-block; background-color:#e0e7ff; color:#4338ca; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; padding:4px 10px; border-radius:12px; margin-bottom:10px;">
                                Morning Intelligence Briefing
                            </div>
                            <h1 style="font-size:28px; font-weight:800; color:#0f172a; margin:0 0 6px 0; letter-spacing:-0.5px;">
                                Daily Top News
                            </h1>
                            <p style="font-size:14px; color:#64748b; margin:0;">
                                {date_str} • Top {total_stories} stories curated by Gemini AI
                            </p>
                        </td>
                    </tr>

                    <!-- Category Content -->
                    <tr>
                        <td>
                            {category_sections_html}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding-top:16px; border-top:1px solid #e2e8f0; text-align:center;">
                            <p style="font-size:12px; color:#94a3b8; margin:0 0 6px 0;">
                                Delivered automatically at 8:00 AM IST via <strong>GitHub Actions</strong>
                            </p>
                            <p style="font-size:12px; color:#cbd5e1; margin:0;">
                                Curated from Google News RSS • Synthesized by Gemini 2.0 Flash
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html, plain_text
