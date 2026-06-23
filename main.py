#!/usr/bin/env python3
import sys
from datetime import datetime
from config_loader import load_config, validate_config
from storage import initialize_database, record_run
from youtube_collector import collect_youtube_comments
from x_collector import collect_x_tweets, get_x_client
from report_generator import generate_html_report

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("  🎯 SENTIMENT ANALYSIS PIPELINE")
    print("="*60)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

def run_pipeline():
    """Run the complete sentiment analysis pipeline"""
    print_banner()

    config = load_config('config.json')
    if not config or not validate_config(config):
        print("❌ Configuration loading failed")
        return False

    print("✅ Configuration loaded successfully\n")

    initialize_database()
    print("✅ Database initialized\n")

    youtube_count = 0
    x_count = 0

    if config.get('youtube', {}).get('enabled', False):
        youtube_videos = config.get('youtube', {}).get('videos', [])
        if youtube_videos:
            max_yt = config.get('analysis', {}).get('max_comments_per_source', 500)
            youtube_count = collect_youtube_comments(youtube_videos, max_yt)
        else:
            print("⚠️  YouTube enabled but no videos configured")
    else:
        print("⏭️  YouTube collection disabled")

    if config.get('x', {}).get('enabled', False):
        x_searches = config.get('x', {}).get('searches', [])
        if x_searches:
            x_client = get_x_client()
            if x_client:
                max_x = config.get('analysis', {}).get('max_comments_per_source', 500)
                x_count = collect_x_tweets(x_searches, x_client, max_x)
            else:
                print("⚠️  X API credentials not configured")
        else:
            print("⚠️  X enabled but no searches configured")
    else:
        print("⏭️  X collection disabled")

    print("\n" + "="*60)
    print(f"✅ Collection complete!")
    print(f"   YouTube comments: {youtube_count}")
    print(f"   X tweets: {x_count}")
    print(f"   Total: {youtube_count + x_count}")
    print("="*60 + "\n")

    record_run(youtube_count, x_count)

    print("📊 Generating report...")
    generate_html_report()

    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY")
    print(f"   Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    return True

if __name__ == '__main__':
    try:
        success = run_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Pipeline error: {str(e)}")
        print("\nFor help, check README.md")
        sys.exit(1)
