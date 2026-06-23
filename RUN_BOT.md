# 🤖 Argos Sentiment Bot - Ready to Run!

Your bot is built and ready to collect Argos comments and analyze sentiment!

## Quick Start (2 Steps)

### Step 1: Make sure dependencies are installed
```bash
pip install -r requirements.txt
```

### Step 2: Run the bot
```bash
python simple_bot.py
```

---

## What It Does

✅ Collects YouTube comments about Argos  
✅ Collects X (Twitter) posts about Argos  
✅ Analyzes sentiment for each post/comment  
✅ Generates beautiful HTML report  
✅ Saves all data to local database  

---

## Output

After running, you'll get:

1. **argos_report.html** - Beautiful report with:
   - Sentiment breakdown
   - Charts comparing YouTube vs X
   - Top positive comments
   - Top negative comments
   - Statistics

2. **argos_sentiment.db** - SQLite database with all collected data

---

## View Your Report

Open this file in your browser:
```
argos_report.html
```

You'll see:
- 📊 Charts and statistics
- 😊 Positive sentiment posts
- 😞 Negative sentiment posts
- 📈 Comparison between platforms

---

## Run It Again

To collect more data:
```bash
python simple_bot.py
```

Each run adds more posts to your database and updates the report.

---

## Customize It

Want to analyze different brands? Edit `simple_bot.py`:

Change this line:
```python
x_posts = collect_x_posts("Argos", max_posts=10)
```

To:
```python
x_posts = collect_x_posts("Nike", max_posts=10)  # or any brand
```

---

## Database

All data is saved in `argos_sentiment.db`. You can:
- Query it with any SQLite viewer
- Export to CSV
- Analyze trends over time

---

**Run it now!**
```bash
python simple_bot.py
```

Then open `argos_report.html` in your browser! 🚀
