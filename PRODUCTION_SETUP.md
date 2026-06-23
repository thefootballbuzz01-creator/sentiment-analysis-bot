# 🚀 Production Setup - Real YouTube + X with Hourly Automation

Your bot will collect **REAL data** from YouTube and X, updating **every hour automatically**.

---

## Step 1: Get API Keys (15 minutes, one-time)

### YouTube API Key (Free)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (any name)
3. Go to "APIs & Services" → "Library"
4. Search "YouTube Data API v3"
5. Click it → "Enable"
6. Go to "Credentials" (left sidebar)
7. Click "Create Credentials" → "API Key"
8. **Copy your API key** - you'll need it soon

### X (Twitter) Bearer Token (Free)

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create/sign in to account
3. Go to "Projects & apps"
4. Create a new app
5. Go to "Keys and tokens"
6. Under "Bearer Token" → "Generate"
7. **Copy your Bearer Token** - you'll need it soon

---

## Step 2: Push to GitHub

### Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name: `sentiment-analysis-bot`
3. Make it **Public** (Vercel needs this for free tier)
4. Click "Create repository"

### Push Your Code

```bash
cd C:\Users\Lenovo\Desktop\argos-sentiment-project

git init
git add .
git commit -m "Initial: production sentiment bot with real APIs"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sentiment-analysis-bot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 3: Add GitHub Secrets

These store your API keys securely.

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"

**Add these 5 secrets:**

| Name | Value |
|------|-------|
| `YOUTUBE_API_KEY` | Your YouTube API key |
| `X_BEARER_TOKEN` | Your X Bearer token |
| `VERCEL_TOKEN` | [Get here](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Your Vercel org ID |
| `VERCEL_PROJECT_ID` | Your Vercel project ID |

**How to add each secret:**
1. Click "New repository secret"
2. Name: (copy from table above)
3. Value: (paste the token)
4. Click "Add secret"
5. Repeat for all 5

---

## Step 4: Get Vercel Credentials

### Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Authorize GitHub

### Get Token

1. Click your profile icon (top right)
2. Click "Settings"
3. Click "Tokens" (left sidebar)
4. Click "Create Token"
5. Name: `github-actions`
6. Scope: `Full Account`
7. **Copy the token** → Add as `VERCEL_TOKEN` secret

### Get Project IDs

1. Go back to Vercel Dashboard
2. Click "Add New..." → "Project"
3. Select your GitHub repo
4. Deploy it (just once to create it)
5. Once deployed, click "Settings"
6. Look for:
   - `projectId=xxx` → This is **VERCEL_PROJECT_ID**
   - `teamId=xxx` → This is **VERCEL_ORG_ID**

Add both to GitHub secrets.

---

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client tweepy
```

---

## Step 6: Test Locally (Optional)

```bash
set YOUTUBE_API_KEY=your_key_here
set X_BEARER_TOKEN=your_token_here
python production_bot.py
```

You'll see:
```
🎬 REAL YouTube Collection
  Searching: 'product reviews'
    📹 Video: https://www.youtube.com/watch?v=...
      ✅ [Positive] Amazing product review...
      ✅ Collected 20 comments

🐦 REAL X Collection
  Searching: 'product review'
    ✅ [Positive] Great product review...
    ✅ Collected 15 posts

📊 SENTIMENT ANALYSIS RESULTS
   Total Posts: 500
   Positive: 350 (70%)
   Negative: 100 (20%)
   Neutral: 50 (10%)
   Satisfaction: 70%
```

---

## Step 7: GitHub Actions Runs Automatically

Once you push to GitHub with secrets configured:

✅ **Every hour** at :00 (1:00, 2:00, 3:00, etc.)
✅ Automatically collects REAL YouTube comments
✅ Automatically collects REAL X tweets
✅ Analyzes sentiment
✅ Updates dashboard
✅ Deploys to Vercel

**You can see runs:**
1. Go to your GitHub repo
2. Click "Actions" tab
3. See all scheduled runs
4. Click one to see logs

---

## Step 8: View Live Dashboard

Your dashboard is live at:
```
https://your-project.vercel.app
```

It **updates every hour automatically** with new sentiment analysis!

---

## How It Works

```
Every Hour (Automated via GitHub Actions)
    ↓
Run production_bot.py
    ↓
Collect REAL YouTube comments (YouTube API)
    ↓
Collect REAL X tweets (X API)
    ↓
Analyze sentiment with VADER
    ↓
Store in SQLite database
    ↓
Generate index.html dashboard
    ↓
Commit changes to GitHub
    ↓
Deploy to Vercel automatically
    ↓
Live dashboard updates at your Vercel URL
```

---

## Dashboard Features

✅ Real YouTube comments with sentiment scores
✅ Real X tweets with sentiment scores
✅ Customer satisfaction percentage
✅ Positive/Negative/Neutral breakdown
✅ Charts and visualizations
✅ Top positive & negative feedback
✅ "Live" indicator showing auto-updates
✅ Last updated timestamp

---

## Troubleshooting

**GitHub Actions shows error?**
- Check you added all 5 secrets correctly
- Check API keys are valid
- Check repo is public (for Vercel free tier)

**No data showing?**
- YouTube API key might be invalid
- X Bearer token might be invalid
- Check you enabled YouTube Data API v3
- Check rate limits aren't exceeded

**Dashboard not updating?**
- Wait for next hour (cron runs on the hour)
- Or click "Run workflow" manually in Actions tab

---

## What You Have Now

🚀 **Production-Ready System**
- ✅ Real YouTube API integration
- ✅ Real X API integration
- ✅ Hourly automatic collection
- ✅ Sentiment analysis on every post
- ✅ Live dashboard
- ✅ Auto-deployment to Vercel
- ✅ All free, no cost

---

## Next Steps

1. ✅ Get API keys (Step 1)
2. ✅ Push to GitHub (Step 2)
3. ✅ Add secrets (Step 3)
4. ✅ Get Vercel credentials (Step 4)
5. ✅ GitHub Actions runs automatically
6. ✅ View live dashboard

**That's it! Your bot now runs 24/7 automatically.** 🎉

---

## Manual Testing

To test a run manually:
1. Go to GitHub repo
2. Click "Actions" tab
3. Click "Hourly Sentiment Analysis"
4. Click "Run workflow"
5. Check the logs

---

**Questions?** Check the logs in GitHub Actions for detailed error messages.

**Ready to go live?** Follow the steps above and you're done! 🚀
