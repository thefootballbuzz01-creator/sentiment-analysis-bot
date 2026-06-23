# 🤖 Argos Bot - REAL Data Collection

Your bot now collects **REAL YouTube comments** and **REAL X tweets**!

## Quick Start

### Step 1: Update Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Edit the Bot (Optional)

Open `simple_bot.py` and change the YouTube URL to analyze a different video:

```python
youtube_url = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

To find a video ID:
1. Go to YouTube
2. Open any video
3. Copy the URL from address bar
4. Use it in the bot

### Step 3: Run the Bot
```bash
python simple_bot.py
```

### Step 4: View Results
Open `argos_report.html` in your browser

---

## What You Get

✅ **Real YouTube Comments**
- From actual videos
- Real people's opinions
- Analyzed for sentiment

✅ **Real X Tweets**
- About "Argos" keyword
- Public tweets
- Analyzed for sentiment

✅ **Beautiful Report**
- Charts comparing YouTube vs X
- Top positive/negative posts
- Sentiment breakdown
- Statistics

---

## Example Usage

### Analyze Argos YouTube Video

1. Find an Argos video on YouTube
2. Copy the URL: `https://www.youtube.com/watch?v=abc123def456`
3. Edit `simple_bot.py`:
   ```python
   youtube_url = "https://www.youtube.com/watch?v=abc123def456"
   ```
4. Run: `python simple_bot.py`

### Analyze Different Search Term

Edit `simple_bot.py`:
```python
x_posts = collect_x_posts("Nike", max_posts=20)  # Changed from "Argos"
```

---

## Database

All collected data is saved in `argos_sentiment.db`

View it:
- Open with any SQLite viewer
- Or query with Python
- Data persists between runs

---

## Run Multiple Times

Each time you run the bot, it adds more data:
```bash
python simple_bot.py
```

Your database and reports grow with each run!

---

## Troubleshooting

**No YouTube comments collected?**
- Video might have comments disabled
- Try a different video
- Check the URL format

**No X tweets collected?**
- Search term might be too specific
- Try a more common keyword
- Can take a minute to collect

**Report not updating?**
- Refresh the browser (F5)
- Or delete `argos_report.html` and run bot again

---

## That's It!

You now have a bot that collects REAL sentiment data from YouTube and X! 🚀

```bash
python simple_bot.py
```

Run it, open the report, and see the sentiment analysis! 👍
