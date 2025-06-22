"""
News filtering module for CryptoGoldAlertBot
Filters news articles based on keywords and relevance
"""

import logging
import re
from typing import List, Dict
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsFilter:
    """Handles filtering of news articles"""
    
    def __init__(self, config):
        self.config = config
        self.sent_headlines = self.load_sent_headlines()
    
    def load_sent_headlines(self) -> List[str]:
        """Load previously sent headlines from file"""
        try:
            if os.path.exists(self.config.SENT_HEADLINES_FILE):
                with open(self.config.SENT_HEADLINES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('headlines', [])
        except Exception as e:
            logger.error(f"Error loading sent headlines: {e}")
        
        return []
    
    def save_sent_headlines(self):
        """Save sent headlines to file"""
        try:
            # Keep only the most recent headlines
            recent_headlines = self.sent_headlines[-self.config.MAX_STORED_HEADLINES:]
            
            data = {
                'headlines': recent_headlines,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config.SENT_HEADLINES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving sent headlines: {e}")
    
    def is_duplicate(self, title: str) -> bool:
        """Check if headline was already sent"""
        # Simple exact match only - be less aggressive about duplicates
        if title in self.sent_headlines:
            return True
        
        # Check for very similar titles (85% match)
        normalized_title = re.sub(r'[^\w\s]', '', title.lower()).strip()
        for sent_title in self.sent_headlines:
            normalized_sent = re.sub(r'[^\w\s]', '', sent_title.lower()).strip()
            if self.similarity_ratio(normalized_title, normalized_sent) > 0.85:
                return True
        
        return False
    
    def similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the specified keywords"""
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        
        return False
    
    def calculate_relevance_score(self, article: Dict) -> float:
        """Calculate relevance score for an article"""
        score = 0.0
        
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        combined_text = f"{title} {summary}"
        
        # Get appropriate keywords based on category
        if article['category'] == 'crypto':
            keywords = self.config.CRYPTO_KEYWORDS
        else:
            keywords = self.config.GOLD_KEYWORDS
        
        # Count keyword matches
        for keyword in keywords:
            keyword_lower = keyword.lower()
            title_matches = title.count(keyword_lower)
            summary_matches = summary.count(keyword_lower)
            
            # Title matches are weighted more heavily
            score += title_matches * 2.0
            score += summary_matches * 1.0
        
        # Boost score for important indicators
        important_terms = {
            'breaking': 3.0,
            'urgent': 3.0,
            'alert': 2.5,
            'crash': 2.5,
            'surge': 2.0,
            'rally': 2.0,
            'record': 2.0,
            'high': 1.5,
            'low': 1.5,
            'regulation': 2.0,
            'ban': 2.5,
            'approval': 2.0
        }
        
        for term, weight in important_terms.items():
            if term in combined_text:
                score += weight
        
        return score
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on keywords and relevance"""
        logger.info(f"Filtering {len(articles)} articles...")
        
        filtered_articles = []
        
        for article in articles:
            try:
                # Skip articles without title
                if not article.get('title'):
                    continue
                
                # Check for duplicates
                if self.is_duplicate(article['title']):
                    logger.debug(f"Skipping duplicate: {article['title'][:50]}...")
                    continue
                
                # Check for relevant keywords - temporarily more lenient
                title_and_summary = f"{article.get('title', '')} {article.get('summary', '')}"
                
                if article['category'] == 'crypto':
                    has_keywords = self.contains_keywords(title_and_summary, self.config.CRYPTO_KEYWORDS)
                    # For crypto, also accept if from crypto-specific sources
                    if not has_keywords and ('coindesk' in article.get('source', '').lower() or 
                                           'cointelegraph' in article.get('source', '').lower() or
                                           'decrypt' in article.get('source', '').lower()):
                        has_keywords = True
                else:
                    has_keywords = self.contains_keywords(title_and_summary, self.config.GOLD_KEYWORDS)
                    # For gold, also accept mining-related articles
                    if not has_keywords and 'mining' in article.get('source', '').lower():
                        has_keywords = True
                
                if not has_keywords:
                    continue
                
                # Calculate relevance score
                relevance_score = self.calculate_relevance_score(article)
                article['relevance_score'] = relevance_score
                
                # Include more articles by lowering threshold further
                if relevance_score >= 0.1:
                    filtered_articles.append(article)
                    logger.info(f"Included article: {article['title'][:50]}... (score: {relevance_score})")
            
            except Exception as e:
                logger.error(f"Error filtering article: {e}")
                continue
        
        # Sort by relevance score (highest first)
        filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Allow more articles to be sent
        max_articles = min(6, len(filtered_articles))
        filtered_articles = filtered_articles[:max_articles]
        
        logger.info(f"Filtered to {len(filtered_articles)} relevant articles")
        return filtered_articles
    
    def mark_as_sent(self, title: str):
        """Mark a headline as sent"""
        self.sent_headlines.append(title)
        self.save_sent_headlines()
