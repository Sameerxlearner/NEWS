"""
Scheduler module for CryptoGoldAlertBot
Handles automated news fetching and alert scheduling
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit
import signal
import sys
import os

from fetch_news import NewsFetcher
from filter import NewsFilter

logger = logging.getLogger(__name__)

class NewsScheduler:
    """Handles scheduling of news fetching and alerts"""
    
    def __init__(self, telegram_bot, config):
        self.telegram_bot = telegram_bot
        self.config = config
        self.scheduler = BlockingScheduler()
        self.news_fetcher = NewsFetcher(config)
        self.news_filter = NewsFilter(config)
        
        # Setup scheduler
        self.setup_jobs()
        
        # Handle graceful shutdown
        atexit.register(self.shutdown)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Main news fetching job with error handling
        self.scheduler.add_job(
            func=self.fetch_and_send_news,
            trigger=IntervalTrigger(minutes=self.config.FETCH_INTERVAL_MINUTES),
            id='news_fetch_job',
            name='Fetch and send news alerts',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=60,  # Allow 60 seconds grace time
            coalesce=True  # Combine multiple missed runs into one
        )
        
        # Daily status update
        self.scheduler.add_job(
            func=self.send_daily_status,
            trigger=CronTrigger(hour=9, minute=0),  # 9:00 AM daily
            id='daily_status_job',
            name='Send daily status update',
            replace_existing=True
        )
        
        # Weekly cleanup job
        self.scheduler.add_job(
            func=self.cleanup_old_data,
            trigger=CronTrigger(day_of_week=0, hour=2, minute=0),  # Sunday 2:00 AM
            id='weekly_cleanup_job',
            name='Weekly data cleanup',
            replace_existing=True
        )
        
        logger.info("Scheduled jobs configured:")
        logger.info(f"- News alerts every {self.config.FETCH_INTERVAL_MINUTES} minutes")
        logger.info("- Daily status at 9:00 AM")
        logger.info("- Weekly cleanup on Sundays at 2:00 AM")
    
    def fetch_and_send_news(self):
        """Main job function: fetch news and send alerts with 24/7 reliability"""
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                logger.info("Starting scheduled news fetch and alert cycle...")
                
                # Fetch all news
                articles = self.news_fetcher.fetch_all_news()
                
                if not articles:
                    logger.info("No articles fetched")
                    return
                
                # Filter relevant articles
                filtered_articles = self.news_filter.filter_articles(articles)
                
                if not filtered_articles:
                    logger.info("No relevant articles found after filtering")
                    return
                
                # Send alerts and mark successful ones as sent
                sent_count = 0
                for article in filtered_articles:
                    try:
                        message = self.telegram_bot.format_article_message(article, self.config.DEFAULT_LANGUAGE)
                        
                        if self.telegram_bot.send_message(message):
                            sent_count += 1
                            self.news_filter.mark_as_sent(article['title'])
                            logger.info(f"Sent alert: {article['title'][:50]}...")
                            
                            # Delay between messages
                            import time
                            time.sleep(1)
                        else:
                            logger.error(f"Failed to send alert: {article['title'][:50]}...")
                            
                    except Exception as e:
                        logger.error(f"Error sending article alert: {e}")
                
                logger.info(f"News cycle completed: {sent_count} messages sent")
                
                # Update activity timestamp for monitoring
                try:
                    activity_file = "data/last_activity.txt"
                    os.makedirs(os.path.dirname(activity_file), exist_ok=True)
                    with open(activity_file, 'w') as f:
                        f.write(datetime.now().isoformat())
                except Exception as e:
                    logger.error(f"Error updating activity timestamp: {e}")
                break  # Success, exit retry loop
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error in news fetch cycle (attempt {retry_count}): {e}")
                
                if retry_count <= max_retries:
                    import time
                    time.sleep(10)  # Wait before retry
                    continue
                else:
                    # Send error notification after all retries failed
                    try:
                        error_msg = f"News fetch failed after {max_retries + 1} attempts: {str(e)[:100]}"
                        self.telegram_bot.send_error_notification(
                            error_msg, 
                            self.config.DEFAULT_LANGUAGE
                        )
                    except:
                        pass  # Don't let error notification failures crash the main process
    
    def send_daily_status(self):
        """Send daily status update"""
        try:
            from utils import get_translation
            
            status_msg = get_translation('daily_status', self.config.DEFAULT_LANGUAGE)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"""
{status_msg}
⏰ {current_time}
🔄 {get_translation('fetch_interval', self.config.DEFAULT_LANGUAGE)}: {self.config.FETCH_INTERVAL_MINUTES} {get_translation('minutes', self.config.DEFAULT_LANGUAGE)}
📰 {get_translation('max_articles', self.config.DEFAULT_LANGUAGE)}: {self.config.MAX_ARTICLES_PER_FETCH}
🗣️ {get_translation('language', self.config.DEFAULT_LANGUAGE)}: {self.config.DEFAULT_LANGUAGE.upper()}
            """.strip()
            
            self.telegram_bot.send_status_update(message, self.config.DEFAULT_LANGUAGE)
            
        except Exception as e:
            logger.error(f"Error sending daily status: {e}")
    
    def cleanup_old_data(self):
        """Clean up old data files"""
        try:
            logger.info("Performing weekly data cleanup...")
            
            # Clean up sent headlines (keep only recent ones)
            self.news_filter.sent_headlines = self.news_filter.sent_headlines[-self.config.MAX_STORED_HEADLINES:]
            self.news_filter.save_sent_headlines()
            
            # Log cleanup completion
            logger.info("Weekly cleanup completed")
            
            # Send cleanup notification
            from utils import get_translation
            cleanup_msg = get_translation('cleanup_completed', self.config.DEFAULT_LANGUAGE)
            self.telegram_bot.send_status_update(cleanup_msg, self.config.DEFAULT_LANGUAGE)
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def _update_activity_timestamp(self):
        """Update activity timestamp for monitoring"""
        try:
            activity_file = "data/last_activity.txt"
            os.makedirs(os.path.dirname(activity_file), exist_ok=True)
            with open(activity_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"Error updating activity timestamp: {e}")

    def shutdown(self):
        """Shutdown the scheduler gracefully"""
        try:
            if self.scheduler.running:
                logger.info("Shutting down scheduler...")
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler shutdown complete")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            logger.info("Starting news scheduler...")
            
            # Run initial fetch
            logger.info("Running initial news fetch...")
            self.fetch_and_send_news()
            
            # Start the scheduler
            logger.info("Starting scheduled jobs...")
            self.scheduler.start()
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            raise
