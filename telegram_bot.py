"""
Telegram bot module for CryptoGoldAlertBot
Handles Telegram bot operations and message formatting
"""

import logging
import requests
import re
from typing import List, Dict
from utils import get_translation, format_message
import time

logger = logging.getLogger(__name__)

class TelegramBot:
    """Handles Telegram bot operations"""
    
    def __init__(self, config):
        self.config = config
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send a message using Telegram HTTP API"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def format_article_message(self, article: Dict, language: str = 'en') -> str:
        """Format a single article for Telegram"""
        try:
            # Get category emoji
            category_emojis = {
                'crypto': '🪙',
                'gold': '🏆'
            }
            
            emoji = category_emojis.get(article['category'], '📰')
            
            # Format the message
            title = article.get('title', 'No Title').strip()
            source = article.get('source', 'Unknown Source').strip()
            link = article.get('link', '').strip()
            published = article.get('published')
            
            # Clean title of problematic characters that cause 400 errors
            title = re.sub(r'[^\w\s\-\.\,\!\?\:\;]', '', title)
            title = title.replace('\n', ' ').replace('\r', ' ')
            title = ' '.join(title.split())  # Remove extra spaces
            
            # Format timestamp
            timestamp = ""
            if published:
                from utils import format_datetime
                timestamp = f"🕐 {format_datetime(published, language)}\n"
            
            # Create formatted message with better structure
            message = f"{emoji} <b>{title}</b>\n\n"
            
            # Add timestamp
            if timestamp:
                message += timestamp
            
            # Add full article content
            if article.get('summary'):
                summary = article['summary'].strip()
                # Clean summary but keep more content
                summary = re.sub(r'<[^>]+>', '', summary)  # Remove HTML tags
                summary = summary.replace('\n', ' ').replace('\r', ' ')
                summary = ' '.join(summary.split())  # Remove extra spaces
                
                # Allow longer summaries for full article content
                if len(summary) > 500:
                    summary = summary[:497] + "..."
                message += f"📰 {summary}\n\n"
            
            # Add source info
            message += f"📰 {source}"
            
            # Add link if available
            if link:
                message += f" | <a href='{link}'>Read More</a>"
            
            # Ensure message isn't too long
            if len(message) > 4000:
                message = message[:3997] + "..."
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting article message: {e}")
            # Return simple fallback message
            title = str(article.get('title', 'News Update'))[:100]
            return f"📰 {title}"
    
    def send_news_alerts(self, articles: List[Dict], language: str = 'en') -> int:
        """Send news alerts for multiple articles"""
        if not articles:
            logger.info("No articles to send")
            return 0
        
        sent_count = 0
        
        # Send header message
        header = get_translation('news_alert_header', language)
        category_counts = {}
        
        for article in articles:
            category = article['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        summary_parts = []
        for category, count in category_counts.items():
            category_name = get_translation(category, language)
            summary_parts.append(f"{category_name}: {count}")
        
        header_message = f"🚨 {header}\n📊 {' | '.join(summary_parts)}\n" + "─" * 30
        
        if self.send_message(header_message):
            sent_count += 1
        
        # Send individual articles
        for article in articles:
            try:
                message = self.format_article_message(article, language)
                
                if self.send_message(message):
                    sent_count += 1
                    logger.info(f"Sent alert: {article['title'][:50]}...")
                else:
                    logger.error(f"Failed to send alert: {article['title'][:50]}...")
                
                # Small delay between messages to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error sending article alert: {e}")
        
        return sent_count
    
    def send_error_notification(self, error_message: str, language: str = 'en'):
        """Send error notification to admin"""
        try:
            error_header = get_translation('error_notification', language)
            message = f"⚠️ {error_header}\n\n🔧 {error_message}"
            self.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def send_status_update(self, status_message: str, language: str = 'en'):
        """Send status update"""
        try:
            status_header = get_translation('status_update', language)
            message = f"ℹ️ {status_header}\n\n{status_message}"
            self.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
    
    def start(self):
        """Start the bot (placeholder for future webhook implementation)"""
        logger.info("Telegram bot initialized and ready")
        
        # Send startup notification
        startup_message = get_translation('bot_started', self.config.DEFAULT_LANGUAGE)
        self.send_status_update(startup_message)