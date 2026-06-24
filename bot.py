#!/usr/bin/env python3
"""
YouTube Sentiment Analysis Bot  (REAL data, no API key needed)

What it does, fully automatically:
  1. Reads search terms from config.json
  2. Finds real YouTube videos for each term
  3. Downloads the real comments from those videos
  4. Scores each comment with VADER sentiment analysis
  5. Stores everything in a local SQLite database
  6. Builds an interactive report.html

Just run:  python bot.py
"""

import json
import os
import re
import sqlite3
import sys
import webbrowser
from datetime import datetime

# Windows terminals default to an old encoding that can't print emoji.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

# Google Play reviews (optional second source; bot still works without it).
try:
    from google_play_scraper import reviews as gp_reviews, Sort as GPSort
    GPLAY = True
except Exception:
    GPLAY = False

analyzer = SentimentIntensityAnalyzer()

# Resolve files next to this script, so it works no matter what folder
# Windows Task Scheduler launches it from.
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "sentiment.db")
CONFIG = os.path.join(BASE, "config.json")
REPORT = os.path.join(BASE, "report.html")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# "Argos" is also a watch brand and shows up on fragrance channels. These
# domain words flag comments that clearly aren't about Argos the retailer,
# so we skip them. Kept specific so genuine shop comments are never dropped.
OFFTOPIC = ("dial", "bezel", "wristwatch", "sapphire", "quartz",
            "chronograph", "fragrance", "perfume", "cologne", "aftershave",
            "eau de", "sillage", "decant", "olympia")

# The dashboard chatbox sends questions to this Cloudflare Worker (the "brain"
# that holds the Gemini key). Paste your Worker URL here after deploying it
# (see CLOUDFLARE_SETUP.md). Until then the chatbox shows a friendly notice.
CHAT_WORKER_URL = os.getenv("CHAT_WORKER_URL", "PASTE_YOUR_WORKER_URL_HERE")


# ---------------------------------------------------------------- config
def load_config():
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- database
def setup_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id    TEXT,
            search_term TEXT,
            author      TEXT,
            text        TEXT,
            sentiment   TEXT,
            score       REAL,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(video_id, author, text)
        )
        """
    )
    # Older databases predate the multi-source `source` column — add it once.
    cols = [r[1] for r in conn.execute("PRAGMA table_info(comments)")]
    if "source" not in cols:
        conn.execute(
            "ALTER TABLE comments ADD COLUMN source TEXT DEFAULT 'YouTube'"
        )
    conn.commit()
    conn.close()


def save_comment(source, video_id, term, author, text, sentiment, score):
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO comments "
            "(source, video_id, search_term, author, text, sentiment, score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source, video_id, term, author, text, sentiment, score),
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


# ---------------------------------------------------------------- sentiment
def analyze(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive", score
    if score <= -0.05:
        return "Negative", score
    return "Neutral", score


# ---------------------------------------------------------------- youtube
def find_videos(term, limit):
    """Search YouTube and return real video IDs (no API key needed)."""
    url = "https://www.youtube.com/results?search_query=" + term.replace(" ", "+")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        return list(dict.fromkeys(ids))[:limit]  # de-duplicate, keep order
    except Exception as e:
        print(f"    ! search failed: {e}")
        return []


def collect_comments(video_id, term, max_comments):
    url = f"https://www.youtube.com/watch?v={video_id}"
    downloader = YoutubeCommentDownloader()
    new = 0
    try:
        for c in downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR):
            if new >= max_comments:
                break
            text = (c.get("text") or "").strip()
            if len(text) < 3:
                continue
            if any(w in text.lower() for w in OFFTOPIC):   # skip watch/fragrance noise
                continue
            author = c.get("author", "Unknown")
            sentiment, score = analyze(text)
            if save_comment("YouTube", video_id, term, author, text,
                            sentiment, score):
                new += 1
    except Exception as e:
        print(f"    ! comments failed: {e}")
    return new


# ---------------------------------------------------------------- google play
def collect_play_reviews(package, label, max_reviews):
    """Download real Google Play reviews for an app (no API key needed)."""
    if not GPLAY:
        print("    ! google-play-scraper not installed")
        return 0
    new = 0
    try:
        revs, _ = gp_reviews(package, lang="en", country="gb",
                             sort=GPSort.NEWEST, count=max_reviews)
        for rv in revs:
            text = (rv.get("content") or "").strip()
            if len(text) < 3:
                continue
            author = rv.get("userName", "Google Play user")
            sentiment, score = analyze(text)
            if save_comment("Google Play", package, label, author, text,
                            sentiment, score):
                new += 1
    except Exception as e:
        print(f"    ! play reviews failed: {e}")
    return new


# ---------------------------------------------------------------- report
def build_report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Sentiment counts per source.
    cur.execute(
        "SELECT source, sentiment, COUNT(*) FROM comments GROUP BY source, sentiment"
    )
    agg = {}
    for src, sent, n in cur.fetchall():
        agg.setdefault(src, {"Positive": 0, "Negative": 0, "Neutral": 0})[sent] = n

    cur.execute(
        "SELECT author, text, score, source FROM comments "
        "WHERE sentiment='Positive' ORDER BY score DESC LIMIT 8"
    )
    top_pos = cur.fetchall()
    cur.execute(
        "SELECT author, text, score, source FROM comments "
        "WHERE sentiment='Negative' ORDER BY score ASC LIMIT 8"
    )
    top_neg = cur.fetchall()

    # All negative comments per source (with author), for theme/issue detection.
    cur.execute("SELECT source, author, text FROM comments WHERE sentiment='Negative'")
    neg_rows = cur.fetchall()

    # All comments (trimmed) embedded for the in-page chatbox to search through.
    cur.execute("SELECT source, sentiment, substr(text,1,220) FROM comments")
    chat_rows = [{"source": s, "sentiment": se, "text": t}
                 for s, se, t in cur.fetchall()]
    conn.close()

    def esc(s):
        return (
            str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    def src_tag(src):
        if src == "YouTube":
            return '<span class="src yt">YouTube</span>'
        if src == "Google Play":
            return '<span class="src gp">Google Play</span>'
        return f'<span class="src">{esc(src)}</span>'

    def cards(rows, css):
        if not rows:
            return '<p class="empty">No comments in this group yet.</p>'
        out = []
        for a, t, s, src in rows:
            initial = esc(a[:1].upper() or "?")
            out.append(
                f'<div class="card {css}">'
                f'<div class="av">{initial}</div>'
                f'<div class="cbody"><div class="ct">{esc(t)}</div>'
                f'<div class="cm"><span class="meta-left">'
                f'<span class="au">{esc(a)}</span>{src_tag(src)}</span>'
                f'<span class="sc">{s:+.2f}</span></div></div></div>'
            )
        return "".join(out)

    def stats(src):
        d = agg.get(src, {"Positive": 0, "Negative": 0, "Neutral": 0})
        p, ng, nu = d["Positive"], d["Negative"], d["Neutral"]
        tot = p + ng + nu
        f = lambda x: round(x / tot * 100, 1) if tot else 0
        return dict(tot=tot, pos=p, neg=ng, neu=nu,
                    sat=round(p / tot * 100, 1) if tot else 0.0,
                    pp=f(p), pn=f(nu), pg=f(ng))

    yt = stats("YouTube")
    gp = stats("Google Play")

    def satcolor(v):
        return "#2dd4bf" if v >= 70 else "#38bdf8" if v >= 50 else "#fb7185"

    if yt["tot"] and gp["tot"]:
        diff = yt["sat"] - gp["sat"]
        if abs(diff) < 3:
            verdict = f"Neck and neck — both about {round((yt['sat'] + gp['sat']) / 2)}% positive"
            vcolor = "#38bdf8"
        elif diff > 0:
            verdict = f"YouTube viewers are more positive  —  {yt['sat']}% vs {gp['sat']}% positive"
            vcolor = "#f87171"
        else:
            verdict = f"Google Play reviewers are more positive  —  {gp['sat']}% vs {yt['sat']}% positive"
            vcolor = "#34d399"
    else:
        verdict = "Collecting data from both platforms…"
        vcolor = "#38bdf8"

    # Themes to look for inside negative comments (what customers complain about).
    THEMES = {
        "Delivery & dispatch": ["deliver", "dispatch", "courier", "arrive",
            "late", "waiting", "shipping", "never arrived", "didn't arrive"],
        "App & website": ["app", "login", "log in", "crash", "update",
            "loading", "website", " site", "error", "bug", "glitch", "freeze",
            "slow", "won't load", "can't log"],
        "Stock & availability": ["stock", "unavailable", "availability",
            "sold out", "not available"],
        "Customer service": ["service", "staff", "support", "rude",
            "unhelpful", "response", "contact", "phone", "call", "helpline"],
        "Refunds & payment": ["refund", "money back", "payment", "charged",
            "overcharged", "voucher", "expensive", "pricing", "price"],
        "Orders & collection": ["order", "cancel", "collection", "collect",
            "missing", "wrong item", "never received", "reserve"],
        "Product quality": ["quality", "broken", "faulty", "damaged",
            "cheap", "stopped working"],
    }

    def issues_html(source):
        matches = {k: [] for k in THEMES}
        for src, author, txt in neg_rows:
            if src != source:
                continue
            tl = txt.lower()
            for theme, kws in THEMES.items():
                if any(k in tl for k in kws):
                    matches[theme].append((author, txt))
        ranked = sorted([(t, m) for t, m in matches.items() if m],
                        key=lambda x: -len(x[1]))[:5]
        if not ranked:
            return '<p class="empty">No clear issues detected yet.</p>'
        top = len(ranked[0][1])
        out = []
        for theme, ms in ranked:
            c = len(ms)
            w = round(c / top * 100)
            plural = "s" if c != 1 else ""
            def who_line(author, txt):
                return (f'<div class="who"><span class="wa">{esc(author)}</span>'
                        f'<span class="wq">“{esc(txt[:70])}…”</span></div>')

            who = [who_line(a, t) for a, t in ms[:3]]   # first 3 always shown
            if c > 3:                                    # rest behind a toggle
                extra = "".join(who_line(a, t) for a, t in ms[3:])
                who.append(
                    f'<details class="wmoredet"><summary>+{c - 3} more — '
                    f'click to see who</summary>{extra}</details>'
                )
            out.append(
                f'<div class="issue"><div class="top">'
                f'<span class="lbl">{theme}</span>'
                f'<span class="cnt">{c} mention{plural}</span></div>'
                f'<div class="track"><div class="fill" style="width:{w}%"></div></div>'
                f'<div class="whos">{"".join(who)}</div></div>'
            )
        return "".join(out)

    template = r"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTube vs Google Play — Sentiment Comparison</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{
  --bg1:#0b1f33;--bg2:#08363f;--bg3:#0a2a3a;
  --glass:rgba(255,255,255,.055);--glass2:rgba(255,255,255,.09);
  --line:rgba(255,255,255,.10);--txt:#e6f6f7;--muted:#8fb0bf;
  --pos:#2dd4bf;--neu:#38bdf8;--neg:#fb7185;
  --yt:#f87171;--gp:#34d399;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,sans-serif;color:var(--txt);
  background:linear-gradient(135deg,var(--bg1),var(--bg2),var(--bg3));
  background-attachment:fixed;padding:28px 18px;min-height:100vh}
.wrap{max-width:1180px;margin:0 auto}
.hero{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px;margin-bottom:22px}
.hero h1{font-size:2.05rem;font-weight:800;letter-spacing:-.5px;
  background:linear-gradient(90deg,#fca5a5,#fff,#6ee7b7);-webkit-background-clip:text;
  background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:var(--muted);margin-top:6px;font-size:.95rem}
.chip{display:inline-flex;align-items:center;gap:8px;background:var(--glass);
  border:1px solid var(--line);padding:9px 15px;border-radius:999px;font-size:.85rem;color:var(--muted)}
.dot{width:9px;height:9px;border-radius:50%;background:#2dd4bf;
  box-shadow:0 0 0 0 rgba(45,212,191,.6);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(45,212,191,.5)}
  70%{box-shadow:0 0 0 10px rgba(45,212,191,0)}100%{box-shadow:0 0 0 0 rgba(45,212,191,0)}}
.verdict{background:var(--glass);border:1px solid var(--line);border-radius:16px;
  padding:18px 24px;margin-bottom:18px;font-size:1.15rem;font-weight:700;text-align:center}
.grid{display:grid;gap:18px}
.vs{grid-template-columns:1fr 1fr;margin-bottom:18px}
.card-glass{background:var(--glass);border:1px solid var(--line);border-radius:18px;backdrop-filter:blur(12px)}
.platform{padding:26px;position:relative;transition:transform .25s}
.platform:hover{transform:translateY(-3px)}
.platform.ytb{border-top:3px solid var(--yt)}
.platform.gpb{border-top:3px solid var(--gp)}
.phead{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.pname{font-size:1.15rem;font-weight:800}
.pname.yt{color:var(--yt)}.pname.gp{color:var(--gp)}
.pcount{font-size:.85rem;color:var(--muted)}
.psat{font-size:3.2rem;font-weight:800;line-height:1.1}
.psat small{font-size:.95rem;font-weight:600;color:var(--muted);margin-left:8px}
.segbar{display:flex;height:26px;border-radius:9px;overflow:hidden;margin:16px 0 14px}
.segbar i{display:block;height:100%}
.legend{display:flex;flex-wrap:wrap;gap:14px}
.legend span{display:flex;align-items:center;gap:7px;font-size:.86rem;color:var(--muted)}
.legend b{color:var(--txt)}
.sw{width:11px;height:11px;border-radius:4px;display:inline-block}
.termwrap{padding:26px;margin-bottom:18px}
.termwrap h3{font-size:.8rem;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:18px}
.cols{grid-template-columns:1fr 1fr;align-items:start}
.collist h2{font-size:1.05rem;font-weight:700;margin-bottom:14px}
.card{display:flex;gap:13px;background:var(--glass);border:1px solid var(--line);
  border-left:3px solid var(--neu);border-radius:14px;padding:14px 16px;margin-bottom:11px;transition:transform .2s,background .2s}
.card:hover{transform:translateX(3px);background:var(--glass2)}
.card.pos{border-left-color:var(--pos)}.card.neg{border-left-color:var(--neg)}
.av{flex:0 0 38px;height:38px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-weight:700;color:#062a30;background:linear-gradient(135deg,#0891b2,#22d3ee)}
.card.pos .av{background:linear-gradient(135deg,#0d9488,#2dd4bf)}
.card.neg .av{color:#fff;background:linear-gradient(135deg,#e11d48,#fb7185)}
.cbody{min-width:0}
.ct{line-height:1.55;font-size:.93rem;word-wrap:break-word}
.cm{display:flex;justify-content:space-between;gap:10px;margin-top:8px;font-size:.78rem}
.au{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sc{color:var(--muted);font-variant-numeric:tabular-nums;background:var(--glass2);padding:1px 8px;border-radius:6px;flex:0 0 auto}
.meta-left{display:flex;align-items:center;gap:8px;min-width:0}
.src{font-size:.7rem;font-weight:600;padding:2px 8px;border-radius:6px;white-space:nowrap;flex:0 0 auto}
.src.yt{color:#fca5a5;background:rgba(248,113,113,.18)}
.src.gp{color:#6ee7b7;background:rgba(52,211,153,.18)}
.empty{color:var(--muted);font-size:.9rem;padding:10px 0}
.improve{padding:26px;margin-bottom:18px}
.improve h3{font-size:.8rem;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px}
.improve .note{font-size:.85rem;color:var(--muted);margin-bottom:20px}
.imp-cols{display:grid;grid-template-columns:1fr 1fr;gap:30px}
.imp-col h4{display:flex;align-items:center;gap:8px;font-size:.95rem;margin-bottom:16px}
.issue{margin-bottom:15px}
.issue .top{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:6px}
.issue .lbl{font-weight:600;font-size:.9rem}
.issue .cnt{font-size:.72rem;color:var(--muted);background:var(--glass2);padding:1px 8px;border-radius:6px;white-space:nowrap}
.issue .track{height:8px;background:rgba(255,255,255,.06);border-radius:5px;overflow:hidden}
.issue .fill{height:100%;background:var(--neg);border-radius:5px}
.whos{margin-top:8px}
.who{font-size:.76rem;margin-bottom:4px;line-height:1.4}
.wa{color:var(--txt);font-weight:700;margin-right:6px}
.wq{color:var(--muted);font-style:italic}
.wmoredet{margin-top:4px}
.wmoredet>summary{font-size:.73rem;color:#22d3ee;cursor:pointer;font-weight:600;list-style:none;display:inline-block}
.wmoredet>summary::-webkit-details-marker{display:none}
.wmoredet>summary:hover{text-decoration:underline}
.wmoredet[open]>summary{margin-bottom:6px}
.foot{text-align:center;color:var(--muted);font-size:.82rem;margin-top:30px;padding-top:20px;border-top:1px solid var(--line)}
#chatfab{position:fixed;bottom:22px;right:22px;width:60px;height:60px;border-radius:50%;
  background:#22d3ee;color:#062a30;font-size:27px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;z-index:1000;box-shadow:0 8px 24px rgba(0,0,0,.45);transition:transform .15s}
#chatfab:hover{transform:scale(1.07)}
#chatpanel{position:fixed;bottom:92px;right:22px;width:380px;max-width:92vw;height:540px;max-height:78vh;
  display:none;flex-direction:column;background:rgba(9,28,42,.97);backdrop-filter:blur(14px);
  border:1px solid var(--line);border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,.55);z-index:1000;overflow:hidden}
#chatpanel.open{display:flex}
#chatpanel.big{width:580px;height:82vh}
.cphead{display:flex;align-items:center;justify-content:space-between;padding:13px 16px;border-bottom:1px solid var(--line)}
.cphead .t{font-weight:700}
.cphead button{background:none;border:0;color:var(--muted);font-size:1.15rem;cursor:pointer;padding:2px 9px;border-radius:7px;line-height:1}
.cphead button:hover{color:var(--txt);background:var(--glass)}
.chatbody{display:flex;flex-direction:column;flex:1;min-height:0;padding:14px 16px}
.chatlog{display:flex;flex-direction:column;gap:10px;flex:1;overflow-y:auto;margin-bottom:12px}
.cmsg{padding:11px 14px;border-radius:13px;max-width:92%;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;font-size:.9rem}
.cmsg.me{align-self:flex-end;background:#22d3ee;color:#062a30;font-weight:600}
.cmsg.bot{align-self:flex-start;background:var(--glass);border:1px solid var(--line)}
.cmsg.bot.think{color:var(--muted);font-style:italic}
.chatform{display:flex;gap:8px}
.chatform input{flex:1;padding:12px 14px;border-radius:11px;border:1px solid var(--line);background:var(--glass);color:var(--txt);font-size:.92rem;outline:none}
.chatform button{padding:12px 18px;border:0;border-radius:11px;background:#22d3ee;color:#062a30;font-weight:700;cursor:pointer}
.chatform button:disabled{opacity:.5;cursor:default}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chip-q{font-size:.74rem;color:var(--muted);background:var(--glass);border:1px solid var(--line);padding:5px 10px;border-radius:999px;cursor:pointer}
.chip-q:hover{color:var(--txt);border-color:var(--glass2)}
@media(max-width:820px){.vs,.cols,.imp-cols{grid-template-columns:1fr}}
</style></head><body><div class="wrap">

<div class="hero">
  <div>
    <h1>📊 YouTube vs Google Play</h1>
    <p>Comparing customer sentiment for Argos across both platforms</p>
  </div>
  <div class="chip"><span class="dot"></span> Updated %%UPDATED%% &middot; refreshes hourly</div>
</div>

<div class="verdict" style="color:%%VCOLOR%%">%%VERDICT%%</div>

<div class="grid vs">
  <div class="card-glass platform ytb">
    <div class="phead"><span class="pname yt">▶ YouTube</span>
      <span class="pcount">%%YT_TOT%% comments</span></div>
    <div class="psat" style="color:%%YT_SATCOLOR%%">%%YT_SAT%%%<small>positive</small></div>
    <div class="segbar">
      <i style="width:%%YT_PP%%%;background:var(--pos)"></i>
      <i style="width:%%YT_PN%%%;background:var(--neu)"></i>
      <i style="width:%%YT_PG%%%;background:var(--neg)"></i>
    </div>
    <div class="legend">
      <span><i class="sw" style="background:var(--pos)"></i>Positive <b>%%YT_POS%%</b></span>
      <span><i class="sw" style="background:var(--neu)"></i>Neutral <b>%%YT_NEU%%</b></span>
      <span><i class="sw" style="background:var(--neg)"></i>Negative <b>%%YT_NEG%%</b></span>
    </div>
  </div>
  <div class="card-glass platform gpb">
    <div class="phead"><span class="pname gp">▷ Google Play</span>
      <span class="pcount">%%GP_TOT%% reviews</span></div>
    <div class="psat" style="color:%%GP_SATCOLOR%%">%%GP_SAT%%%<small>positive</small></div>
    <div class="segbar">
      <i style="width:%%GP_PP%%%;background:var(--pos)"></i>
      <i style="width:%%GP_PN%%%;background:var(--neu)"></i>
      <i style="width:%%GP_PG%%%;background:var(--neg)"></i>
    </div>
    <div class="legend">
      <span><i class="sw" style="background:var(--pos)"></i>Positive <b>%%GP_POS%%</b></span>
      <span><i class="sw" style="background:var(--neu)"></i>Neutral <b>%%GP_NEU%%</b></span>
      <span><i class="sw" style="background:var(--neg)"></i>Negative <b>%%GP_NEG%%</b></span>
    </div>
  </div>
</div>

<div class="card-glass termwrap">
  <h3>Side-by-side sentiment — % of each platform</h3>
  <canvas id="cmp" height="110"></canvas>
</div>

<div class="card-glass improve">
  <h3>🔧 What needs improving — from negative comments</h3>
  <div class="note">Recurring themes detected in the negative comments on each platform, most-mentioned first.</div>
  <div class="imp-cols">
    <div class="imp-col"><h4><span class="src yt">YouTube</span> top complaints</h4>%%YT_ISSUES%%</div>
    <div class="imp-col"><h4><span class="src gp">Google Play</span> top complaints</h4>%%GP_ISSUES%%</div>
  </div>
</div>

<div class="grid cols">
  <div class="collist">
    <h2>💚 Most positive (both platforms)</h2>
    %%POS_CARDS%%
  </div>
  <div class="collist">
    <h2>❤️ Most negative (both platforms)</h2>
    %%NEG_CARDS%%
  </div>
</div>

<div class="foot">Generated by bot.py &middot; VADER sentiment &middot; YouTube (keyless) + Google Play (keyless) &middot; data in sentiment.db</div>
</div>

<div id="chatfab" title="Ask the comments">💬</div>
<div id="chatpanel">
  <div class="cphead"><span class="t">💬 Ask the comments</span>
    <span><button id="chatbig" title="Expand">⤢</button><button id="chatclose" title="Close">&times;</button></span></div>
  <div class="chatbody">
    <div class="chatlog" id="chatlog"></div>
    <form class="chatform" id="chatform">
      <input id="chatq" autocomplete="off" placeholder="Ask about the comments…">
      <button id="chatb" type="submit">Ask</button>
    </form>
    <div class="chips">
      <span class="chip-q">App problems?</span>
      <span class="chip-q">Delivery vs service?</span>
      <span class="chip-q">What do people praise?</span>
    </div>
  </div>
</div>

<script>
const GR='#9aa0c4';
Chart.defaults.color=GR;Chart.defaults.font.family="Inter";
new Chart(document.getElementById('cmp'),{type:'bar',
data:{labels:['Positive','Neutral','Negative'],datasets:[
{label:'YouTube',data:%%CMP_YT%%,backgroundColor:'#f87171',borderRadius:6},
{label:'Google Play',data:%%CMP_GP%%,backgroundColor:'#34d399',borderRadius:6}]},
options:{responsive:true,
plugins:{legend:{position:'bottom',labels:{usePointStyle:true,padding:18}},
tooltip:{callbacks:{label:(c)=>c.dataset.label+': '+c.parsed.y+'%'}}},
scales:{x:{grid:{display:false},ticks:{color:GR}},
y:{beginAtZero:true,grid:{color:'rgba(255,255,255,.06)'},
ticks:{color:GR,callback:(v)=>v+'%'}}}}});

// ---- in-page chatbox (searches the comments here, asks the Worker brain) ----
const COMMENTS = %%COMMENTS_JSON%%;
const WORKER = "%%WORKER_URL%%";
const CSTOP = new Set("the a an and or but is are was were be to of in on for with about what why how do does did people say saying think argos they it this that i you their there have has".split(" "));
function cretrieve(q){
  const terms=[...new Set((q.toLowerCase().match(/[a-z']+/g)||[]))].filter(w=>!CSTOP.has(w)&&w.length>2);
  return COMMENTS.map(c=>{const tl=c.text.toLowerCase();
      return {c,h:terms.reduce((a,t)=>a+(tl.includes(t)?1:0),0)};})
    .filter(x=>x.h>0).sort((a,b)=>b.h-a.h).slice(0,40).map(x=>x.c);
}
const clog=document.getElementById('chatlog'),cform=document.getElementById('chatform'),
      cq=document.getElementById('chatq'),cb=document.getElementById('chatb');
function cadd(t,cls){const d=document.createElement('div');d.className='cmsg '+cls;
  d.textContent=t;clog.appendChild(d);clog.scrollTop=clog.scrollHeight;return d;}
function cbuildPrompt(q,comments){
  var block=comments.map(function(c,i){return '['+(i+1)+'] ('+c.source+', '+c.sentiment+') '+c.text;}).join('\n');
  return 'Real Argos customer comments from YouTube and Google Play:\n\n'+block+
    '\n\nQuestion: '+q+'\n\nAnswer using ONLY the comments above. Be concise. Note '+
    'roughly how many comments raise each point and whether they are YouTube or '+
    'Google Play. If there is not enough information, say so.';
}
async function cask(q){
  q=(q||'').trim(); if(!q) return;
  cadd(q,'me'); cq.value=''; cb.disabled=true;
  const thinking=cadd('Thinking…','bot think');
  try{
    const comments=cretrieve(q);
    if(!comments.length){thinking.remove();cadd('No comments matched that — try different words.','bot');}
    else if(WORKER.indexOf('PASTE')<0){
      const r=await fetch(WORKER,{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({question:q,comments})});
      const data=await r.json(); thinking.remove(); cadd(data.answer||'(no answer)','bot');
    } else {
      if(!window.askLocal){thinking.remove();cadd('AI is still loading — give it a few seconds and ask again.','bot');}
      else{const ans=await window.askLocal(cbuildPrompt(q,comments),function(msg){thinking.textContent=msg;});
        thinking.remove(); cadd(ans,'bot');}
    }
  }catch(e){thinking.remove();cadd('Chatbox error: '+((e&&e.message)?e.message:e),'bot');}
  cb.disabled=false; cq.focus();
}
cform.addEventListener('submit',e=>{e.preventDefault();cask(cq.value);});
document.querySelectorAll('.chip-q').forEach(ch=>ch.addEventListener('click',()=>cask(ch.textContent)));
// floating widget open / close / expand
const fab=document.getElementById('chatfab'),panel=document.getElementById('chatpanel');
fab.addEventListener('click',()=>{panel.classList.toggle('open');
  if(panel.classList.contains('open'))cq.focus();});
document.getElementById('chatclose').addEventListener('click',()=>panel.classList.remove('open'));
document.getElementById('chatbig').addEventListener('click',()=>panel.classList.toggle('big'));
</script>
<script type="module">
// Runs a small AI model INSIDE the browser — no key, no server. First question
// downloads the model (~1 min); after that it's cached and fast.
import * as webllm from "https://esm.run/@mlc-ai/web-llm";
const LMODEL="Qwen2.5-0.5B-Instruct-q4f16_1-MLC";
const LSYS="You are a customer-insight analyst. Answer strictly from the comments provided; never invent feedback, numbers, or quotes. Be concise and useful.";
let engine=null, loading=null;
function makeWorker(){
  const code='import { WebWorkerMLCEngineHandler } from "https://esm.run/@mlc-ai/web-llm";'
    +'const h=new WebWorkerMLCEngineHandler();self.onmessage=(m)=>h.onmessage(m);';
  return new Worker(URL.createObjectURL(new Blob([code],{type:"text/javascript"})),{type:"module"});
}
window.askLocal=async function(prompt,onProgress){
  if(!navigator.gpu) throw new Error("This browser can't run the in-page AI (no WebGPU). Use the latest Chrome or Edge on a computer.");
  try{
    if(!engine){
      if(onProgress) onProgress("Loading AI model (first time only)…");
      if(!loading) loading=webllm.CreateWebWorkerMLCEngine(makeWorker(),LMODEL,{initProgressCallback:function(p){
        if(onProgress) onProgress("Loading AI model… "+Math.round((p.progress||0)*100)+"%");}});
      engine=await loading;
    }
    if(onProgress) onProgress("Thinking…");
    const reply=await engine.chat.completions.create({
      messages:[{role:"system",content:LSYS},{role:"user",content:prompt}],
      temperature:0.3, max_tokens:800});
    return (reply.choices[0].message.content||"").trim();
  }catch(e){ engine=null; loading=null; throw e; }   // reset so a retry can re-load
};
</script></body></html>"""

    # Embed the comments for the chatbox to search (escape </ so it can't break the <script>).
    chat_json = json.dumps(chat_rows, ensure_ascii=False).replace("</", "<\\/")

    repl = {
        "%%UPDATED%%": f"{datetime.now():%Y-%m-%d %H:%M}",
        "%%VERDICT%%": verdict,
        "%%VCOLOR%%": vcolor,
        "%%YT_TOT%%": str(yt["tot"]), "%%YT_SAT%%": str(yt["sat"]),
        "%%YT_SATCOLOR%%": satcolor(yt["sat"]),
        "%%YT_PP%%": str(yt["pp"]), "%%YT_PN%%": str(yt["pn"]), "%%YT_PG%%": str(yt["pg"]),
        "%%YT_POS%%": str(yt["pos"]), "%%YT_NEU%%": str(yt["neu"]), "%%YT_NEG%%": str(yt["neg"]),
        "%%GP_TOT%%": str(gp["tot"]), "%%GP_SAT%%": str(gp["sat"]),
        "%%GP_SATCOLOR%%": satcolor(gp["sat"]),
        "%%GP_PP%%": str(gp["pp"]), "%%GP_PN%%": str(gp["pn"]), "%%GP_PG%%": str(gp["pg"]),
        "%%GP_POS%%": str(gp["pos"]), "%%GP_NEU%%": str(gp["neu"]), "%%GP_NEG%%": str(gp["neg"]),
        "%%CMP_YT%%": json.dumps([yt["pp"], yt["pn"], yt["pg"]]),
        "%%CMP_GP%%": json.dumps([gp["pp"], gp["pn"], gp["pg"]]),
        "%%YT_ISSUES%%": issues_html("YouTube"),
        "%%GP_ISSUES%%": issues_html("Google Play"),
        "%%POS_CARDS%%": cards(top_pos, "pos"),
        "%%NEG_CARDS%%": cards(top_neg, "neg"),
        "%%WORKER_URL%%": CHAT_WORKER_URL,
        "%%COMMENTS_JSON%%": chat_json,
    }
    for k, v in repl.items():
        template = template.replace(k, v)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(template)

    total = yt["tot"] + gp["tot"]
    pos = yt["pos"] + gp["pos"]
    neg = yt["neg"] + gp["neg"]
    neu = yt["neu"] + gp["neu"]
    satisfaction = round(pos / total * 100, 1) if total else 0.0
    return total, pos, neg, neu, satisfaction


# ---------------------------------------------------------------- main
def main():
    print("\n" + "=" * 60)
    print("  🤖 CUSTOMER SENTIMENT BOT  (YouTube + Google Play)")
    print("=" * 60)

    cfg = load_config()
    setup_db()

    grand_total = 0
    for term in cfg["search_terms"]:
        print(f"\n🔎 YouTube search: '{term}'")
        videos = find_videos(term, cfg["videos_per_term"])
        print(f"   found {len(videos)} videos")
        for vid in videos:
            got = collect_comments(vid, term, cfg["comments_per_video"])
            grand_total += got
            print(f"   • {vid}: +{got} new comments")

    for app in cfg.get("google_play_apps", []):
        label = app.get("label", app["package"])
        print(f"\n📱 Google Play reviews: {label}")
        got = collect_play_reviews(app["package"], label,
                                   cfg.get("reviews_per_app", 100))
        grand_total += got
        print(f"   • {app['package']}: +{got} new reviews")

    total, pos, neg, neu, satisfaction = build_report()

    print("\n" + "=" * 60)
    print(f"  ✅ DONE — {grand_total} new comments this run")
    print(f"     Database now holds {total} comments total")
    print(f"     😊 {pos} positive | 😞 {neg} negative | 😐 {neu} neutral")
    print(f"     Customer satisfaction: {satisfaction}%")
    print("=" * 60)
    # When run by Task Scheduler we pass --scheduled, so we DON'T pop open
    # a browser every hour. Running it by hand opens the report for you.
    if "--scheduled" not in sys.argv:
        print("  📊 Opening report.html in your browser...")
        try:
            webbrowser.open(REPORT)
        except Exception:
            print("     (open report.html manually if it didn't pop up)")
    else:
        print(f"  📊 Report updated: {REPORT}")
    print()


if __name__ == "__main__":
    main()
