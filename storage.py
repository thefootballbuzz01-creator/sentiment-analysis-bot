import sqlite3
import os
from datetime import datetime

DB_PATH = "database"
DB_FILE = os.path.join(DB_PATH, "sentiment.db")

def initialize_database():
    """Create database and tables if they don't exist"""
    os.makedirs(DB_PATH, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            author TEXT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            positive_score REAL,
            negative_score REAL,
            neutral_score REAL,
            compound_score REAL,
            created_at TIMESTAMP,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, source_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            youtube_count INTEGER DEFAULT 0,
            reddit_count INTEGER DEFAULT 0,
            total_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed'
        )
    ''')

    conn.commit()
    conn.close()

def add_comment(source, source_id, author, text, sentiment_scores):
    """Add a comment to the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO comments
            (source, source_id, author, text, sentiment, positive_score,
             negative_score, neutral_score, compound_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source,
            source_id,
            author,
            text,
            sentiment_scores['label'],
            sentiment_scores['pos'],
            sentiment_scores['neg'],
            sentiment_scores['neu'],
            sentiment_scores['compound'],
            datetime.now()
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding comment: {e}")
        return False
    finally:
        conn.close()

def get_all_comments():
    """Retrieve all comments from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM comments ORDER BY collected_at DESC')
    rows = cursor.fetchall()
    conn.close()

    return rows

def get_comments_by_source(source):
    """Get comments filtered by source (youtube or reddit)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM comments WHERE source = ? ORDER BY collected_at DESC',
        (source,)
    )
    rows = cursor.fetchall()
    conn.close()

    return rows

def get_sentiment_stats():
    """Get sentiment statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT source, sentiment, COUNT(*) as count
        FROM comments
        GROUP BY source, sentiment
    ''')
    stats = cursor.fetchall()
    conn.close()

    return stats

def get_top_comments(sentiment_type, limit=5):
    """Get top comments by sentiment"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if sentiment_type == 'positive':
        cursor.execute('''
            SELECT source, author, text, compound_score
            FROM comments
            WHERE sentiment = 'Positive'
            ORDER BY compound_score DESC
            LIMIT ?
        ''', (limit,))
    elif sentiment_type == 'negative':
        cursor.execute('''
            SELECT source, author, text, compound_score
            FROM comments
            WHERE sentiment = 'Negative'
            ORDER BY compound_score ASC
            LIMIT ?
        ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows

def record_run(youtube_count, reddit_count):
    """Record a pipeline run"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO runs (started_at, completed_at, youtube_count, reddit_count, total_count, status)
        VALUES (?, ?, ?, ?, ?, 'completed')
    ''', (datetime.now(), datetime.now(), youtube_count, reddit_count, youtube_count + reddit_count))

    conn.commit()
    conn.close()

def get_last_update_time():
    """Get the timestamp of the last successful run"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT completed_at FROM runs WHERE status = "completed" ORDER BY completed_at DESC LIMIT 1'
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None
