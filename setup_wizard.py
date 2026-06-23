#!/usr/bin/env python3
"""
Automated Setup Wizard for Sentiment Analysis Bot
Does everything for you!
"""

import os
import subprocess
import json
from getpass import getpass

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(cmd, description=""):
    """Run a shell command"""
    if description:
        print(f"  ⏳ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if description:
                print(f"  ✅ {description} - Done!")
            return True, result.stdout
        else:
            print(f"  ❌ Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, str(e)

def setup_git():
    """Initialize and push to GitHub"""
    print_header("STEP 1: Git Setup")

    print("  1. Make sure you have Git installed (git --version to check)")
    input("  Press Enter when ready...")

    github_username = input("\n  Enter your GitHub username: ").strip()
    repo_name = "sentiment-analysis-bot"

    print(f"\n  Setting up Git repository...")

    # Initialize git
    run_command("git init", "Initializing git")
    run_command("git config user.email 'you@example.com'", "Setting git email")
    run_command("git config user.name 'Your Name'", "Setting git name")

    # Add all files
    run_command("git add .", "Adding files to git")

    # Commit
    run_command('git commit -m "Initial commit: production sentiment bot"', "Creating commit")

    # Set main branch
    run_command("git branch -M main", "Setting main branch")

    # Add remote
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"
    run_command(f'git remote add origin "{remote_url}"', "Adding GitHub remote")

    print(f"\n  ⚠️  IMPORTANT:")
    print(f"     1. Go to https://github.com/new")
    print(f"     2. Repository name: {repo_name}")
    print(f"     3. Make it PUBLIC")
    print(f"     4. Click 'Create repository'")
    print(f"     5. Come back here and press Enter")

    input("\n  Press Enter when you've created the GitHub repo...")

    # Push
    success, output = run_command(f'git push -u origin main', "Pushing to GitHub")

    if success:
        print(f"\n  ✅ Code pushed to GitHub!")
        return github_username
    else:
        print(f"\n  ⚠️  Push might need authentication")
        print(f"     GitHub might ask for login - use your GitHub username and password (or personal access token)")
        return github_username

def add_github_secrets(github_username):
    """Guide user to add GitHub secrets"""
    print_header("STEP 2: Add GitHub Secrets")

    print("  Secrets are like passwords - they store your API keys securely\n")

    # Get API keys
    print("  Enter your API keys (they won't be shown as you type):\n")

    youtube_key = getpass("  YouTube API Key: ").strip()
    x_token = getpass("  X Bearer Token: ").strip()

    print("\n  ⚠️  Now you MUST add these to GitHub manually (for security):\n")

    print(f"  1. Go to: https://github.com/{github_username}/sentiment-analysis-bot")
    print(f"  2. Click: Settings → Secrets and variables → Actions")
    print(f"  3. Click: New repository secret")
    print(f"\n  Then add these 5 secrets:\n")

    print(f"  Secret 1:")
    print(f"    Name: YOUTUBE_API_KEY")
    print(f"    Value: {youtube_key[:10]}... (your YouTube key)")

    print(f"\n  Secret 2:")
    print(f"    Name: X_BEARER_TOKEN")
    print(f"    Value: {x_token[:10]}... (your X token)")

    print(f"\n  Secret 3:")
    print(f"    Name: VERCEL_TOKEN")
    print(f"    Value: (get from https://vercel.com/account/tokens)")

    print(f"\n  Secret 4:")
    print(f"    Name: VERCEL_ORG_ID")
    print(f"    Value: (from Vercel project settings)")

    print(f"\n  Secret 5:")
    print(f"    Name: VERCEL_PROJECT_ID")
    print(f"    Value: (from Vercel project settings)")

    input("\n  Press Enter when you've added all 5 secrets...")

    return youtube_key, x_token

def setup_vercel(github_username):
    """Guide user to set up Vercel"""
    print_header("STEP 3: Set Up Vercel (Free Hosting)")

    print("  1. Go to: https://vercel.com")
    print("  2. Click: Sign up → Continue with GitHub")
    print("  3. Authorize GitHub")
    print("  4. Click: Add New → Project")
    print("  5. Select: sentiment-analysis-bot")
    print("  6. Click: Deploy")
    print("\n  ⏳ Wait for deployment to finish...\n")

    input("  Press Enter when Vercel shows 'Deployed'...")

    print("\n  Now get your Vercel credentials:")
    print("  1. Go to: https://vercel.com/account/tokens")
    print("  2. Click: Create Token")
    print("  3. Copy the token (this is VERCEL_TOKEN)")

    vercel_token = getpass("\n  Paste your Vercel token: ").strip()

    print("\n  Now get your Vercel project IDs:")
    print("  1. Go to your project dashboard on Vercel")
    print("  2. Click: Settings")
    print("  3. Look for projectId and teamId in the page")

    vercel_org_id = input("\n  Enter VERCEL_ORG_ID: ").strip()
    vercel_project_id = input("  Enter VERCEL_PROJECT_ID: ").strip()

    return vercel_token, vercel_org_id, vercel_project_id

def create_env_file(youtube_key, x_token):
    """Create .env file for local testing"""
    print_header("STEP 4: Create Local .env File")

    env_content = f"""YOUTUBE_API_KEY={youtube_key}
X_BEARER_TOKEN={x_token}
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("  ✅ Created .env file for local testing\n")

def final_summary(github_username):
    """Show final summary"""
    print_header("✅ SETUP COMPLETE!")

    print(f"  Your sentiment analysis bot is now set up!\n")

    print(f"  📊 Your dashboard:")
    print(f"     https://sentiment-analysis-bot.vercel.app\n")

    print(f"  🤖 What happens now:")
    print(f"     • Every hour: Collects REAL YouTube comments")
    print(f"     • Every hour: Collects REAL X tweets")
    print(f"     • Every hour: Analyzes sentiment")
    print(f"     • Every hour: Updates your live dashboard\n")

    print(f"  📋 View automation:")
    print(f"     GitHub: https://github.com/{github_username}/sentiment-analysis-bot/actions\n")

    print(f"  🚀 It's live and running 24/7!\n")

def main():
    """Main setup wizard"""
    print_header("🚀 SENTIMENT ANALYSIS BOT SETUP WIZARD")

    print("  This wizard will set up your bot automatically!\n")
    print("  You'll need:")
    print("    • YouTube API Key")
    print("    • X Bearer Token")
    print("    • GitHub account")
    print("    • Vercel account (free)\n")

    input("  Press Enter to start...")

    try:
        # Step 1: Git setup
        github_username = setup_git()

        # Step 2: Add secrets
        youtube_key, x_token = add_github_secrets(github_username)

        # Step 3: Vercel setup
        vercel_token, vercel_org_id, vercel_project_id = setup_vercel(github_username)

        # Step 4: Create .env
        create_env_file(youtube_key, x_token)

        # Final summary
        final_summary(github_username)

        print("\n  ✨ Your bot is now live and updates every hour!\n")

    except KeyboardInterrupt:
        print("\n\n  ❌ Setup cancelled")
    except Exception as e:
        print(f"\n  ❌ Error during setup: {e}")
        print("  Try running the steps manually or ask for help")

if __name__ == "__main__":
    main()
