# 🚀 Deployment Guide (GitHub Actions + Vercel)

Complete guide to set up automated sentiment analysis that runs every hour and deploys to Vercel.

## Prerequisites

- ✅ Completed the Quick Start (locally working pipeline)
- ✅ GitHub account ([github.com](https://github.com))
- ✅ Reddit API credentials (from Quick Start)
- ✅ Project pushed to GitHub

---

## Part 1: Push to GitHub

### 1.1 Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it: `argos-sentiment-project`
3. Description: "Automated sentiment analysis pipeline"
4. Choose Public or Private (private is safer)
5. Click "Create repository"

### 1.2 Push Your Code

After creating the repository, GitHub shows you instructions. Run these:

```bash
cd C:\Users\Lenovo\Desktop\argos-sentiment-project

git init
git add .
git commit -m "Initial commit: sentiment analysis pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/argos-sentiment-project.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Part 2: Set Up Vercel

Vercel hosts your reports for free.

### 2.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Choose "Continue with GitHub"
4. Authorize GitHub

### 2.2 Create Project

1. Click "Add New..." → "Project"
2. Select your repository
3. Click "Import"
4. In the "Configure Project" screen:
   - Framework: `Other`
   - Build Command: `echo "Skipping build"`
   - Output Directory: `reports`
5. Click "Deploy"

**Wait for deployment to finish** (usually 1-2 minutes)

### 2.3 Get Vercel IDs

After deployment, you need three IDs:

**Get VERCEL_TOKEN:**
1. Click your profile icon (top-right)
2. Click "Settings"
3. Click "Tokens" (left sidebar)
4. Click "Create Token"
5. Name it: `GitHub-Actions`
6. Scope: `Full Account`
7. Click "Create"
8. **Copy the token** - you'll need it in a moment

**Get VERCEL_ORG_ID and VERCEL_PROJECT_ID:**
1. Go back to your project page
2. Click "Settings"
3. Look for these IDs:
   - `projectId=xxxx` → this is **VERCEL_PROJECT_ID**
   - `teamId=xxxx` → this is **VERCEL_ORG_ID**
   - (Or look at the URL - it shows both)

---

## Part 3: Configure GitHub Secrets

GitHub Secrets store sensitive info (credentials) securely.

### 3.1 Add Secrets

1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions" (left sidebar)
4. Click "New repository secret"

**Add 5 secrets:**

| Name | Value | Where to Find |
|------|-------|---------------|
| `REDDIT_CLIENT_ID` | From .env | From Reddit app page |
| `REDDIT_CLIENT_SECRET` | From .env | From Reddit app page |
| `VERCEL_TOKEN` | Got from Vercel | Vercel account settings |
| `VERCEL_ORG_ID` | Got from Vercel | Vercel project settings |
| `VERCEL_PROJECT_ID` | Got from Vercel | Vercel project settings |

**How to add each secret:**
1. Click "New repository secret"
2. Paste the name (exactly as shown)
3. Paste the value
4. Click "Add secret"
5. Repeat for all 5

---

## Part 4: Enable GitHub Actions

### 4.1 Activate Workflow

1. Go to your repository
2. Click "Actions" tab
3. You should see "Sentiment Analysis Pipeline" listed
4. If it says "Workflows disabled", click "Enable GitHub Actions"

---

## Part 5: Test the Setup

### 5.1 Trigger First Run Manually

1. Go to "Actions" tab
2. Click "Sentiment Analysis Pipeline" (left sidebar)
3. Click "Run workflow" (top-right)
4. Click "Run workflow" button

**Watch the run:**
1. You'll see a new workflow run appear
2. Click on it to see live logs
3. Watch for ✅ or ❌

Expected output:
```
✅ Configuration loaded
✅ Database initialized
✅ Connected to Reddit API
✅ Collection complete
✅ PIPELINE COMPLETED SUCCESSFULLY
```

### 5.2 Check Vercel Deployment

1. Go to [vercel.com](https://vercel.com)
2. Click on your project
3. You should see a new deployment with recent timestamp
4. Click the URL at top to view your live report

---

## Part 6: Verify Automation

### 6.1 Schedule Check

The workflow is set to run every hour at :00 (12:00, 1:00, 2:00, etc UTC).

To see the schedule:
1. Go to "Actions" tab
2. Click "Sentiment Analysis Pipeline"
3. You should see a "scheduled" run every hour

### 6.2 View Live Reports

Your reports are now live at your Vercel URL:
- Check it in your browser
- Refresh after the next scheduled run (up to 1 hour)

---

## 📋 Customization

### Change Frequency

Edit `.github/workflows/pipeline.yml` line with `cron:`:

**Common schedules:**
- Every 6 hours: `'0 */6 * * *'`
- Every day at 9 AM UTC: `'0 9 * * *'`
- Every Monday 8 AM UTC: `'0 8 * * 1'`

[Cron generator](https://crontab.guru)

### Change YouTube/Reddit URLs

Edit `config.json` and push to GitHub. Workflow automatically uses new config.

### Stop Automation

Rename `.github/workflows/pipeline.yml` to something else to disable.

---

## 🆘 Troubleshooting

### Workflow Not Running

**Problem:** Workflow shows "disabled" or "no runs"

**Solution:**
1. Go to "Actions" tab
2. Click "I understand my workflows, go ahead and enable them"
3. Check that `.github/workflows/pipeline.yml` exists

### Workflow Fails (Red X)

**Problem:** Workflow run shows ❌

**Solution:**
1. Click on the failed run
2. Expand the failed step to see error
3. Common errors:
   - **"REDDIT_CLIENT_ID not set"** → Secret not added correctly
   - **"Deployment failed"** → Vercel credentials wrong
   - **"Connection refused"** → Temporary API issue, will retry next hour

### Reports Not Updated

**Problem:** Report shows old data

**Solution:**
1. Check "Actions" tab - see if latest run completed ✅
2. Wait for next scheduled run (up to 1 hour)
3. Manually trigger run to test

### Can't See Updated Report

**Problem:** Vercel URL shows old report

**Solution:**
1. Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` Mac)
2. Clear cache: Open DevTools (F12) → Network → check "Disable cache" → refresh
3. Wait 2-3 minutes for deployment to complete

---

## 📊 Monitor Your Pipeline

### GitHub Actions Dashboard

View all runs: Repository → Actions → Sentiment Analysis Pipeline

Each run shows:
- ⏱️ Start time
- ⏳ Duration
- ✅ Success or ❌ Failure
- 📝 Full logs

### Vercel Deployments

View all deployments: Vercel Dashboard → Project → Deployments

Each deployment shows:
- 📅 Deployment time
- 🌍 Live URL
- ✅ Status
- 📝 Build logs

---

## 🔐 Security Best Practices

1. **Never commit .env** - Already in .gitignore ✓
2. **Use GitHub Secrets** - Never paste credentials in code or comments ✓
3. **Restrict repository access** - Use Private repository if sensitive
4. **Rotate credentials** - Change Reddit/Vercel secrets monthly
5. **Review workflow changes** - Check before merging changes to `.github/workflows/`

---

## 💾 Backups

SQLite database grows over time. To back up:

1. Go to your repository
2. Click "Actions"
3. Find a successful run
4. Click "Artifacts" (if available)
5. Download database.zip

Or manually:
```bash
git pull
# Copy database/sentiment.db somewhere safe
```

---

## 🚀 Next Steps

- ✅ Automation running hourly
- ✅ Reports deployed to Vercel
- ✅ Comments collected and analyzed automatically

**Optional enhancements:**
- Add email notifications when errors occur
- Create Slack webhook to notify on reports
- Add custom sentiment thresholds
- Analyze by date ranges
- Add more video URLs or subreddits

---

**Questions?** Check README.md or review GitHub Actions logs for detailed error messages.
