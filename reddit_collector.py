import praw
import os
from dotenv import load_dotenv
from sentiment_analyzer import analyze_sentiment
from storage import add_comment

load_dotenv()

def get_reddit_instance():
    """Create and return authenticated Reddit instance"""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'SentimentAnalyzer/1.0')

    if not client_id or not client_secret:
        print("❌ Reddit credentials not found in .env file")
        print("   See README.md for setup instructions")
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        reddit.auth.refresh()
        print("✅ Connected to Reddit API")
        return reddit
    except Exception as e:
        print(f"❌ Failed to authenticate with Reddit: {str(e)}")
        return None

def collect_reddit_comments(searches, reddit_instance, max_comments=500):
    """Collect comments from Reddit"""
    print("\n=== Reddit Comment Collection ===")

    if not reddit_instance:
        print("❌ Reddit instance not available")
        return 0

    total_collected = 0

    for search_data in searches:
        subreddit_name = search_data.get('subreddit')
        keywords = search_data.get('keywords', '')
        label = search_data.get('label', f'r/{subreddit_name}')

        print(f"\nSearching r/{subreddit_name} for: '{keywords}'")
        print(f"Label: {label}")

        try:
            subreddit = reddit_instance.subreddit(subreddit_name)
            comment_count = 0

            search_query = keywords if keywords else None
            submissions = subreddit.search(
                search_query,
                sort='new',
                time_filter='week',
                limit=100
            ) if search_query else subreddit.new(limit=100)

            for submission in submissions:
                if comment_count >= max_comments:
                    break

                submission.comments.replace_more(limit=0)

                for comment in submission.comments.list():
                    if comment_count >= max_comments:
                        break

                    text = comment.body
                    author = comment.author.name if comment.author else 'Unknown'
                    comment_id = comment.id

                    if len(text.strip()) < 3:
                        continue

                    sentiment = analyze_sentiment(text)
                    add_comment(
                        source='Reddit',
                        source_id=comment_id,
                        author=author,
                        text=text,
                        sentiment_scores=sentiment
                    )

                    comment_count += 1
                    total_collected += 1

                    if comment_count % 50 == 0:
                        print(f"  📝 Collected {comment_count} comments...")

            print(f"✅ Collected {comment_count} comments from r/{subreddit_name}")

        except Exception as e:
            print(f"❌ Error collecting from r/{subreddit_name}: {str(e)}")
            continue

    print(f"\n✅ Total Reddit comments collected: {total_collected}")
    return total_collected
