#!/usr/bin/env python3
"""
Auto-Discovery Sentiment Bot
Bot automatically finds YouTube videos and analyzes comments
"""

import sqlite3
import requests
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from youtube_comment_downloader import YoutubeCommentDownloader

analyzer = SentimentIntensityAnalyzer()
DB_FILE = "auto_sentiment.db"

# Search topics - bot will find videos for these
SEARCH_TOPICS = [
    "product review",
    "customer service",
    "shopping haul",
    "unboxing",
    "best deals",
]

# Popular video URLs (fallback if search fails)
POPULAR_VIDEOS = [
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=L4KzWxWRx8w",
    "https://www.youtube.com/watch?v=Z0EHvVFhO7c",
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
            video_url TEXT,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

def save_post(source, author, text, sentiment, score, video_url):
    """Save to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO posts (source, author, text, sentiment, score, video_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source, author, text, sentiment, score, video_url))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def auto_find_youtube_videos(search_topic):
    """Automatically find YouTube videos for a topic"""
    print(f"\n  🔍 Searching YouTube for: '{search_topic}'")

    videos = []

    try:
        # Try searching via YouTube
        search_url = f"https://www.youtube.com/results?search_query={search_topic}&sp=CAMSBAgIARgC"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Look for video IDs in the response
            import re
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)

            if video_ids:
                for vid_id in video_ids[:3]:  # Get top 3
                    videos.append(f"https://www.youtube.com/watch?v={vid_id}")
                print(f"     ✅ Found {len(videos)} videos")
                return videos

    except Exception as e:
        print(f"     ⚠️  Search error: {e}")

    # Fallback: use popular videos
    print(f"     📝 Using popular videos...")
    return POPULAR_VIDEOS[:2]

def analyze_youtube_comments(video_url, max_comments=30):
    """Analyze comments from a specific video"""
    total = 0

    try:
        downloader = YoutubeCommentDownloader()
        comment_count = 0

        for comment in downloader.get_comments_from_url(video_url, sort_by='recent'):
            if comment_count >= max_comments:
                break

            text = comment.get('text', '')
            author = comment.get('author', 'Unknown')

            if len(text.strip()) < 3:
                continue

            sentiment, score = analyze_sentiment(text)

            if save_post('YouTube', author, text, sentiment, score, video_url):
                comment_count += 1
                total += 1
                print(f"       ✅ [{sentiment}] {text[:50]}...")

        return total

    except Exception as e:
        print(f"       ⚠️  Error: {e}")
        return 0

def main():
    """Main function"""
    print("\n" + "="*70)
    print("  🤖 AUTO-DISCOVERY SENTIMENT BOT")
    print("  Finding and analyzing YouTube videos automatically...")
    print("="*70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    setup_db()

    total_posts = 0

    # For each search topic
    for topic in SEARCH_TOPICS:
        print(f"\n📌 Topic: '{topic}'")
        print("-" * 70)

        # Find videos for this topic
        videos = auto_find_youtube_videos(topic)

        # Analyze comments from found videos
        for video_url in videos:
            print(f"\n  📹 Analyzing: {video_url}")

            analyzed = analyze_youtube_comments(video_url, max_comments=20)
            total_posts += analyzed

            if analyzed > 0:
                print(f"     ✅ Analyzed {analyzed} comments")
            else:
                print(f"     ⚠️  No comments collected")

    # Analyze results
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

    print(f"\n  📈 OVERALL RESULTS:")
    print(f"     Total Posts: {total}")
    print(f"     Positive: {pos or 0} ({round((pos or 0)/total*100 if total else 0, 1)}%)")
    print(f"     Negative: {neg or 0} ({round((neg or 0)/total*100 if total else 0, 1)}%)")
    print(f"     Neutral: {neu or 0} ({round((neu or 0)/total*100 if total else 0, 1)}%)")
    print(f"     Avg Sentiment Score: {round(avg or 0, 2)}")

    satisfaction = round((pos or 0) / total * 100 if total > 0 else 0, 1)
    print(f"\n  😊 CUSTOMER SATISFACTION: {satisfaction}%")

    if satisfaction >= 70:
        print(f"     Status: ✅ EXCELLENT - Customers very happy")
    elif satisfaction >= 50:
        print(f"     Status: 🟡 GOOD - Most satisfied")
    else:
        print(f"     Status: 🔴 NEEDS IMPROVEMENT")

    # Top feedback
    print(f"\n  💚 TOP POSITIVE FEEDBACK:")
    cursor.execute('''
        SELECT text, video_url FROM posts
        WHERE sentiment='Positive'
        ORDER BY score DESC
        LIMIT 3
    ''')

    for text, url in cursor.fetchall():
        print(f"     \"{text}\"")

    print(f"\n  ❤️ TOP NEGATIVE FEEDBACK:")
    cursor.execute('''
        SELECT text, video_url FROM posts
        WHERE sentiment='Negative'
        ORDER BY score ASC
        LIMIT 3
    ''')

    for text, url in cursor.fetchall():
        print(f"     \"{text}\"")

    # Generate HTML report
    print(f"\n  📊 Generating report...")

    cursor.execute('''
        SELECT source,
               SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END),
               SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END)
        FROM posts
        GROUP BY source
    ''')

    source_stats = cursor.fetchall()
    yt_stats = source_stats[0] if source_stats else ('YouTube', 0, 0, 0)

    cursor.execute('''
        SELECT text FROM posts
        WHERE sentiment='Positive'
        ORDER BY score DESC
        LIMIT 5
    ''')
    top_pos = [t[0] for t in cursor.fetchall()]

    cursor.execute('''
        SELECT text FROM posts
        WHERE sentiment='Negative'
        ORDER BY score ASC
        LIMIT 5
    ''')
    top_neg = [t[0] for t in cursor.fetchall()]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Discovery Sentiment Report</title>
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
        .chart-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
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
        .comment-text {{ color: #333; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Auto-Discovery Sentiment Analysis</h1>
            <p>Bot automatically found and analyzed YouTube videos • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="content">
            <div class="stats">
                <div class="stat">
                    <h3>Total Analyzed</h3>
                    <div class="number">{total}</div>
                </div>
                <div class="stat">
                    <h3>😊 Positive</h3>
                    <div class="number" style="color: #28a745;">{pos or 0}</div>
                </div>
                <div class="stat">
                    <h3>😞 Negative</h3>
                    <div class="number" style="color: #dc3545;">{neg or 0}</div>
                </div>
                <div class="stat">
                    <h3>Satisfaction</h3>
                    <div class="number" style="color: #667eea;">{satisfaction}%</div>
                </div>
            </div>

            <div class="chart-box">
                <h3>Sentiment Distribution</h3>
                <canvas id="chart"></canvas>
            </div>

            <h2>💚 Positive Feedback</h2>
            {''.join([f'<div class="comment positive"><div class="comment-text">{t}</div></div>' for t in top_pos])}

            <h2 style="margin-top: 30px;">❤️ Negative Feedback</h2>
            {''.join([f'<div class="comment negative"><div class="comment-text">{t}</div></div>' for t in top_neg])}
        </div>
    </div>

    <script>
        new Chart(document.getElementById('chart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{{
                    data: [{pos or 0}, {neg or 0}, {neu or 0}],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }});
    </script>
</body>
</html>"""

    with open('auto_report.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("     ✅ Report: auto_report.html")

    conn.close()

    print("\n" + "="*70)
    print("✅ AUTO-DISCOVERY CYCLE COMPLETE")
    print(f"   Videos Found: Multiple")
    print(f"   Comments Analyzed: {total}")
    print(f"   Report: auto_report.html")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
