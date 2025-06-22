# CryptoGoldAlertBot

A Python Telegram bot that fetches real-time cryptocurrency and gold market news alerts with multi-language support.

## Features

- Real-time news from CoinDesk, Cointelegraph, Decrypt, and Mining.com
- Smart keyword filtering for relevant market news
- Duplicate detection to prevent repeated alerts
- Multi-language support (English and Hindi)
- Scheduled alerts every 2-5 minutes
- 24/7 monitoring with automatic restart
- Rich message formatting with timestamps and summaries

## Deployment on Render (Free)

### Step 1: Prepare Your Repository

1. Download all the project files from this Replit
2. Create a new GitHub repository
3. Upload all files to your GitHub repository

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the deployment:
   - **Name**: cryptogoldalertbot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r render-requirements.txt`
   - **Start Command**: `python main.py`

### Step 3: Set Environment Variables

In Render dashboard, go to Environment and add:

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Your chat/channel ID
- `DEFAULT_LANGUAGE`: en (or hi for Hindi)
- `FETCH_INTERVAL_MINUTES`: 5
- `MAX_ARTICLES_PER_FETCH`: 15

### Step 4: Deploy

Click "Create Web Service" and Render will automatically deploy your bot.

## Local Development

1. Install dependencies:
```bash
pip install -r render-requirements.txt
```

2. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

3. Run the bot:
```bash
python main.py
```

## Configuration

- News sources are automatically fetched from RSS feeds
- Keywords are pre-configured for crypto and gold market relevance
- Duplicate detection prevents repeated news
- Articles are filtered by recency (last 6 hours)

## Files Structure

- `main.py` - Main entry point with error handling
- `config.py` - Configuration and environment variables
- `fetch_news.py` - RSS feed fetching and parsing
- `filter.py` - News filtering and duplicate detection
- `telegram_bot.py` - Telegram message formatting and sending
- `scheduler.py` - Automated scheduling with APScheduler
- `utils.py` - Utility functions and translations
- `keepalive.py` - 24/7 monitoring and auto-restart

## Support

The bot includes comprehensive error handling, logging, and automatic recovery mechanisms for reliable 24/7 operation.