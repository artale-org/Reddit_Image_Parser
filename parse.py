import praw
import os # Optional: To load credentials from environment variables
import requests
import shutil
import re # <-- Add import for regular expressions (for sanitizing)
import sys # <-- Add import for sys
import datetime # <-- Add import for timestamps

# --- Reddit API Credentials ---
# Replace with your actual credentials obtained from https://www.reddit.com/prefs/apps/
# It's recommended to use environment variables for security instead of hardcoding.
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "xxx") # Replace YOUR_CLIENT_ID or set env var
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "xxx") # Replace YOUR_CLIENT_SECRET or set env var
USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "xxx") # Replace YourUsername or set env var

# --- Configuration ---
SUBREDDIT_NAME = "AIArtwork" # Art, AIArtwork, aiArt
POST_LIMIT = 5000 # How many posts to fetch (adjust as needed, None for potentially more)
DOWNLOAD_DIR = SUBREDDIT_NAME
LOG_FILE = "parse.log" # <-- Define log file name

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- Helper function to sanitize filenames ---
def sanitize_filename(title):
    """Removes or replaces characters invalid for filenames."""
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)
    # Replace colons potentially missed (though covered above)
    sanitized = sanitized.replace(":", "-")
    # Replace excessive whitespace with a single underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Limit length to avoid issues (e.g., max 150 chars)
    max_len = 150
    if len(sanitized) > max_len:
        # Find the last underscore before the limit to avoid cutting words
        cut_off = sanitized[:max_len].rfind('_')
        if cut_off > max_len / 2: # Only cut at underscore if it's reasonably far in
             sanitized = sanitized[:cut_off]
        else:
             sanitized = sanitized[:max_len] # Otherwise, just truncate
    return sanitized.strip('_') # Remove leading/trailing underscores
# --- End helper function ---

# --- Helper function for logging ---
def log_message(message):
    """Prints a message with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
# --- End helper function ---

def fetch_ai_artwork_posts():
    """
    Fetches image posts (titles and URLs) from the specified subreddit.
    """
    log_message(f"--- Script execution started ---") # <-- Use log_message
    log_message(f"Connecting to Reddit API...") # <-- Use log_message
    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )
        # Verify connection is read-only (no user login needed for public subreddits)
        log_message(f"Read-only status: {reddit.read_only}") # <-- Use log_message
        log_message(f"Fetching posts and downloading images from r/{SUBREDDIT_NAME}...") # <-- Use log_message

        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        posts_data = []
        downloaded_count = 0
        skipped_count = 0
        error_count = 0
        # Fetch 'hot' posts, you can change to 'new', 'top', etc.
        for submission in subreddit.hot(limit=POST_LIMIT):
            # Check if the post URL likely points to an image
            # This is a basic check, might miss galleries or other image sources
            url = submission.url
            is_image = url.endswith(('.jpg', '.jpeg', '.png', '.gif')) or 'i.redd.it' in url or 'i.imgur.com' in url

            if is_image:
                posts_data.append({
                    "title": submission.title,
                    "url": url,
                    "score": submission.score,
                    "id": submission.id
                })
                log_message(f"Found: {submission.title[:50]}... ({url})") # <-- Use log_message

                # --- Image Download Logic ---
                try:
                    # Get the file extension
                    file_extension = os.path.splitext(url)[1]

                    # --- Generate filename from title ---
                    sanitized_title = sanitize_filename(submission.title)
                    if not sanitized_title: # Handle cases where title becomes empty after sanitizing
                        sanitized_title = submission.id # Fallback to ID if title is unusable
                    filename = f"{sanitized_title}{file_extension}"
                    # --- End filename generation ---

                    filepath = os.path.join(DOWNLOAD_DIR, filename)

                    # Check if file already exists to avoid re-downloading
                    if not os.path.exists(filepath):
                        log_message(f"  Downloading to {filepath}...") # <-- Use log_message
                        response = requests.get(url, stream=True)
                        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                        with open(filepath, 'wb') as f:
                            # Copy the response stream directly to the file
                            response.raw.decode_content = True # Ensure compressed content is handled
                            shutil.copyfileobj(response.raw, f)
                        log_message(f"  Saved: {filepath}") # <-- Use log_message
                        downloaded_count += 1
                    else:
                        log_message(f"  Skipping download, file already exists: {filepath}") # <-- Use log_message
                        skipped_count += 1

                except requests.exceptions.RequestException as req_err:
                    log_message(f"An error occurred with requests: {req_err}") # <-- Use log_message
                    error_count += 1
                except IOError as io_err:
                    log_message(f"An I/O error occurred: {io_err}") # <-- Use log_message
                    error_count += 1
                except Exception as e:
                    log_message(f"An unexpected error occurred: {e}") # <-- Use log_message
                    error_count += 1
                # --- End Image Download Logic ---

            # else:
                # log_message(f"Skipping non-direct image post: {submission.title[:50]}... ({url})") # <-- Use log_message

        log_message(f"\n--- Fetch Summary ---") # <-- Use log_message
        log_message(f"Found {len(posts_data)} potential image posts.") # <-- Use log_message
        log_message(f"Successfully downloaded: {downloaded_count}") # <-- Use log_message
        log_message(f"Skipped (already exist): {skipped_count}") # <-- Use log_message
        log_message(f"Errors during download: {error_count}") # <-- Use log_message
        return posts_data

    except praw.exceptions.PRAWException as e:
        log_message(f"An error occurred with PRAW: {e}") # <-- Use log_message
        log_message("Please ensure your Reddit API credentials (CLIENT_ID, CLIENT_SECRET, USER_AGENT) are correct.") # <-- Use log_message
        return []
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}") # <-- Use log_message
        return []
    finally:
        log_message(f"--- Script execution finished ---") # <-- Use log_message

if __name__ == "__main__":
    # --- Redirect stdout to log file ---
    original_stdout = sys.stdout # Store original stdout
    log_file_handle = open(LOG_FILE, 'a', encoding='utf-8') # Open log file in append mode
    sys.stdout = log_file_handle # Redirect stdout
    # --- End redirection ---

    try:
        # Example usage:
        artwork_posts = fetch_ai_artwork_posts()

        # You can now process the 'artwork_posts' list
        # For example, print them out (this will now go to the log file):
        log_message("\n--- Collected Post Info (Details in Log) ---") # <-- Use log_message
        if artwork_posts:
            # Keep this loop minimal or remove if detail isn't needed outside download phase
            # for i, post in enumerate(artwork_posts):
            #     log_message(f"{i+1}. Title: {post['title']}")
            #     log_message(f"   URL: {post['url']}")
            #     log_message(f"   Score: {post['score']}")
            #     log_message("-" * 10)
            pass # Pass here as summary is printed within fetch_ai_artwork_posts
        else:
            log_message("No image posts were fetched or processed.") # <-- Use log_message

    except Exception as e:
        # Log any unexpected errors in the main block
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] UNHANDLED EXCEPTION in main block: {e}", file=sys.stderr) # Print to stderr to see on console
        log_message(f"UNHANDLED EXCEPTION in main block: {e}") # Also log it

    finally:
        # --- Restore stdout ---
        sys.stdout = original_stdout # Restore original stdout
        log_file_handle.close() # Close the log file
        print(f"Script finished. Output saved to {LOG_FILE}") # Print final confirmation to console
        # --- End restore ---
