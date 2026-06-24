#!/usr/bin/env python3
"""
Ask-your-data (RAG) — ask questions about the collected comments in plain English.

How it works:
  1. RETRIEVAL (free, no API): finds the comments most relevant to your question
     by keyword matching against the local sentiment.db database.
  2. GENERATION (Claude API): sends ONLY those real comments to Claude and asks it
     to answer using them — so the answer is grounded in actual feedback, not made up.

Run:   python ask.py "what do people complain about with delivery?"
   or:  python ask.py        (then type questions interactively)

Needs an Anthropic API key in .env  ->  ANTHROPIC_API_KEY=sk-ant-...
"""

import os
import re
import sqlite3
import sys

from dotenv import load_dotenv
import anthropic

load_dotenv()

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "sentiment.db")

# Default model: Haiku — cheapest and fastest. Set ASK_MODEL=claude-opus-4-8 in
# .env for the most capable (and pricier) answers.
MODEL = os.getenv("ASK_MODEL", "claude-haiku-4-5")
TOP_K = 40  # how many of the most relevant comments to feed the model

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "to", "of", "in", "on", "for", "with", "about", "what", "why", "how",
    "do", "does", "did", "people", "say", "saying", "think", "argos", "they",
    "it", "this", "that", "i", "you", "their", "there", "have", "has",
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


def build_prompt(question, comments):
    lines = []
    for i, (source, sentiment, score, text) in enumerate(comments, 1):
        lines.append(f"[{i}] ({source}, {sentiment}) {text}")
    block = "\n".join(lines)
    return (
        f"Here are real customer comments about Argos collected from YouTube and "
        f"Google Play:\n\n{block}\n\n"
        f"Question: {question}\n\n"
        f"Answer using ONLY the comments above. Be concise and specific. Where it "
        f"helps, note roughly how many comments raise a point and whether they came "
        f"from YouTube or Google Play. If the comments don't contain enough "
        f"information to answer, say so plainly."
    )


SYSTEM = (
    "You are a customer-insight analyst. You answer questions strictly from the "
    "customer comments provided in the user's message — never invent feedback, "
    "numbers, or quotes that aren't supported by them. Quote sparingly and keep "
    "answers tight and useful for a presentation."
)


def ask(question):
    comments = retrieve(question)
    if not comments:
        print("\nNo comments matched that question. Try different words, or run "
              "the bot first to collect data.\n")
        return

    try:
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM,
            messages=[{"role": "user", "content": build_prompt(question, comments)}],
        )
    except anthropic.AuthenticationError:
        print("\n❌ Your Anthropic API key is missing or invalid.\n"
              "   Put a valid key in .env as:  ANTHROPIC_API_KEY=sk-ant-...\n"
              "   Get one at: https://console.anthropic.com/settings/keys\n")
        return
    except Exception as e:
        print(f"\n❌ Could not reach the Claude API: {e}\n")
        return

    answer = next((b.text for b in resp.content if b.type == "text"), "")
    print("\n" + "=" * 70)
    print(f"  Q: {question}")
    print("=" * 70)
    print(f"\n{answer}\n")
    print(f"(answer grounded in {len(comments)} real comments · model: {MODEL})\n")


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  No ANTHROPIC_API_KEY found. Add it to .env first — see README.\n")
        return

    if len(sys.argv) > 1:                       # one-shot:  python ask.py "question"
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
