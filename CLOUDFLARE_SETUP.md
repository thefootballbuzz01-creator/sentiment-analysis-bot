# 🧠 Connect the chatbox "brain" (free Cloudflare Worker)

Your dashboard now has a chatbox built in. To make it answer questions, it needs
a tiny free backend (a "Worker") that holds your Gemini key safely. This takes
about 5 minutes and needs **no card**.

You'll do steps 1–6, then **paste me your Worker URL** and I'll switch it on.

---

## 1. Create a free Cloudflare account
- Go to **https://dash.cloudflare.com/sign-up**
- Sign up with your email, verify it. (Free plan, no card needed.)

## 2. Create a Worker
- In the left menu, click **Workers & Pages**
- Click **Create application** → **Create Worker**
- Give it a name like **`argos-chat`** → click **Deploy**

## 3. Paste in the code
- Click **Edit code** (top right)
- **Select all** the existing code and delete it
- Open the file **`worker.js`** from your project, copy everything, and paste it in
- Click **Deploy** (top right)

## 4. Add your Gemini key as a SECRET
- Go to the Worker's **Settings** tab → **Variables and Secrets** (or **Variables**)
- Click **Add** →
  - **Type:** Secret (tick **Encrypt** if asked)
  - **Name:** `GEMINI_API_KEY`
  - **Value:** paste your free Gemini key (the same `AIza...` one)
- Click **Save / Deploy**
- *(Optional)* Add another variable — Name `GEMINI_MODEL`, Value `gemini-2.5-flash`

## 5. Copy your Worker's web address
- At the top of the Worker page you'll see a URL like:
  ```
  https://argos-chat.your-name.workers.dev
  ```
- Copy it. **This URL is safe to share** — your key stays hidden inside Cloudflare.

## 6. Tell me the URL
- Paste that `https://...workers.dev` address into our chat
- I'll plug it into your dashboard and push it live — then the chatbox on your
  public website works for anyone. 🎉

---

### Notes
- The Gemini **key never touches the public page** — it lives only as a Cloudflare
  secret. That's the secure, professional setup.
- Because the chatbox is public, anyone visiting could use your free Gemini
  quota. That's fine for a demo; if it ever gets rate-limited, it just shows a
  short "try again" message.
- Stuck on any step? Tell me which number you're on and what you see.
