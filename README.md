# 🎯 Automated Sentiment Analysis Pipeline

A completely **free** sentiment analysis system that automatically collects comments from YouTube and Reddit, analyzes their sentiment, and generates beautiful reports with charts and visualizations.

## ✨ Features

- ✅ **Zero Cost** - No paid APIs or subscriptions required
- 🔄 **Fully Automated** - Runs on a schedule (every hour with GitHub Actions)
- 📊 **Beautiful Reports** - Interactive HTML dashboards with charts
- 🎥 **Multi-Source** - Analyzes comments from YouTube and Reddit
- 💾 **Local Storage** - All data stored in SQLite database
- 🚀 **Auto-Deploy** - Deploys reports to free Vercel hosting

## 🎓 Quick Start (Beginner-Friendly)

### Step 1: Install Python

1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.8 or higher
3. **Important**: During installation, check the box that says "Add Python to PATH"
4. Click "Install Now"

### Step 2: Clone or Set Up This Project

```bash
# Navigate to your project folder
cd argos-sentiment-project

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Reddit Credentials

This is the only external setup needed!

1. **Create Reddit Application:**
   - Go to [Reddit App Registration](https://www.reddit.com/prefs/apps)
   - Log in with your Reddit account (create one if needed)
   - Scroll to "Developed applications" section
   - Click "Create App" or "Create Another App"
   - Fill in the form:
     - **Name**: SentimentAnalyzer
     - **App Type**: Select "Script"
     - **Description**: For personal use
     - **Redirect URI**: http://localhost:8000
   - Click "Create App"

2. **Copy Credentials:**
   - You'll see your app listed below
   - You'll see "personal use script" under the app name - this is your **Client ID**
   - Below that is a "secret" field - this is your **Client Secret**

3. **Add to .env File:**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Open `.env` in a text editor
   - Replace `your_client_id_here` with your Client ID
   - Replace `your_client_secret_here` with your Client Secret
   - Save the file

**Example .env file:**
```
REDDIT_CLIENT_ID=abc123xyz789
REDDIT_CLIENT_SECRET=your_secret_key_here
REDDIT_USER_AGENT=SentimentAnalyzer/1.0
```

### Step 5: Configure What to Analyze

Edit `config.json` to choose what to analyze:

```json
{
  "youtube": {
    "enabled": true,
    "videos": [
      {
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "label": "My Video"
      }
    ]
  },
  "reddit": {
    "enabled": true,
    "searches": [
      {
        "subreddit": "python",
        "keywords": "sentiment analysis",
        "label": "Python Sentiment Posts"
      }
    ]
  }
}
```

**To get a YouTube video URL:**
- Open the video on YouTube
- Copy the URL from your browser's address bar
- Paste it into the config

**To find Reddit subreddits:**
- Go to [reddit.com](https://reddit.com)
- Browse communities you're interested in
- Subreddit names are what comes after `reddit.com/r/`
- Example: `reddit.com/r/python` → subreddit name is `python`

### Step 6: Run the Pipeline

```bash
python main.py
```

You should see output like:
```
============================================================
  🎯 SENTIMENT ANALYSIS PIPELINE
============================================================
✅ Configuration loaded successfully
✅ Database initialized
✅ Connected to Reddit API

=== YouTube Comment Collection ===
📝 Collecting comments from: My Video
...

=== Reddit Comment Collection ===
📝 Searching r/python for: 'sentiment analysis'
...

✅ PIPELINE COMPLETED SUCCESSFULLY
```

### Step 7: View Your Report

Open `reports/index.html` in your web browser to see your interactive report!

---

## 🤖 Set Up Automation (GitHub Actions + Vercel)

Once you're happy with local results, automate it!

### Part A: Set Up Vercel (1 minute)

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" → choose "Continue with GitHub"
3. Complete GitHub authorization
4. Click "+ New Project"
5. Select this repository
6. Click "Deploy"
7. Once deployed, you'll get a URL like `https://your-project.vercel.app`

### Part B: Add GitHub Secrets

GitHub Secrets securely store sensitive info (like Reddit credentials) so they're not visible in code.

1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions" (on the left)
4. Click "New repository secret"

**Add these secrets:**

| Name | Value |
|------|-------|
| `REDDIT_CLIENT_ID` | Your Reddit Client ID |
| `REDDIT_CLIENT_SECRET` | Your Reddit Client Secret |
| `VERCEL_TOKEN` | [Get from Vercel](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Your Vercel team/org ID (find in Vercel dashboard) |
| `VERCEL_PROJECT_ID` | Your project ID from Vercel |

**To get Vercel Token & IDs:**
1. Log in to [vercel.com](https://vercel.com)
2. Click your profile icon → "Settings"
3. Click "Tokens" (left sidebar)
4. Click "Create Token"
5. Copy the token and save as `VERCEL_TOKEN`
6. Go to your project page
7. Copy the Project ID and Organization ID shown at the top

### Part C: Enable GitHub Actions

1. Go to your repository
2. Click "Actions" tab
3. Click "I understand my workflows, go ahead and enable them"

**That's it!** Your pipeline will now:
- ✅ Run automatically every hour
- ✅ Collect fresh comments
- ✅ Analyze sentiment
- ✅ Update your report
- ✅ Deploy to Vercel automatically

---

## 📊 Understanding the Report

Your generated HTML report includes:

1. **Summary Statistics**
   - Total comments analyzed
   - Breakdown by source (YouTube vs Reddit)
   - Sentiment split (Positive, Neutral, Negative)

2. **Interactive Charts**
   - Pie charts showing sentiment distribution per source
   - Bar chart comparing YouTube vs Reddit
   - Mouse over to see exact counts

3. **Top Comments**
   - Most positive comments
   - Most negative comments
   - Score and source for each

4. **Last Updated Timestamp**
   - Shows when the report was last generated

---

## 🎯 Common Questions

### Q: Will this cost money?

**A:** No! Everything is free:
- Python: Free
- VADER sentiment analysis: Free
- Reddit API: Free (for personal use)
- YouTube comment scraping: Free
- GitHub Actions: Free (first 2000 minutes/month)
- Vercel: Free tier available

### Q: How often does it run?

**A:** By default, every hour. You can change this in `.github/workflows/pipeline.yml` on the line with `cron: '0 * * * *'`

**Common cron schedules:**
- Every hour: `'0 * * * *'` (current)
- Every 6 hours: `'0 */6 * * *'`
- Daily at 9 AM UTC: `'0 9 * * *'`
- Every Monday at 8 AM: `'0 8 * * 1'`

[Cron expression generator](https://crontab.guru)

### Q: How do I change what gets analyzed?

**A:** Edit `config.json` with new video URLs and subreddits, then commit and push to GitHub. The pipeline will automatically use the new configuration.

### Q: How much data can it handle?

**A:** By default, up to 500 comments per source per run. Change `max_comments_per_source` in `config.json` (1000+ works fine, but takes longer).

### Q: How do I see the logs?

**A:** Go to your GitHub repository → "Actions" tab → click on a workflow run → see output in real-time.

### Q: Can I run it locally on a schedule?

**A:** Yes! Use Windows Task Scheduler or cron jobs on Mac/Linux to run `python main.py` at intervals.

---

## 🔧 Troubleshooting

### Error: "REDDIT_CLIENT_ID not found"

**Solution:** Make sure you:
1. Created a `.env` file (not `.env.example`)
2. Added your Reddit credentials correctly
3. Saved the file

### Error: "ModuleNotFoundError: No module named 'praw'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "Connection refused" when collecting Reddit comments

**Solution:** Reddit API might be temporarily down. Run again in a few minutes.

### GitHub Action failing to deploy

**Solution:** Check your Vercel secrets are correct:
1. Get a fresh Vercel token (old one might have expired)
2. Make sure `VERCEL_PROJECT_ID` is set correctly

### No comments being collected

**Possible causes:**
- YouTube video has comments disabled
- Reddit API credentials wrong
- The video/subreddit has no recent comments

**Test:** Run locally with `python main.py` to see detailed error messages.

---

## 📁 Project Structure

```
argos-sentiment-project/
├── main.py                 # Main pipeline orchestrator
├── config.json            # Your configuration (edit this!)
├── requirements.txt       # Python dependencies
├── .env                   # Reddit credentials (create from .env.example)
├── .env.example          # Template for .env
│
├── config_loader.py      # Loads configuration
├── sentiment_analyzer.py # VADER sentiment analysis
├── storage.py            # SQLite database
├── youtube_collector.py  # YouTube comment scraper
├── reddit_collector.py   # Reddit comment scraper
├── report_generator.py   # HTML report generator
│
├── database/
│   └── sentiment.db      # SQLite database (created automatically)
├── reports/
│   └── index.html        # Your interactive report
└── .github/workflows/
    └── pipeline.yml      # GitHub Actions configuration
```

---

## 🚀 Advanced Usage

### Running from Command Line with Arguments

```bash
# Run with custom config file
python main.py --config my_config.json

# Run specific collectors only
python main.py --youtube-only
python main.py --reddit-only
```

### Viewing Raw Data

```bash
# Open SQLite database with any SQLite viewer
# Or use Python to query:
python -c "import sqlite3; db = sqlite3.connect('database/sentiment.db'); 
cursor = db.cursor(); 
cursor.execute('SELECT * FROM comments LIMIT 5'); 
print(cursor.fetchall())"
```

### Custom Sentiment Thresholds

Edit `sentiment_analyzer.py` to adjust when comments are marked positive/negative:

```python
# Current thresholds:
if scores['compound'] >= 0.05:  # Change 0.05 to adjust sensitivity
    label = 'Positive'
elif scores['compound'] <= -0.05:
    label = 'Negative'
```

---

## 📝 License

This project is open source and free to use.

## 💡 Tips

- **Start small:** Test with 1-2 videos before adding more
- **Monitor GitHub Actions:** Check the "Actions" tab to see pipeline runs
- **Check reports frequently:** HTML reports update automatically
- **Backup data:** SQLite database grows over time; consider backing it up

---

## 🆘 Need Help?

1. Check this README for your issue
2. Check GitHub Issues in the repository
3. Review error messages in GitHub Actions logs
4. Make sure Python 3.8+ is installed

---

**Happy analyzing! 🎉**
