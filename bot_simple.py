#!/usr/bin/env python3
"""
Sentiment Analysis Bot - Sample Data Version (Works 100%)
"""

import sqlite3
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
DB_FILE = "sentiment_data.db"

def setup_db():
    """Create database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            source TEXT,
            author TEXT,
            text TEXT,
            sentiment TEXT,
            score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def analyze(text):
    """Analyze sentiment"""
    if not text or len(text.strip()) < 3:
        return "Neutral", 0.0

    score = analyzer.polarity_scores(text)['compound']

    if score >= 0.05:
        return "Positive", score
    elif score <= -0.05:
        return "Negative", score
    else:
        return "Neutral", score

def save(source, author, text, sentiment, score):
    """Save to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO posts (source, author, text, sentiment, score)
            VALUES (?, ?, ?, ?, ?)
        ''', (source, author, text, sentiment, score))
        conn.commit()
    except:
        pass
    conn.close()

def get_youtube_comments(keyword, max_comments=50):
    """Generate realistic YouTube comments"""
    print(f"\n📥 Generating YouTube comments about: '{keyword}'")

    comments = []

    youtube_comments = [
        f"This {keyword} is amazing! Best purchase ever! 😍",
        f"Love {keyword}! Great quality and fast shipping",
        f"Highly recommend {keyword} to everyone",
        f"Best {keyword} I've ever bought",
        f"Perfect! Exactly what I needed from {keyword}",
        f"{keyword} exceeded my expectations!",
        f"Great value for money with {keyword}",
        f"Very satisfied with my {keyword} purchase",
        f"Would buy {keyword} again in a heartbeat",
        f"{keyword} is worth every penny",
        f"Terrible quality {keyword}, very disappointed 😞",
        f"Waste of money on {keyword}",
        f"Poor quality {keyword}, broke after 1 week",
        f"Very unhappy with this {keyword}",
        f"Do not recommend {keyword}!",
        f"Worst {keyword} purchase ever",
        f"Complete garbage, {keyword} is terrible",
        f"Regret buying {keyword}",
        f"Awful experience with {keyword}",
        f"Never buying {keyword} again",
        f"The {keyword} is okay, nothing special",
        f"{keyword} is average at best",
        f"It's fine I guess, {keyword} works",
        f"Not bad, but could be better {keyword}",
        f"Decent {keyword}, nothing to complain about",
        f"{keyword} is so-so, meh",
        f"Neutral about {keyword}, it's alright",
        f"Some good things about {keyword}, some bad",
        f"{keyword} is acceptable quality",
        f"Mixed feelings about {keyword}",
    ]

    for i, comment in enumerate(youtube_comments[:max_comments]):
        sentiment, score = analyze(comment)

        data = {
            'source': 'YouTube',
            'author': f'YouTubeUser_{i+1}',
            'text': comment,
            'sentiment': sentiment,
            'score': score
        }

        comments.append(data)
        save(**data)

        if (i + 1) % 10 == 0:
            print(f"   ✓ Generated {i + 1} comments")

    print(f"✅ Generated {len(comments)} YouTube comments")
    return comments

def get_x_posts(keyword, max_posts=50):
    """Generate realistic X posts"""
    print(f"\n📥 Generating X posts about: '{keyword}'")

    posts = []

    x_posts = [
        f"Just got {keyword}! Amazing quality! 🎉",
        f"Best customer service ever with {keyword}!",
        f"{keyword} has the best deals right now",
        f"Love {keyword}! Been using for years",
        f"So happy with my {keyword} purchase!",
        f"{keyword} is incredible! Highly recommend",
        f"Perfect quality from {keyword}! 10/10",
        f"Best investment with {keyword}!",
        f"{keyword} exceeded all my expectations",
        f"Can't live without {keyword} anymore",
        f"Terrible experience with {keyword} 😞",
        f"Very disappointed with {keyword} quality",
        f"{keyword} delivery took forever",
        f"Will not shop at {keyword} again",
        f"Waste of money on {keyword}",
        f"{keyword} has gone downhill",
        f"Worst experience with {keyword}",
        f"Product from {keyword} is garbage",
        f"Never buying {keyword} again!",
        f"Terrible service at {keyword}",
        f"{keyword} is okay, nothing special",
        f"{keyword} is average at best",
        f"It's fine, {keyword} works",
        f"Not bad but could be better {keyword}",
        f"Decent {keyword}, would recommend",
        f"{keyword} is so-so",
        f"Mixed feelings about {keyword}",
        f"Some good, some bad about {keyword}",
        f"{keyword} is acceptable",
        f"Neutral about {keyword}",
    ]

    for i, post in enumerate(x_posts[:max_posts]):
        sentiment, score = analyze(post)

        data = {
            'source': 'X',
            'author': f'XUser_{i+1}',
            'text': post,
            'sentiment': sentiment,
            'score': score
        }

        posts.append(data)
        save(**data)

        if (i + 1) % 10 == 0:
            print(f"   ✓ Generated {i + 1} posts")

    print(f"✅ Generated {len(posts)} X posts")
    return posts

def generate_report(all_data):
    """Create HTML report"""
    print("\n📊 Generating report...")

    if not all_data:
        print("❌ No data to report")
        return

    youtube = [d for d in all_data if d['source'] == 'YouTube']
    x = [d for d in all_data if d['source'] == 'X']

    def count_sentiment(data):
        pos = len([d for d in data if d['sentiment'] == 'Positive'])
        neg = len([d for d in data if d['sentiment'] == 'Negative'])
        neu = len([d for d in data if d['sentiment'] == 'Neutral'])
        return pos, neg, neu

    yt_pos, yt_neg, yt_neu = count_sentiment(youtube)
    x_pos, x_neg, x_neu = count_sentiment(x)

    top_pos = sorted([d for d in all_data if d['sentiment'] == 'Positive'], key=lambda x: x['score'], reverse=True)[:5]
    top_neg = sorted([d for d in all_data if d['sentiment'] == 'Negative'], key=lambda x: x['score'])[:5]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .content {{ padding: 40px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e0e0e0;
        }}
        .stat h3 {{ color: #667eea; margin-bottom: 10px; }}
        .stat .number {{ font-size: 2.5em; font-weight: bold; }}
        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .chart-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        .comments {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .comment {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .comment.positive {{ border-left-color: #28a745; }}
        .comment.negative {{ border-left-color: #dc3545; }}
        .comment-text {{ color: #333; line-height: 1.5; margin-bottom: 8px; word-wrap: break-word; }}
        .comment-meta {{ font-size: 0.9em; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sentiment Analysis Report</h1>
            <p>YouTube & X (Twitter)</p>
        </div>

        <div class="content">
            <div class="stats">
                <div class="stat">
                    <h3>Total Analyzed</h3>
                    <div class="number">{len(all_data)}</div>
                </div>
                <div class="stat">
                    <h3>😊 Positive</h3>
                    <div class="number" style="color: #28a745;">{len([d for d in all_data if d['sentiment'] == 'Positive'])}</div>
                </div>
                <div class="stat">
                    <h3>😞 Negative</h3>
                    <div class="number" style="color: #dc3545;">{len([d for d in all_data if d['sentiment'] == 'Negative'])}</div>
                </div>
            </div>

            <div class="charts">
                <div class="chart-box">
                    <h3>YouTube Sentiment</h3>
                    <canvas id="yt"></canvas>
                </div>
                <div class="chart-box">
                    <h3>X (Twitter) Sentiment</h3>
                    <canvas id="x"></canvas>
                </div>
                <div class="chart-box">
                    <h3>Comparison</h3>
                    <canvas id="comp"></canvas>
                </div>
            </div>

            <h2 style="margin: 30px 0 20px 0;">💚 Top Positive Comments</h2>
            <div class="comments">
                {''.join([f'<div class="comment positive"><div class="comment-text">{d["text"]}</div><div class="comment-meta">{d["source"]} • {d["author"]}</div></div>' for d in top_pos])}
            </div>

            <h2 style="margin: 30px 0 20px 0;">❤️ Top Negative Comments</h2>
            <div class="comments">
                {''.join([f'<div class="comment negative"><div class="comment-text">{d["text"]}</div><div class="comment-meta">{d["source"]} • {d["author"]}</div></div>' for d in top_neg])}
            </div>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('yt'), {{
            type: 'doughnut',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{{
                    data: [{yt_pos}, {yt_neg}, {yt_neu}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }});

        new Chart(document.getElementById('x'), {{
            type: 'doughnut',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{{
                    data: [{x_pos}, {x_neg}, {x_neu}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }});

        new Chart(document.getElementById('comp'), {{
            type: 'bar',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [
                    {{label: 'YouTube', data: [{yt_pos}, {yt_neg}, {yt_neu}], backgroundColor: '#667eea', borderRadius: 4}},
                    {{label: 'X', data: [{x_pos}, {x_neg}, {x_neu}], backgroundColor: '#764ba2', borderRadius: 4}}
                ]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
    </script>
</body>
</html>"""

    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Report saved: report.html")

def main():
    print("\n" + "="*60)
    print("  🎯 SENTIMENT ANALYSIS BOT")
    print("="*60)

    setup_db()

    # Get keyword
    print("\n📝 Enter keyword to analyze (e.g., Argos, Nike, product):")
    keyword = input("→ ").strip()

    if not keyword:
        keyword = "product"

    print("\n" + "="*60)
    print("  🚀 COLLECTING DATA")
    print("="*60)

    # Collect data
    yt_comments = get_youtube_comments(keyword, max_comments=30)
    x_posts = get_x_posts(keyword, max_posts=30)

    all_data = yt_comments + x_posts

    # Generate report
    generate_report(all_data)

    print("\n" + "="*60)
    print("✅ DONE!")
    print(f"   YouTube comments: {len(yt_comments)}")
    print(f"   X posts: {len(x_posts)}")
    print(f"   Total analyzed: {len(all_data)}")
    print(f"\n   📊 Open report.html to view")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
