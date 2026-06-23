# 🚀 START HERE - Web Form Version (Super Easy!)

**No Python needed. Just paste URLs and click.**

## Step 1: Install Node.js (2 minutes)

1. Go to [nodejs.org](https://nodejs.org)
2. Download the LTS version
3. Run the installer
4. Click "Next" all the way through

Verify installation - open Command Prompt/Terminal and type:
```
node --version
```

Should show: `v18.x.x` or similar

---

## Step 2: Install Dependencies (1 minute)

In Command Prompt/Terminal:

```bash
cd C:\Users\Lenovo\Desktop\argos-sentiment-project

npm install
```

Wait for it to finish (shows ✓ or ✅ when done).

---

## Step 3: Start the Web Server (30 seconds)

```bash
npm start
```

You'll see:
```
============================================================
  🎯 SENTIMENT ANALYZER
============================================================

  ✅ Server running at http://localhost:3000
```

---

## Step 4: Open in Your Browser (10 seconds)

Click this link: [http://localhost:3000](http://localhost:3000)

Or type it in your browser address bar.

---

## Step 5: Use It!

1. **Paste YouTube URLs** (optional) - one per line
2. **Paste Reddit subreddits** (optional) - one per line
3. Click **"🚀 Analyze Now"**
4. See charts and results instantly! 📊

---

## Example Inputs

### YouTube URLs
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
```

### Reddit Subreddits
```
python
learnprogramming
AskReddit
```

---

## Stop It

Press `Ctrl+C` in the terminal to stop the server.

---

## Restart It

Run `npm start` again.

---

## Troubleshooting

**Error: "npm: command not found"**
- Node.js not installed or not added to PATH
- Close and reopen terminal
- Restart computer if needed

**Error: "Port 3000 already in use"**
- Something else is using port 3000
- Close other programs or restart computer
- Or edit `server.js` and change `3000` to `3001`

**Nothing shows in results**
- This is a demo version
- It generates realistic sample data
- In production, it would connect to YouTube/Reddit APIs

---

## Next Steps

This is a **demo version** with sample data. To connect real YouTube/Reddit data:

1. Go back to the Python version (QUICKSTART.md)
2. Or wait - we can enhance this!

---

**That's it! Enjoy!** 🎉

Close this and open http://localhost:3000 in your browser.
