# Instagram Spider

A data scraping tool for Instagram to collect user lists from hashtags and post comments.

[中文文档](README.md)

## ✨ Features

- 📌 **Hashtag User Collection** - Get user information from posts under a specific hashtag
- 💬 **Post Comment Collection** - Get comment users from a specific post (with tree structure)
- 📊 **Hashtag Posts + Comments** - Batch collect posts and their comments under a hashtag (one sheet per post)
- 🔐 **Session Persistence** - Login state is automatically saved for future use
- 📁 **Multiple Export Formats** - Export to Excel and JSON formats

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/deepco_ig_spider.git
cd deepco_ig_spider
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

After running, an interactive menu will be displayed:

```
Please select an option:
  1. Get user list from hashtag
  2. Get comment users from a post
  3. Get posts and comments from hashtag (one sheet per post)
  4. Login (enter sessionid)
  5. Logout
  6. Test network connection
  7. Exit
```

### Command Line Mode

```bash
# Get hashtag users (up to 50 posts)
python main.py --hashtag python --max-posts 50

# Get post comment users
python main.py --media-id 1234567890 --max-comments 100
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--hashtag` | `-t` | Hashtag (without #) | - |
| `--media-id` | `-m` | Post's media_id (pk) | - |
| `--max-posts` | - | Maximum number of posts to fetch | 50 |
| `--max-comments` | - | Maximum number of comments to fetch | 100 |

## 🔐 Login Instructions

This tool requires Instagram session information to work properly.

### Steps to Get Session Information:

1. Open Instagram in your browser and log in
2. Press `F12` to open Developer Tools
3. Switch to the `Network` tab
4. Click on any post to trigger an API request
5. Find the following in `Request Headers`:
   - `sessionid` from `Cookie`
   - `csrftoken` from `Cookie`
   - `x-ig-www-claim` (optional)

### How to Login

Run the program and select `4. Login`, then enter the information as prompted.

Once logged in successfully, the session will be automatically saved to `sessions/instagram_session.json` and will be loaded automatically on the next run.

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
CONFIG = {
    # Maximum posts per hashtag
    "max_posts_per_hashtag": 50,
    
    # Maximum comments per post
    "max_comments_per_post": 100,
    
    # Request delay (seconds) to avoid rate limiting
    "request_delay": 2,
    
    # Output directory
    "output_dir": "output",
    
    # Save as Excel
    "save_excel": True,
    
    # Save as JSON
    "save_json": False,
    
    # Save raw media JSON data
    "save_raw_json": False,
    
    # Request timeout (seconds)
    "timeout": 30,
}
```

## 📂 Output Files

All output files are saved in the `output/` directory.

### Hashtag User Data (Excel)

| Field | Description |
|-------|-------------|
| username | Username |
| full_name | Full name |
| pk | Post ID |
| like_count | Number of likes |
| comment_count | Number of comments |
| location_name | Location name |
| location_address | Location address |
| location_city | City |
| text | Post content |
| text_translation | Translated content |

### Comment User Data (Excel)

| Field | Description |
|-------|-------------|
| level | Level indicator (└─ for child comments) |
| username | Username |
| full_name | Full name |
| text | Comment content |
| comment_like_count | Comment likes |
| child_comment_count | Number of child comments |
| pk | Comment ID |
| media_id | Post ID |

## 📁 Project Structure

```
deepco_ig_spider/
├── main.py              # Main entry point
├── ig_spider.py         # Core spider module
├── config.py            # Configuration file
├── requirements.txt     # Dependencies
├── sessions/            # Session storage directory
│   └── instagram_session.json
├── output/              # Output files directory
├── README.md            # Chinese documentation
└── README_EN.md         # English documentation
```

## ⚠️ Important Notes

1. **Network Requirements** - Must be able to access Instagram (VPN may be required)
2. **Request Frequency** - Avoid frequent requests, keep the default request delay
3. **Account Security** - Do not use in untrusted environments
4. **Compliance** - Please comply with Instagram's Terms of Service, use only for legitimate purposes

## 📄 License

MIT License

