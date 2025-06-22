#!/usr/bin/env python3
"""
Debug script to see what articles are being fetched and why they're not passing filters
"""

from fetch_news import NewsFetcher
from filter import NewsFilter
from config import Config

def debug_news_flow():
    config = Config()
    fetcher = NewsFetcher(config)
    news_filter = NewsFilter(config)
    
    print("=== Fetching Articles ===")
    articles = fetcher.fetch_all_news()
    print(f"Total articles fetched: {len(articles)}")
    
    print("\n=== Sample Articles ===")
    for i, article in enumerate(articles[:5]):
        print(f"\nArticle {i+1}:")
        print(f"Title: {article['title']}")
        print(f"Category: {article['category']}")
        print(f"Summary: {article.get('summary', 'No summary')[:100]}...")
        
        # Check keywords manually
        title_and_summary = f"{article.get('title', '')} {article.get('summary', '')}"
        if article['category'] == 'crypto':
            keywords = config.CRYPTO_KEYWORDS
        else:
            keywords = config.GOLD_KEYWORDS
            
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in title_and_summary.lower():
                found_keywords.append(keyword)
        
        print(f"Found keywords: {found_keywords}")
        
        # Calculate relevance
        relevance = news_filter.calculate_relevance_score(article)
        print(f"Relevance score: {relevance}")
    
    print("\n=== Filtering Results ===")
    filtered = news_filter.filter_articles(articles)
    print(f"Articles after filtering: {len(filtered)}")
    
    for article in filtered:
        print(f"\nFiltered Article:")
        print(f"Title: {article['title']}")
        print(f"Score: {article.get('relevance_score', 0)}")

if __name__ == "__main__":
    debug_news_flow()