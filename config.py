"""
Configuration module for CryptoGoldAlertBot
Handles environment variables and configuration settings
"""

import os
from typing import List, Dict

class Config:
    """Configuration class for the bot"""
    
    def __init__(self):
        # Telegram Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Language Configuration
        self.DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # 'en' or 'hi'
        
        # News Fetch Configuration
        self.FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "2"))
        self.MAX_ARTICLES_PER_FETCH = int(os.getenv("MAX_ARTICLES_PER_FETCH", "15"))
        
        # RSS Feed URLs
        self.RSS_FEEDS = {
            "crypto": [
                "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "https://cointelegraph.com/rss",
                "https://decrypt.co/feed"
            ],
            "gold": [
                "https://www.kitco.com/news/kitconews.rss",
                "https://www.mining.com/rss/",
                "https://www.goldprice.org/rss.xml"
            ]
        }
        
        # Filter Keywords - expanded for better matching
        self.CRYPTO_KEYWORDS = [
            "bitcoin", "ethereum", "binance", "etf", "crypto", "cryptocurrency",
            "altcoin", "market", "bull", "bear", "trading", "btc", "eth", 
            "blockchain", "defi", "nft", "coin", "digital", "mining",
            "wallet", "exchange", "price", "surge", "rally", "drop",
            "investment", "token", "decentralized", "web3"
        ]
        
        self.GOLD_KEYWORDS = [
            "gold", "precious", "metals", "bullion", "mining", "miners",
            "copper", "silver", "commodity", "resources", "exploration",
            "discovery", "reserves", "production", "output", "market",
            "price", "investment", "safe", "haven", "inflation"
        ]
        
        # Data Storage
        self.SENT_HEADLINES_FILE = "data/sent_headlines.json"
        self.MAX_STORED_HEADLINES = 50
        
        # API Configuration
        self.REQUEST_TIMEOUT = 30
        self.MAX_RETRIES = 3
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.SENT_HEADLINES_FILE), exist_ok=True)
