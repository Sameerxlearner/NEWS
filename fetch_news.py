"""
News fetching module for CryptoGoldAlertBot
Fetches and parses RSS feeds from various news sources
"""

import logging
import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class NewsFetcher:
    """Handles fetching news from RSS feeds"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoGoldAlertBot/1.0'
        })
    
    def fetch_feed(self, url: str, retries: int = 3) -> Optional[Dict]:
        """Fetch a single RSS feed with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching feed: {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url, 
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                # Parse the RSS feed
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {url}: {feed.bozo_exception}")
                
                return feed
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                break
        
        return None
    
    def parse_articles(self, feed: Dict, category: str) -> List[Dict]:
        """Parse articles from a feed"""
        articles = []
        
        if not feed or not hasattr(feed, 'entries'):
            return articles
        
        for entry in feed.entries[:self.config.MAX_ARTICLES_PER_FETCH]:
            try:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Skip articles older than 6 hours for real-time news
                if pub_date and (datetime.now() - pub_date) > timedelta(hours=6):
                    continue
                
                article = {
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '').strip(),
                    'published': pub_date,
                    'category': category,
                    'source': getattr(feed, 'feed', {}).get('title', 'Unknown')
                }
                
                # Skip articles without title or link
                if not article['title'] or not article['link']:
                    continue
                
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error parsing article: {e}")
                continue
        
        return articles
    
    def fetch_crypto_news(self) -> List[Dict]:
        """Fetch cryptocurrency news"""
        logger.info("Fetching cryptocurrency news...")
        all_articles = []
        
        for feed_url in self.config.RSS_FEEDS['crypto']:
            feed = self.fetch_feed(feed_url)
            if feed:
                articles = self.parse_articles(feed, 'crypto')
                all_articles.extend(articles)
                logger.info(f"Fetched {len(articles)} crypto articles from {feed_url}")
        
        return all_articles
    
    def fetch_gold_news(self) -> List[Dict]:
        """Fetch gold market news"""
        logger.info("Fetching gold market news...")
        all_articles = []
        
        for feed_url in self.config.RSS_FEEDS['gold']:
            feed = self.fetch_feed(feed_url)
            if feed:
                articles = self.parse_articles(feed, 'gold')
                all_articles.extend(articles)
                logger.info(f"Fetched {len(articles)} gold articles from {feed_url}")
        
        return all_articles
    
    def fetch_all_news(self) -> List[Dict]:
        """Fetch all news (crypto and gold)"""
        logger.info("Starting news fetch cycle...")
        
        all_articles = []
        
        # Fetch crypto news
        try:
            crypto_articles = self.fetch_crypto_news()
            all_articles.extend(crypto_articles)
        except Exception as e:
            logger.error(f"Error fetching crypto news: {e}")
        
        # Fetch gold news
        try:
            gold_articles = self.fetch_gold_news()
            all_articles.extend(gold_articles)
        except Exception as e:
            logger.error(f"Error fetching gold news: {e}")
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
