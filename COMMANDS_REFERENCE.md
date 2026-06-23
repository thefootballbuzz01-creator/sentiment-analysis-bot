# 📝 Quick Commands Reference

Keep this handy while working with the project.

## Installation & Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Copy environment template
copy .env.example .env
```

## Running the Pipeline

```bash
# Run full pipeline (YouTube + Reddit)
python main.py

# Test your setup
python test_setup.py

# Run with verbose output (if supported)
python main.py --verbose
```

## Database Operations

```bash
# View database contents (requires sqlite3)
sqlite3 database/sentiment.db

# Query all comments
SELECT COUNT(*) FROM comments;

# Get sentiment breakdown
SELECT source, sentiment, COUNT(*) FROM comments GROUP BY source, sentiment;

# Export to CSV (in sqlite3)
.mode csv
.output report.csv
SELECT * FROM comments;
.quit
```

## Git Operations

```bash
# Initialize git (first time only)
git init

# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push origin main

# Pull latest changes
git pull

# View commit history
git log --oneline

# See what changed
git diff

# Undo uncommitted changes
git restore .
```

## GitHub Actions

```bash
# View workflow status (requires gh CLI)
gh workflow list

# View recent runs
gh run list

# View specific run logs
gh run view <run-id>

# Trigger workflow manually
gh workflow run pipeline.yml
```

## Python Utilities

```bash
# Check Python version
python --version

# List installed packages
pip list

# Upgrade pip
python -m pip install --upgrade pip

# Install specific version
pip install package-name==1.2.3

# Freeze current environment
pip freeze > requirements.txt

# Check for outdated packages
pip list --outdated
```

## Directory Navigation

```bash
# Change to project directory
cd C:\Users\Lenovo\Desktop\argos-sentiment-project

# List files
ls          # Mac/Linux
dir         # Windows
ls -la      # Detailed list

# Create new directory
mkdir folder-name

# Remove directory
rmdir folder-name

# View file contents
cat file.txt        # Mac/Linux
type file.txt       # Windows
```

## Development

```bash
# Edit files (recommended)
# VS Code: code .
# Notepad: notepad filename.txt

# Run tests
python test_setup.py

# Check for syntax errors
python -m py_compile main.py

# View last updated time on a file
ls -l filename       # Mac/Linux
dir filename         # Windows
```

## Vercel (Deployment)

```bash
# Install Vercel CLI (optional)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variable
vercel env add VARIABLE_NAME

# View environment variables
vercel env ls
```

## Useful Links

- Python docs: https://docs.python.org/3/
- GitHub: https://github.com
- Vercel: https://vercel.com
- Reddit API: https://www.reddit.com/prefs/apps
- Cron scheduler: https://crontab.guru

## Common Issues & Quick Fixes

```bash
# Module not found
# Solution: pip install -r requirements.txt

# Permission denied (Mac/Linux)
# Solution: chmod +x script.py

# Port already in use
# Solution: lsof -ti:PORT | xargs kill -9

# Clear Python cache
# Solution: find . -type d -name __pycache__ -exec rm -r {} +

# Reset git to last commit
# Solution: git reset --hard HEAD

# See what will be deleted (dry run)
# Solution: git clean -fd --dry-run
```

## Environment Variables

If not using .env file, set directly:

```bash
# Windows
set REDDIT_CLIENT_ID=your_id
set REDDIT_CLIENT_SECRET=your_secret

# Mac/Linux
export REDDIT_CLIENT_ID=your_id
export REDDIT_CLIENT_SECRET=your_secret
```

---

**Tip:** Bookmark this page for quick reference!
