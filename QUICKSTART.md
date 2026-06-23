# ⚡ Quick Start (5 Minutes)

Get your sentiment analysis pipeline running in 5 minutes!

## Step 1: Install Python (2 min)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ⚠️ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

Verify installation - open Command Prompt/Terminal and type:
```bash
python --version
```

Should show: `Python 3.x.x`

---

## Step 2: Set Up Project (1 min)

Open Command Prompt/Terminal in your project folder:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Get Reddit Credentials (1.5 min)

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Log in (create account if needed)
3. Click "Create App"
4. Fill form:
   - Name: `SentimentAnalyzer`
   - Type: `Script`
   - Redirect URI: `http://localhost:8000`
5. Click "Create App"
6. Copy your **client ID** and **client secret**

---

## Step 4: Configure (30 sec)

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in any text editor

3. Paste your Reddit credentials:
   ```
   REDDIT_CLIENT_ID=your_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   REDDIT_USER_AGENT=SentimentAnalyzer/1.0
   ```

4. Save

---

## Step 5: Run! (30 sec)

```bash
python main.py
```

Wait for it to complete. You'll see lots of output ending with:
```
✅ PIPELINE COMPLETED SUCCESSFULLY
```

---

## Step 6: View Report (5 sec)

Open `reports/index.html` in your browser 🎉

---

## What Just Happened?

✅ Downloaded YouTube comments  
✅ Downloaded Reddit comments  
✅ Analyzed sentiment of each comment  
✅ Stored everything in local database  
✅ Generated beautiful HTML report with charts  

---

## Next: Set Up Automation

Once this works, read the full **README.md** to:
- Set up GitHub Actions to run hourly
- Deploy automatically to free Vercel hosting
- Create full CI/CD pipeline

---

## Troubleshooting

### "python: command not found"
- Python not installed or not added to PATH
- Close/reopen terminal after installing Python
- Restart computer if still failing

### "No module named 'vaderSentiment'"
```bash
pip install -r requirements.txt
```

### "Reddit credentials not configured"
- Make sure you created `.env` (not just `.env.example`)
- Make sure credentials are correct
- Make sure file is saved

### "No comments collected"
- Check video/subreddit exists
- Check credentials are correct
- Run again (API rate limits might apply)

---

**All working? Time to set up automation!** 👉 Read `README.md`
