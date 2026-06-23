# 🤖 Autonomous Sentiment Analysis Bot - Setup Guide

Your bot is ready to collect real YouTube comments and X tweets with full customer sentiment analysis!

## Quick Setup (10 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get X API Token (Free, 5 minutes)

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create/sign in to your account
3. Create an app → copy **Bearer Token**

### Step 3: Set Token in Environment

**Windows Command Prompt:**
```bash
set X_BEARER_TOKEN=your_token_here
```

**Or create .env file:**
```
X_BEARER_TOKEN=your_token_here
```

### Step 4: Configure Bot

Edit `autonomous_bot.py` and change:

```python
# Line ~30-35
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    # Add more videos
]

X_SEARCHES = [
    "Your Keyword",  # e.g., "Argos", "Nike", "customer service"
    # Add more keywords
]
```

### Step 5: Run the Bot

```bash
python autonomous_bot.py
```

You'll see:
```
🎬 [YOUTUBE] Collecting comments...
  ✓ 50 comments
✅ Downloaded 50 comments

🐦 [X] Collecting tweets...
  ✓ 50 tweets
✅ Downloaded 50 tweets

📊 Analyzing customer sentiment...
  📈 Today's Summary:
     Total posts: 100
     Positive: 70 (70%)
     Negative: 20 (20%)
     Neutral: 10 (10%)
     Avg Score: 0.45

  😊 Customer Satisfaction: 70%
     Status: ✅ EXCELLENT

📊 Generating dashboard...
✅ Dashboard saved: dashboard.html
```

### Step 6: View Dashboard

Open in your browser:
```
dashboard.html
```

You'll see:
- 📊 Customer satisfaction score
- 😊 Sentiment breakdown
- 💚 Top positive feedback
- ❤️ Top negative feedback
- 🔴 Common issues identified
- 📈 YouTube vs X comparison

---

## Make It Fully Autonomous (Runs 24/7)

### Option A: Schedule Locally (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set to run daily: `python C:\...\autonomous_bot.py`

### Option B: GitHub Actions (Recommended - Runs Every Hour)

1. Push to GitHub
2. Add GitHub Secrets:
   - `X_BEARER_TOKEN` = your token
3. It runs automatically every hour!

---

## What It Analyzes

✅ **Real YouTube Comments**
- Downloads actual comments from your videos
- Analyzes sentiment
- Identifies issues

✅ **Real X Tweets**
- Searches for your keywords
- Collects public tweets
- Analyzes sentiment

✅ **Customer Sentiment**
- Calculates satisfaction score
- Identifies common issues (delivery, quality, price, etc.)
- Tracks trends over time
- Compares YouTube vs X

✅ **Issues Detected**
- Delivery problems
- Quality complaints
- Pricing concerns
- Customer service issues
- Website/app problems

---

## Database

All data saved in: `customer_sentiment.db`

Run anytime:
```bash
python autonomous_bot.py
```

Each run adds more data. Dashboard updates automatically!

---

## Customization

**Change what to analyze:**
```python
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=abc123",
    "https://www.youtube.com/watch?v=def456",
]

X_SEARCHES = [
    "Nike shoes",
    "Apple customer service",
    "Amazon delivery",
]
```

**Change comment/tweet limits:**
```python
collect_youtube(max_comments=100)  # Default: 50
collect_x(max_posts=100)  # Default: 50
```

---

## Output Files

- `dashboard.html` - Interactive dashboard (open in browser)
- `customer_sentiment.db` - SQLite database with all data
- `console output` - Real-time progress

---

## That's It!

You now have a fully autonomous bot that:
- ✅ Collects real YouTube comments
- ✅ Collects real X tweets
- ✅ Analyzes customer sentiment
- ✅ Identifies issues
- ✅ Generates beautiful dashboards
- ✅ Runs 24/7 (if set up with scheduling)

**Run it now:**
```bash
python autonomous_bot.py
```

Then open `dashboard.html` to see results! 🚀
