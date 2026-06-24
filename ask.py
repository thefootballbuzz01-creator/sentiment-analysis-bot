#!/usr/bin/env python3
"""
Ask-your-data — ask questions about the collected comments in plain English.

Works in TWO modes, automatically:
  • FREE mode (default, no key, no money): finds the comments most relevant to
    your question and summarises them — counts, YouTube vs Google Play split,
    common themes, and the most relevant real quotes. Runs offline.
  • AI mode (optional): if an Anthropic API key is present in .env, it also asks
    Claude to write a fluent answer grounded in those same real comments.

Run:   python ask.py "what do people complain about with delivery?"
   or:  python ask.py        (then type questions interactively)
"""

import os
import re
import sqlite3
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "sentiment.db")

# Used only if you add an Anthropic key. Haiku = cheapest; or ASK_MODEL=claude-opus-4-8.
MODEL = os.getenv("ASK_MODEL", "claude-haiku-4-5")
TOP_K = 40

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "to", "of", "in", "on", "for", "with", "about", "what", "why", "how",
    "do", "does", "did", "people", "say", "saying", "think", "argos", "they",
    "it", "this", "that", "i", "you", "their", "there", "have", "has",
}

# Same themes the dashboard uses — for grouping complaints/praise by topic.
THEMES = {
    "Delivery & dispatch": ["deliver", "dispatch", "courier", "arrive", "late",
                            "waiting", "shipping", "never arrived"],
    "App & website": ["app", "login", "log in", "crash", "update", "loading",
                      "website", "error", "bug", "glitch", "freeze", "slow"],
    "Stock & availability": ["stock", "unavailable", "availability", "sold out"],
    "Customer service": ["service", "staff", "support", "rude", "unhelpful",
                         "response", "contact", "phone", "call"],
    "Refunds & payment": ["refund", "money", "payment", "charged", "voucher",
                          "expensive", "price", "fraud"],
    "Orders & collection": ["order", "cancel", "collection", "collect",
                            "missing", "wrong item", "reserve"],
    "Product quality": ["quality", "broken", "faulty", "damaged", "cheap"],
}


def retrieve(question, limit=TOP_K):
    """Find the comments most relevant to the question — keyword overlap, no API."""
    terms = {w for w in re.findall(r"[a-z']+", question.lower())
             if w not in STOPWORDS and len(w) > 2}
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT source, sentiment, score, text FROM comments"
    ).fetchall()
    conn.close()

    scored = []
    for source, sentiment, score, text in rows:
        tl = text.lower()
        hits = sum(1 for t in terms if t in tl)
        if hits:
            scored.append((hits, source, sentiment, score, text))
    scored.sort(key=lambda r: -r[0])
    return [r[1:] for r in scored[:limit]]


def free_summary(question, comments):
    """Answer using only retrieval + counting — completely free, no API."""
    pos = sum(1 for c in comments if c[1] == "Positive")
    neg = sum(1 for c in comments if c[1] == "Negative")
    neu = sum(1 for c in comments if c[1] == "Neutral")
    yt = sum(1 for c in comments if c[0] == "YouTube")
    gp = sum(1 for c in comments if c[0] == "Google Play")
    total = len(comments)

    print("\n" + "=" * 70)
    print(f"  Q: {question}")
    print("=" * 70)
    print(f"\n  Found {total} relevant comments  "
          f"({yt} YouTube · {gp} Google Play)")
    print(f"  Sentiment:  😊 {pos} positive   😞 {neg} negative   😐 {neu} neutral")

    # Which themes show up among the matched comments
    theme_counts = {}
    for _, _, _, text in comments:
        tl = text.lower()
        for theme, kws in THEMES.items():
            if any(k in tl for k in kws):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
    if theme_counts:
        ranked = sorted(theme_counts.items(), key=lambda x: -x[1])[:4]
        print("\n  Common topics in these comments:")
        for theme, n in ranked:
            print(f"     • {theme}: {n}")

    print("\n  Most relevant comments:")
    for source, sentiment, score, text in comments[:6]:
        tag = "YT" if source == "YouTube" else "GP"
        print(f"     [{tag}/{sentiment}] {text[:90]}")
    print(f"\n  (free mode — grounded in {total} real comments, no AI service used)\n")


def ai_answer(question, comments):
    """Optional: ask Claude to write a grounded answer (needs an API key)."""
    import anthropic
    block = "\n".join(
        f"[{i}] ({s}, {sent}) {t}"
        for i, (s, sent, sc, t) in enumerate(comments, 1)
    )
    prompt = (
        f"Here are real customer comments about Argos from YouTube and Google "
        f"Play:\n\n{block}\n\nQuestion: {question}\n\nAnswer using ONLY these "
        f"comments. Be concise; note roughly how many raise each point and "
        f"whether they're YouTube or Google Play. If there isn't enough info, "
        f"say so."
    )
    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=MODEL, max_tokens=1024,
            system=("You are a customer-insight analyst. Answer strictly from the "
                    "comments provided; never invent feedback or numbers."),
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"\n  (AI answer unavailable — {type(e).__name__}; showing free "
              f"summary instead)")
        free_summary(question, comments)
        return
    answer = next((b.text for b in resp.content if b.type == "text"), "")
    print("\n" + "=" * 70)
    print(f"  Q: {question}")
    print("=" * 70)
    print(f"\n{answer}\n")
    print(f"  (AI answer · grounded in {len(comments)} real comments · {MODEL})\n")


def ask(question):
    comments = retrieve(question)
    if not comments:
        print("\n  No comments matched that question. Try different words.\n")
        return
    if os.getenv("ANTHROPIC_API_KEY", "").startswith("sk-ant-"):
        ai_answer(question, comments)
    else:
        free_summary(question, comments)


def main():
    if len(sys.argv) > 1:
        ask(" ".join(sys.argv[1:]))
        return
    print("\n💬 Ask anything about the Argos comments (blank line to quit).\n"
          "   e.g. 'what are the main delivery complaints?'\n")
    while True:
        try:
            q = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        ask(q)


if __name__ == "__main__":
    main()
