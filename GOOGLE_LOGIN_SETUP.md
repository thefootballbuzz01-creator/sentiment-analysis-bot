# 🔐 Turn on "Sign in with Google" (free)

The dashboard already has the Google sign-in gate built in. To switch it on, you
need **one thing I can't create for you: a Google OAuth Client ID** (it's free
and uses your existing Google account). Get it, paste it to me, and I'll activate it.

> Honest note: this is a **front-end** login — it shows who's signing in and gates
> the page, which is perfect for a demo/presentation. It is NOT bank-level security
> (a static website has no server to truly enforce it). For coursework it's exactly
> what "add authentication" means; just know the limit.

---

## Get your Client ID (~5 minutes)

1. Go to **https://console.cloud.google.com** and sign in with your Google account
2. Top bar → **project dropdown → New Project** → name it `argos-dashboard` → **Create** (then select it)
3. Left menu → **APIs & Services → OAuth consent screen**
   - User type: **External** → **Create**
   - App name: `Argos Dashboard` · User support email: your email · Developer email: your email
   - **Save and continue** through the steps (you can skip scopes); under **Test users** add your own email → **Save**
4. Left menu → **APIs & Services → Credentials**
   - **Create credentials → OAuth client ID**
   - Application type: **Web application**
   - Name: `Argos dashboard web`
   - Under **Authorized JavaScript origins → Add URI**, paste exactly:
     ```
     https://thefootballbuzz01-creator.github.io
     ```
   - Click **Create**
5. A box pops up with your **Client ID** — it looks like:
   ```
   123456789-abc123def456.apps.googleusercontent.com
   ```
   Copy it.

## Then tell me
Paste that Client ID into our chat (it's **not** a secret — Client IDs are meant to
be public and embedded in web pages). I'll drop it into the dashboard, push it, and
the "Sign in with Google" gate goes live on your site.

---

### Notes
- Until you add the Client ID, the dashboard stays **open** (no gate) so you're never locked out.
- The gate is also **skipped when you open the file locally** (so your own testing always works).
- If sign-in says "unverified app", that's normal for a test project — click **Advanced → continue**, or use the email you added as a Test user.
