# Reddit AI Artwork Downloader

A Python script for automatically downloading images from AI artwork subreddits.

## Description

This script connects to the Reddit API and fetches image posts from specified subreddits, particularly those featuring AI-generated artwork. It downloads the images locally while preserving post titles as filenames and maintains a detailed log of operations.

## Features

- Fetches image posts from any subreddit (default: r/AIArtwork)
- Downloads images to a local directory
- Sanitizes filenames based on post titles
- Skips already downloaded images
- Comprehensive logging of all operations
- Configurable post limit

## Requirements

- Python 3.6+
- Required Python packages:
  - praw
  - requests

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:
    ```bash
    pip install praw requests
    ```

## Usage
Run the script with Python:

```bash
python parse.py
```
The script will:
1. Connect to the Reddit API
2. Fetch posts from the configured subreddit
3. Download images from valid image posts
4. Save all logs to the specified log file
5. Create a directory named after the subreddit and save all images there

## Output

- All downloaded images will be saved to the configured directory
- Filenames will be based on post titles (sanitized for valid filesystem characters)
- Operation logs will be saved to the configured log file
- A summary will be displayed when the script completes

## Limitations

- The script primarily handles direct image links and may not capture gallery posts or other complex media types
- Reddit API has rate limits (1000 requests per minute) which may affect large-scale scraping
- Very long post titles will be truncated to avoid filesystem issues

## License

[Insert your license information here]

