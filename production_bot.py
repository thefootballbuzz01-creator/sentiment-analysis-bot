#!/usr/bin/env python3
"""
Production Sentiment Analysis Bot
Real YouTube API + Real X API with hourly automation
"""

import os
import json
import sqlite3
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# YouTube API
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    from google.auth.httplib2 import HttpHttp
    import googleapiclient.discovery
    YOUTUBE_AVAILABLE = True
except:
    YOUTUBE_AVAILABLE = False

# X API (Tweepy)
try:
    import tweepy
    X_AVAILABLE = True
except:
    X_AVAILABLE = False

analyzer = SentimentIntensityAnalyzer()
DB_FILE = "production_sentiment.db"

# Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN', '')

# Search queries
YOUTUBE_SEARCHES = [
    "product reviews",
    "customer service",
    "unboxing",
    "product quality",
    "shopping experience",
]

X_SEARCHES = [
    "product review",
    "customer service",
    "great product",
    "amazing deal",
    "customer satisfaction",
]

def setup_db():
    """Create database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            author TEXT,
            text TEXT,
            sentiment TEXT,
            score REAL,
            source_url TEXT,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            youtube_count INTEGER,
            x_count INTEGER,
            total_count INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def analyze_sentiment(text):
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

def save_post(source, author, text, sentiment, score, source_url):
    """Save to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO posts (source, author, text, sentiment, score, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source, author, text, sentiment, score, source_url))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def collect_youtube_comments(max_comments=50):
    """Collect REAL YouTube comments using API"""
    print("\n🎬 REAL YouTube Collection")
    print("="*50)

    if not YOUTUBE_API_KEY:
        print("⚠️  YouTube API key not set")
        return 0

    if not YOUTUBE_AVAILABLE:
        print("⚠️  YouTube API library not available")
        return 0

    total = 0

    try:
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Search for videos
        for search_query in YOUTUBE_SEARCHES:
            print(f"\n  Searching: '{search_query}'")

            try:
                search_response = youtube.search().list(
                    q=search_query,
                    part='id',
                    type='video',
                    maxResults=5,
                    order='relevance'
                ).execute()

                for item in search_response.get('items', [])[:2]:
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"

                    print(f"    📹 Video: {video_url}")

                    try:
                        # Get comments for this video
                        comments_response = youtube.commentThreads().list(
                            videoId=video_id,
                            part='snippet',
                            maxResults=20,
                            textFormat='plainText'
                        ).execute()

                        for thread in comments_response.get('items', []):
                            comment = thread['snippet']['topLevelComment']['snippet']
                            text = comment['textDisplay']
                            author = comment['authorDisplayName']

                            if len(text.strip()) < 3:
                                continue

                            sentiment, score = analyze_sentiment(text)

                            if save_post('YouTube', author, text, sentiment, score, video_url):
                                total += 1
                                print(f"      ✅ [{sentiment}] {text[:50]}...")

                    except Exception as e:
                        print(f"    ⚠️  Error: {e}")

            except Exception as e:
                print(f"  ⚠️  Search error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print(f"\n✅ YouTube: {total} comments collected")
    return total

def collect_x_posts(max_posts=50):
    """Collect REAL X posts using API"""
    print("\n🐦 REAL X Collection")
    print("="*50)

    if not X_BEARER_TOKEN:
        print("⚠️  X Bearer token not set")
        return 0

    if not X_AVAILABLE:
        print("⚠️  Tweepy not available")
        return 0

    total = 0

    try:
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN)

        for search_query in X_SEARCHES:
            print(f"\n  Searching: '{search_query}'")

            try:
                tweets = client.search_recent_tweets(
                    query=search_query,
                    max_results=min(100, max_posts),
                    tweet_fields=['public_metrics', 'created_at', 'author_id'],
                    expansions=['author_id'],
                    user_fields=['username']
                )

                if not tweets.data:
                    print(f"    ⚠️  No tweets found")
                    continue

                users_dict = {}
                if tweets.includes and 'users' in tweets.includes:
                    for user in tweets.includes['users']:
                        users_dict[user.id] = user.username

                for tweet in tweets.data:
                    text = tweet.text
                    author = users_dict.get(tweet.author_id, 'Unknown')
                    tweet_url = f"https://x.com/i/web/status/{tweet.id}"

                    if len(text.strip()) < 3:
                        continue

                    sentiment, score = analyze_sentiment(text)

                    if save_post('X', author, text, sentiment, score, tweet_url):
                        total += 1
                        print(f"      ✅ [{sentiment}] {text[:50]}...")

            except Exception as e:
                print(f"  ⚠️  Error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print(f"\n✅ X: {total} posts collected")
    return total

def analyze_results():
    """Analyze and display results"""
    print("\n" + "="*70)
    print("  📊 SENTIMENT ANALYSIS RESULTS")
    print("="*70)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(*),
               SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END),
               AVG(score)
        FROM posts
    ''')

    result = cursor.fetchone()
    total, pos, neg, neu, avg = result if result[0] else (0, 0, 0, 0, 0)

    print(f"\n  📈 OVERALL:")
    print(f"     Total Posts: {total}")
    print(f"     Positive: {pos or 0} ({round((pos or 0)/total*100 if total else 0, 1)}%)")
    print(f"     Negative: {neg or 0} ({round((neg or 0)/total*100 if total else 0, 1)}%)")
    print(f"     Neutral: {neu or 0} ({round((neu or 0)/total*100 if total else 0, 1)}%)")

    satisfaction = round((pos or 0) / total * 100 if total > 0 else 0, 1)
    print(f"\n  😊 SATISFACTION: {satisfaction}%")
    print(f"     Status: {'✅ EXCELLENT' if satisfaction >= 70 else '🟡 GOOD' if satisfaction >= 50 else '🔴 CRITICAL'}")

    # By source
    cursor.execute('''
        SELECT source, COUNT(*),
               SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END)
        FROM posts
        GROUP BY source
    ''')

    print(f"\n  📊 BY SOURCE:")
    for source, count, pos_s, neg_s in cursor.fetchall():
        print(f"     {source}: {count} posts ({round(pos_s/count*100 if count else 0, 0):.0f}% positive)")

    conn.close()

def generate_dashboard():
    """Generate HTML dashboard"""
    print(f"\n  📊 Generating live dashboard...")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(*),
               SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END),
               AVG(score)
        FROM posts
    ''')

    total, pos, neg, neu, avg_score = cursor.fetchone()
    total = total or 0
    pos = pos or 0
    neg = neg or 0
    neu = neu or 0
    satisfaction = round(pos / total * 100 if total > 0 else 0, 1)

    cursor.execute('''
        SELECT source,
               SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END)
        FROM posts
        GROUP BY source
    ''')

    source_stats = cursor.fetchall()
    yt_stats = next((s for s in source_stats if s[0] == 'YouTube'), None) or ('YouTube', 0, 0, 0)
    x_stats = next((s for s in source_stats if s[0] == 'X'), None) or ('X', 0, 0, 0)

    cursor.execute('SELECT author, text FROM posts WHERE sentiment="Positive" ORDER BY score DESC LIMIT 5')
    top_pos = cursor.fetchall()

    cursor.execute('SELECT author, text FROM posts WHERE sentiment="Negative" ORDER BY score ASC LIMIT 5')
    top_neg = cursor.fetchall()

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Sentiment Dashboard</title>
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
        .header .live {{ color: #ff4444; font-weight: bold; }}
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
        .comment {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }}
        .comment.positive {{ border-left-color: #28a745; }}
        .comment.negative {{ border-left-color: #dc3545; }}
        .comment-text {{ color: #333; line-height: 1.5; margin-bottom: 8px; }}
        .comment-meta {{ font-size: 0.85em; color: #999; }}
        h2 {{ margin-top: 30px; margin-bottom: 15px; }}
        .refresh {{ font-size: 0.9em; color: #999; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Live Sentiment Analysis</h1>
            <p><span class="live">● LIVE</span> Real-time YouTube & X data • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.9;">Updates automatically every hour via GitHub Actions</p>
        </div>

        <div class="content">
            <div class="stats">
                <div class="stat">
                    <h3>Total Analyzed</h3>
                    <div class="number">{total}</div>
                </div>
                <div class="stat">
                    <h3>😊 Positive</h3>
                    <div class="number" style="color: #28a745;">{pos}</div>
                    <p>{round(pos/total*100 if total else 0, 1)}%</p>
                </div>
                <div class="stat">
                    <h3>😞 Negative</h3>
                    <div class="number" style="color: #dc3545;">{neg}</div>
                    <p>{round(neg/total*100 if total else 0, 1)}%</p>
                </div>
                <div class="stat">
                    <h3>Satisfaction</h3>
                    <div class="number" style="color: #667eea;">{satisfaction}%</div>
                    <p>{'✅ EXCELLENT' if satisfaction >= 70 else '🟡 GOOD' if satisfaction >= 50 else '🔴 CRITICAL'}</p>
                </div>
            </div>

            <div class="charts">
                <div class="chart-box">
                    <h3>Overall Sentiment</h3>
                    <canvas id="overall"></canvas>
                </div>
                <div class="chart-box">
                    <h3>YouTube vs X</h3>
                    <canvas id="comparison"></canvas>
                </div>
            </div>

            <h2>💚 Top Positive Feedback</h2>
            {''.join([f'<div class="comment positive"><div class="comment-text">"{text}"</div><div class="comment-meta">{author}</div></div>' for author, text in top_pos])}

            <h2>❤️ Top Negative Feedback</h2>
            {''.join([f'<div class="comment negative"><div class="comment-text">"{text}"</div><div class="comment-meta">{author}</div></div>' for author, text in top_neg])}

            <div class="refresh">
                ⏰ This dashboard updates automatically every hour<br>
                🤖 Powered by automated GitHub Actions
            </div>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('overall'), {{
            type: 'doughnut',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{{
                    data: [{pos}, {neg}, {neu}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }});

        new Chart(document.getElementById('comparison'), {{
            type: 'bar',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [
                    {{label: 'YouTube', data: [{yt_stats[1]}, {yt_stats[2]}, {yt_stats[3]}], backgroundColor: '#667eea'}},
                    {{label: 'X', data: [{x_stats[1]}, {x_stats[2]}, {x_stats[3]}], backgroundColor: '#764ba2'}}
                ]
            }},
            options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
    </script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("     ✅ Dashboard: index.html")
    conn.close()

def main():
    """Main function"""
    print("\n" + "="*70)
    print("  🚀 PRODUCTION SENTIMENT BOT")
    print("  Real YouTube API + Real X API")
    print("="*70)
    print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    setup_db()

    yt_total = collect_youtube_comments(max_comments=20)
    x_total = collect_x_posts(max_posts=20)

    analyze_results()
    generate_dashboard()

    print("\n" + "="*70)
    print("✅ CYCLE COMPLETE")
    print(f"   YouTube: {yt_total}")
    print(f"   X: {x_total}")
    print(f"   Total: {yt_total + x_total}")
    print(f"\n   📊 Dashboard: index.html")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
