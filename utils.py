"""
Utility functions for CryptoGoldAlertBot
Includes translations, formatting helpers, and common utilities
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        'crypto': 'Cryptocurrency',
        'gold': 'Gold Market',
        'category': 'Category',
        'source': 'Source',
        'relevance': 'Relevance',
        'read_more': 'Read More',
        'news_alert_header': 'Latest Market News Alert',
        'error_notification': 'Bot Error Notification',
        'status_update': 'Bot Status Update',
        'bot_started': 'CryptoGoldAlertBot has started successfully! 🚀',
        'daily_status': 'Daily Status Report',
        'fetch_interval': 'Fetch Interval',
        'minutes': 'minutes',
        'max_articles': 'Max Articles per Fetch',
        'language': 'Language',
        'cleanup_completed': 'Weekly data cleanup completed successfully',
        'breaking_news': 'BREAKING NEWS',
        'market_update': 'Market Update',
        'price_alert': 'Price Alert'
    },
    'hi': {
        'crypto': 'क्रिप्टोकरेंसी',
        'gold': 'सोना बाजार',
        'category': 'श्रेणी',
        'source': 'स्रोत',
        'relevance': 'प्रासंगिकता',
        'read_more': 'और पढ़ें',
        'news_alert_header': 'नवीनतम बाजार समाचार अलर्ट',
        'error_notification': 'बॉट त्रुटि सूचना',
        'status_update': 'बॉट स्थिति अपडेट',
        'bot_started': 'CryptoGoldAlertBot सफलतापूर्वक शुरू हो गया है! 🚀',
        'daily_status': 'दैनिक स्थिति रिपोर्ट',
        'fetch_interval': 'फेच अंतराल',
        'minutes': 'मिनट',
        'max_articles': 'प्रति फेच अधिकतम लेख',
        'language': 'भाषा',
        'cleanup_completed': 'साप्ताहिक डेटा सफाई सफलतापूर्वक पूर्ण',
        'breaking_news': 'ब्रेकिंग न्यूज',
        'market_update': 'बाजार अपडेट',
        'price_alert': 'मूल्य अलर्ट'
    }
}

def get_translation(key: str, language: str = 'en') -> str:
    """Get translation for a given key and language"""
    try:
        if language in TRANSLATIONS and key in TRANSLATIONS[language]:
            return TRANSLATIONS[language][key]
        
        # Fallback to English
        if key in TRANSLATIONS['en']:
            return TRANSLATIONS['en'][key]
        
        # Fallback to key itself
        return key.replace('_', ' ').title()
        
    except Exception as e:
        logger.error(f"Translation error for key '{key}', language '{language}': {e}")
        return key.replace('_', ' ').title()

def format_message(text: str, max_length: int = 4096) -> str:
    """Format and truncate message for Telegram"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text

def clean_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    
    # Remove HTML tags but keep content
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text.strip())
    
    return clean_text

def format_datetime(dt: datetime, language: str = 'en') -> str:
    """Format datetime for display"""
    if not dt:
        return ""
    
    try:
        if language == 'hi':
            # Simple Hindi date format
            return dt.strftime("%d/%m/%Y %H:%M")
        else:
            # English date format
            return dt.strftime("%B %d, %Y at %H:%M")
    except Exception as e:
        logger.error(f"Error formatting datetime: {e}")
        return str(dt)

def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    if not url:
        return "Unknown"
    
    try:
        # Simple domain extraction
        if '://' in url:
            domain = url.split('://')[1].split('/')[0]
        else:
            domain = url.split('/')[0]
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()
        
    except Exception as e:
        logger.error(f"Error extracting domain from {url}: {e}")
        return "Unknown"

def is_market_hours() -> bool:
    """Check if it's during typical market hours (UTC)"""
    try:
        now = datetime.utcnow()
        hour = now.hour
        weekday = now.weekday()
        
        # Crypto markets are 24/7, but traditional markets are weekdays 9-17 UTC
        # We'll be more lenient and consider 6-22 UTC as active hours
        is_weekday = weekday < 5  # Monday to Friday
        is_active_hour = 6 <= hour <= 22
        
        return is_weekday and is_active_hour
        
    except Exception as e:
        logger.error(f"Error checking market hours: {e}")
        return True  # Default to True if can't determine

def calculate_sentiment_score(text: str) -> float:
    """Calculate basic sentiment score for text"""
    if not text:
        return 0.0
    
    try:
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            'up', 'rise', 'surge', 'gain', 'bull', 'rally', 'increase', 'high',
            'growth', 'profit', 'success', 'strong', 'positive', 'boost',
            'moon', 'pump', 'breakout', 'breakthrough'
        ]
        
        # Negative indicators
        negative_words = [
            'down', 'fall', 'crash', 'drop', 'bear', 'decline', 'decrease', 'low',
            'loss', 'fail', 'weak', 'negative', 'dump', 'collapse', 'plunge',
            'correction', 'selloff'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate score (-1 to 1)
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0
        
        score = (positive_count - negative_count) / max(total_words / 10, 1)
        return max(-1.0, min(1.0, score))  # Clamp between -1 and 1
        
    except Exception as e:
        logger.error(f"Error calculating sentiment: {e}")
        return 0.0

def format_number(number: float, language: str = 'en') -> str:
    """Format numbers for display"""
    try:
        if language == 'hi':
            # Indian number formatting (lakhs, crores)
            if number >= 10000000:  # 1 crore
                return f"₹{number/10000000:.2f} करोड़"
            elif number >= 100000:  # 1 lakh
                return f"₹{number/100000:.2f} लाख"
            else:
                return f"₹{number:,.2f}"
        else:
            # Western formatting
            if number >= 1000000000:  # Billion
                return f"${number/1000000000:.2f}B"
            elif number >= 1000000:  # Million
                return f"${number/1000000:.2f}M"
            elif number >= 1000:  # Thousand
                return f"${number/1000:.2f}K"
            else:
                return f"${number:,.2f}"
                
    except Exception as e:
        logger.error(f"Error formatting number {number}: {e}")
        return str(number)

def validate_config(config) -> List[str]:
    """Validate configuration and return list of errors"""
    errors = []
    
    try:
        # Check required fields
        if not config.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not config.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID is required")
        
        # Check numeric values
        if config.FETCH_INTERVAL_MINUTES < 1:
            errors.append("FETCH_INTERVAL_MINUTES must be at least 1")
        
        if config.MAX_ARTICLES_PER_FETCH < 1:
            errors.append("MAX_ARTICLES_PER_FETCH must be at least 1")
        
        # Check language
        if config.DEFAULT_LANGUAGE not in ['en', 'hi']:
            errors.append("DEFAULT_LANGUAGE must be 'en' or 'hi'")
        
        # Check RSS feeds
        if not config.RSS_FEEDS.get('crypto'):
            errors.append("At least one crypto RSS feed is required")
        
        if not config.RSS_FEEDS.get('gold'):
            errors.append("At least one gold RSS feed is required")
        
    except Exception as e:
        errors.append(f"Configuration validation error: {e}")
    
    return errors
