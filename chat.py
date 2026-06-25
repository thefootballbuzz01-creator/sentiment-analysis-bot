#!/usr/bin/env python3
"""
Local chatbox website — ask questions about the Argos comments in a browser.

Run:   python chat.py
Then a chat page opens at http://localhost:8000 . Type a question, get an
AI answer grounded in your real comments. Free (Google Gemini), and your key
stays on your computer. Press Ctrl+C in the terminal to stop it.
"""

import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from ask import retrieve, _prompt, SYSTEM, THEMES   # reuse the same retrieval

GEM_KEY = os.getenv("GEMINI_API_KEY", "")
GEM_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def free_text(question, comments):
    """Offline summary used if there's no key / Gemini is unavailable."""
    pos = sum(1 for c in comments if c[1] == "Positive")
    neg = sum(1 for c in comments if c[1] == "Negative")
    yt = sum(1 for c in comments if c[0] == "YouTube")
    gp = sum(1 for c in comments if c[0] == "Google Play")
    counts = {}
    for _, _, _, t in comments:
        tl = t.lower()
        for theme, kws in THEMES.items():
            if any(k in tl for k in kws):
                counts[theme] = counts.get(theme, 0) + 1
    topics = ", ".join(f"{t} ({n})" for t, n in
                       sorted(counts.items(), key=lambda x: -x[1])[:4])
    quotes = "\n".join(f"• [{('YT' if s=='YouTube' else 'GP')}/{sent}] {t[:110]}"
                       for s, sent, sc, t in comments[:5])
    return (f"Found {len(comments)} relevant comments ({yt} YouTube, {gp} Google "
            f"Play) — {pos} positive, {neg} negative.\n\nTop topics: {topics}\n\n"
            f"Most relevant comments:\n{quotes}")


def gemini_text(question, comments):
    if not GEM_KEY:
        return None
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEM_MODEL}:generateContent?key={GEM_KEY}")
    body = {
        "contents": [{"parts": [{"text": SYSTEM + "\n\n" + _prompt(question, comments)}]}],
        "generationConfig": {"maxOutputTokens": 2048,
                             "thinkingConfig": {"thinkingBudget": 0}},
    }
    try:
        r = requests.post(url, json=body, timeout=40)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def answer(question):
    question = (question or "").strip()
    if not question:
        return "Ask me something about the Argos comments."
    comments = retrieve(question)
    if not comments:
        return "No comments matched that question — try different words."
    txt = gemini_text(question, comments)
    if txt:
        return txt.strip() + f"\n\n— grounded in {len(comments)} real comments"
    return free_text(question, comments)


PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ask the Argos comments</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;color:#e6f6f7;
  background:linear-gradient(135deg,#0b1f33,#08363f,#0a2a3a);min-height:100vh;
  display:flex;flex-direction:column;align-items:center;padding:24px}
.wrap{width:100%;max-width:760px;display:flex;flex-direction:column;height:90vh}
h1{font-size:1.5rem;margin-bottom:4px}
p.sub{color:#8fb0bf;font-size:.9rem;margin-bottom:16px}
#log{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:12px;padding:6px}
.msg{padding:13px 16px;border-radius:14px;max-width:90%;line-height:1.5;
  white-space:pre-wrap;word-wrap:break-word}
.me{align-self:flex-end;background:#22d3ee;color:#062a30;font-weight:600}
.bot{align-self:flex-start;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.12)}
.bot.think{color:#8fb0bf;font-style:italic}
form{display:flex;gap:10px;margin-top:14px}
input{flex:1;padding:14px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.15);
  background:rgba(255,255,255,.06);color:#fff;font-size:1rem;outline:none}
button{padding:14px 22px;border:0;border-radius:12px;background:#22d3ee;color:#062a30;
  font-weight:700;font-size:1rem;cursor:pointer}
button:disabled{opacity:.5;cursor:default}
.hint{color:#8fb0bf;font-size:.82rem;margin-top:8px;text-align:center}
</style></head><body><div class="wrap">
<h1>💬 Ask the Argos comments</h1>
<p class="sub">Live answers from real YouTube &amp; Google Play feedback</p>
<div id="log"></div>
<form id="f">
  <input id="q" autocomplete="off" placeholder="e.g. what are the main delivery complaints?">
  <button id="b" type="submit">Ask</button>
</form>
<div class="hint">Try: "what do people dislike about the app?" · "is delivery or service the bigger problem?"</div>
</div>
<script>
const log=document.getElementById('log'),f=document.getElementById('f'),
      q=document.getElementById('q'),b=document.getElementById('b');
function add(text,cls){const d=document.createElement('div');d.className='msg '+cls;
  d.textContent=text;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
f.addEventListener('submit',async(e)=>{e.preventDefault();
  const question=q.value.trim();if(!question)return;
  add(question,'me');q.value='';b.disabled=true;
  const thinking=add('Thinking…','bot think');
  try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question})});
    const data=await r.json();thinking.remove();add(data.answer,'bot');
  }catch(err){thinking.remove();add('Something went wrong: '+err,'bot');}
  b.disabled=false;q.focus();
});
q.focus();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):        # let the dashboard page call this server
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self._send(PAGE.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            question = json.loads(raw).get("question", "")
        except Exception:
            question = ""
        body = json.dumps({"answer": answer(question)}).encode("utf-8")
        self._send(body, "application/json")


def main():
    port = 8000
    print("\n" + "=" * 60)
    print("  💬 ARGOS CHATBOX  —  open http://localhost:8000")
    print("=" * 60)
    print("  Mode:", "Gemini AI" if GEM_KEY else "free offline summary")
    print("  Press Ctrl+C here to stop.\n")
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass
    try:
        ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")


if __name__ == "__main__":
    main()
