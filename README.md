# 📰 Automated Daily Intelligence Briefing

An automated news curation pipeline that fetches, curates, and delivers a daily email briefing every morning at **8:00 AM IST**, featuring the **Top 5 stories** across three key domains:

1. 🤖 **Artificial Intelligence**
2. 💻 **MNCs, Tech & Software Engineering**
3. 🌍 **Geopolitics & Indian Politics**

Each story includes a crisp headline, a 3–4 line paragraph summary (explaining context, what happened, and why it matters), the publisher name, and a direct URL to the source.

---

## 🏗️ Architecture

```
[Google News RSS Queries]
         ↓
[news_fetcher.py]  Fetches ~25 fresh candidate articles per topic
         ↓
[summarizer.py]    Gemini AI deduplicates & crafts 3-4 line summaries
         ↓
[url_decoder.py]   Resolves Google redirect links to direct publisher URLs
         ↓
[email_formatter.py] Renders a responsive, modern HTML newsletter
         ↓
[sender.py]        Dispatches via Gmail SMTP (SSL:465)
         ↓
[GitHub Actions]   Runs scheduled every day at 8:00 AM IST (2:30 AM UTC)
```

---

## 🔑 Prerequisites & Credentials

You only need two free accounts:

### 1. Gemini API Key (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API key** -> **Create API key**.
3. Copy your API key.

### 2. Gmail App Password (Free)
To send emails securely via Gmail SMTP:
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Make sure **2-Step Verification** is turned ON.
3. In the search bar at the top, search for **"App passwords"** (or visit [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
4. Enter an App Name (e.g., `News Automation`) and click **Create**.
5. Copy the generated **16-character password** (e.g., `abcd efgh ijkl mnop`).

---

## 💻 Local Setup & Testing

### 1. Clone or Open the Project
```bash
cd /path/to/news_automation
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Your Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and fill in:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_app_password
RECIPIENT_EMAIL=your_email@gmail.com
```

### 4. Run a Dry Run (Preview without sending email)
```bash
python main.py --dry-run
```
This fetches live news, summarizes it using Gemini, resolves publisher URLs, and outputs **`preview_email.html`**. You can double-click this file to open it in Chrome or Safari to review the exact visual styling.

### 5. Test Email Connection
To verify your Gmail SMTP credentials without fetching news:
```bash
python main.py --test-email
```

### 6. Run the Full Live Pipeline
```bash
python main.py
```

---

## 🚀 Deploying to GitHub Actions (Zero-Cost 24/7 Hosting)

The project includes a ready-to-use GitHub Actions workflow configured in `.github/workflows/daily_news.yml`.

### Step 1: Initialize Git and Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit of news automation"
# Create a new private repository on GitHub, then link it:
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 2: Add Secrets to GitHub
1. In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Under **Repository secrets**, click **New repository secret** and add:

| Secret Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google AI Studio API key |
| `GMAIL_USER` | Your Gmail address (sender) |
| `GMAIL_APP_PASSWORD` | The 16-character Gmail App Password |
| `RECIPIENT_EMAIL` | The email where the daily digest should be sent |

### Step 3: Test Workflow Manually
1. Go to the **Actions** tab in your GitHub repository.
2. Select **Daily News Digest** in the left sidebar.
3. Click the **Run workflow** dropdown button -> click **Run workflow**.
4. Within 1–2 minutes, check your email inbox!

---

## ⚙️ Customization

* **Change Delivery Time:** Edit the cron expression in [`.github/workflows/daily_news.yml`](.github/workflows/daily_news.yml).
  * Default: `cron: '30 2 * * *'` (2:30 AM UTC = **8:00 AM IST**).
* **Customize Categories or Keywords:** Edit the queries and target count in [`config.py`](config.py).
* **Email Styling:** Modify colors, padding, and layout in [`email_formatter.py`](email_formatter.py).
