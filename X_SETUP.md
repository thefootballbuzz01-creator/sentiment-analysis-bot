# 🐦 X (Twitter) API Setup Guide

Follow these steps to get your X API credentials.

## Step 1: Create Developer Account

1. Go to: [developer.twitter.com](https://developer.twitter.com)
2. Click "Sign up" (or sign in if you have an account)
3. Use your existing X account or create one
4. Fill out the developer application form:
   - **Use case**: Academic research / Data analysis
   - **Description**: "Sentiment analysis of tweets for research purposes"
5. Accept terms and verify email
6. Wait for approval (usually instant)

---

## Step 2: Create an Application

1. Go to [developer.twitter.com/en/portal/dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click "Create App"
3. Name your app: `SentimentAnalyzer`
4. Click "Create"

---

## Step 3: Get Your Credentials

1. In your app dashboard, click the **"Keys and tokens"** tab
2. You'll see several sections:

### API Key & Secret
- **API Key** = Copy this → use as `X_API_KEY`
- **API Secret** = Copy this → use as `X_API_SECRET`

### Bearer Token
- Scroll down to "Authentication Tokens"
- Click "Generate" for Bearer Token
- Copy the token → use as `X_BEARER_TOKEN`

---

## Step 4: Add to .env File

1. Open `.env` in your project folder (in text editor)
2. Paste your credentials:

```
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

3. Save the file

---

## Step 5: Set Permissions

1. In your app dashboard, go to **Settings**
2. Find **App Permissions** → set to **Read only** (since we're only reading tweets)
3. Save

---

## Important Notes

⚠️ **Keep your tokens secret!**
- Never share these with anyone
- Never commit them to GitHub
- They're like passwords for your X account

✅ **Rate Limits**
- Free tier allows 300 tweets per 15 minutes
- Our pipeline respects these limits

✅ **Public Tweets Only**
- We only collect public tweets
- No private/protected account data

---

## Testing Your Credentials

Once added to .env, run:

```bash
python main.py
```

If it works, you'll see:
```
✅ Connected to X (Twitter) API
```

If it fails, check:
1. `.env` file exists and saved correctly
2. No extra spaces in credentials
3. Credentials are accurate (copy-paste carefully)
4. API key/secret match your app

---

## Troubleshooting

**Error: "Bearer Token not found"**
- Make sure `.env` file is created (not `.env.example`)
- Check spelling: `X_BEARER_TOKEN=`

**Error: "401 Unauthorized"**
- Your token might be invalid
- Generate a new token from developer dashboard
- Update `.env` with new token

**Error: "429 Too Many Requests"**
- You've hit the rate limit
- Wait 15 minutes and try again
- Our pipeline automatically spaces requests out

---

**All set?** Run `python main.py` to start collecting tweets! 🚀
