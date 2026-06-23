import tweepy
import os
from dotenv import load_dotenv
from sentiment_analyzer import analyze_sentiment
from storage import add_comment

load_dotenv()

def get_x_client():
    """Create and return authenticated X/Twitter client"""
    bearer_token = os.getenv('X_BEARER_TOKEN')

    if not bearer_token:
        print("❌ X (Twitter) Bearer Token not found in .env file")
        print("   See README.md for setup instructions")
        return None

    try:
        client = tweepy.Client(bearer_token=bearer_token)
        print("✅ Connected to X (Twitter) API")
        return client
    except Exception as e:
        print(f"❌ Failed to authenticate with X API: {str(e)}")
        return None

def collect_x_tweets(searches, client, max_tweets=500):
    """Collect tweets from X/Twitter"""
    print("\n=== X (Twitter) Tweet Collection ===")

    if not client:
        print("❌ X client not available")
        return 0

    total_collected = 0

    for search_data in searches:
        query = search_data.get('query')
        label = search_data.get('label', query)

        print(f"\nSearching X for: '{query}'")
        print(f"Label: {label}")

        try:
            tweets_data = client.search_recent_tweets(
                query=query,
                max_results=min(100, max_tweets),
                tweet_fields=['public_metrics', 'created_at', 'author_id'],
                expansions=['author_id'],
                user_fields=['username']
            )

            if not tweets_data.data:
                print(f"⚠️  No tweets found for: {query}")
                continue

            users_dict = {}
            if tweets_data.includes and 'users' in tweets_data.includes:
                for user in tweets_data.includes['users']:
                    users_dict[user.id] = user.username

            tweet_count = 0
            for tweet in tweets_data.data:
                if tweet_count >= max_tweets:
                    break

                text = tweet.text
                author = users_dict.get(tweet.author_id, f'User_{tweet.author_id}')
                tweet_id = tweet.id

                if len(text.strip()) < 3:
                    continue

                sentiment = analyze_sentiment(text)
                add_comment(
                    source='X',
                    source_id=str(tweet_id),
                    author=author,
                    text=text,
                    sentiment_scores=sentiment
                )

                tweet_count += 1
                total_collected += 1

                if tweet_count % 25 == 0:
                    print(f"  📝 Collected {tweet_count} tweets...")

            print(f"✅ Collected {tweet_count} tweets for '{label}'")

        except tweepy.TweepyException as e:
            print(f"❌ X API error for '{query}': {str(e)}")
            if "429" in str(e):
                print("   Rate limit reached. Try again in 15 minutes.")
            continue
        except Exception as e:
            print(f"❌ Error collecting from '{query}': {str(e)}")
            continue

    print(f"\n✅ Total X tweets collected: {total_collected}")
    return total_collected
