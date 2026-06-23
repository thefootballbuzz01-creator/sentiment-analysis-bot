# ⚡ YouTube + X (Twitter) - Quick Start (10 Minutes)

**Get real sentiment analysis from YouTube videos and X tweets!**

## Step 1: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

Wait for: `Successfully installed...`

---

## Step 2: Get X API Credentials (5 min)

**Quick Version:**
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create an account or sign in
3. Click "Create App"
4. Name it: `SentimentAnalyzer`
5. Copy your **API Key**, **API Secret**, and **Bearer Token**

**Detailed Instructions:**
→ Read `X_SETUP.md` in your project folder

---

## Step 3: Add Credentials

1. Open `.env` in your project folder (text editor)
2. Replace the placeholders:

```
X_API_KEY=your_key_here
X_API_SECRET=your_secret_here
X_BEARER_TOKEN=your_token_here
```

3. Save the file

---

## Step 4: Configure Videos & Searches

Edit `config.json`:

**YouTube videos:**
```json
"youtube": {
  "enabled": true,
  "videos": [
    {
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "label": "Video Name"
    }
  ]
}
```

**X searches:**
```json
"x": {
  "enabled": true,
  "searches": [
    {
      "query": "python programming",
      "label": "Python Posts"
    }
  ]
}
```

---

## Step 5: Run the Pipeline

```bash
python main.py
```

You'll see:
```
✅ Connected to X (Twitter) API
=== YouTube Comment Collection ===
📝 Collecting comments...
=== X (Twitter) Tweet Collection ===
📝 Collecting tweets...
✅ PIPELINE COMPLETED SUCCESSFULLY
```

---

## Step 6: View Report

Open this file in your browser:

```
reports/index.html
```

You'll see:
✅ YouTube sentiment breakdown  
✅ X (Twitter) sentiment breakdown  
✅ Comparison charts  
✅ Top positive & negative posts  

---

## Example Inputs

### YouTube URLs
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
```

### X Search Queries
```
python
machine learning
web development
javascript
```

---

## Any Issues?

**X connection failed?**
- Check `.env` credentials are correct
- No spaces before/after values
- Read X_SETUP.md for detailed help

**No comments collected?**
- Video might have comments disabled
- X might have rate limits (wait 15 min)
- Check your search queries are valid

**Module not found?**
```bash
pip install -r requirements.txt
```

---

## Next Steps

- ✅ Run it again to collect more data
- ✅ Change config.json to analyze different content
- ✅ Set up automation (GitHub Actions + Vercel)
   → Read README.md for automation setup

---

**Done! Enjoy your sentiment analysis!** 🚀
