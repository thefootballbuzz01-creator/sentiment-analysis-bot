from youtube_comment_downloader import *
import re
from sentiment_analyzer import analyze_sentiment
from storage import add_comment

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtube\.com\/embed\/)([0-9A-Za-z_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None

def collect_youtube_comments(video_urls, max_comments=500):
    """Collect comments from YouTube videos"""
    print("\n=== YouTube Comment Collection ===")
    total_collected = 0

    for video_data in video_urls:
        url = video_data.get('url')
        label = video_data.get('label', 'Unknown')

        video_id = extract_video_id(url)
        if not video_id:
            print(f"⚠️  Could not extract video ID from: {url}")
            continue

        print(f"\nCollecting comments from: {label}")
        print(f"Video URL: {url}")

        try:
            downloader = YoutubeCommentDownloader()
            comments_data = downloader.get_comments_from_url(
                url,
                sort_by=SORT_BY_RECENT
            )

            comment_count = 0
            for comment in comments_data:
                if comment_count >= max_comments:
                    break

                text = comment.get('text', '')
                author = comment.get('author', 'Unknown')
                comment_id = comment.get('cid', '')

                if not text or len(text.strip()) < 3:
                    continue

                sentiment = analyze_sentiment(text)
                add_comment(
                    source='YouTube',
                    source_id=comment_id,
                    author=author,
                    text=text,
                    sentiment_scores=sentiment
                )

                comment_count += 1
                total_collected += 1

                if comment_count % 50 == 0:
                    print(f"  📝 Collected {comment_count} comments...")

            print(f"✅ Collected {comment_count} comments from {label}")

        except Exception as e:
            print(f"❌ Error collecting from {label}: {str(e)}")
            continue

    print(f"\n✅ Total YouTube comments collected: {total_collected}")
    return total_collected
