#!/usr/bin/env python3
"""
CryptoGoldAlertBot - Main Entry Point
A Telegram bot that sends real-time cryptocurrency and gold market news alerts
"""

import os
import sys
import logging
from telegram_bot import TelegramBot
from scheduler import NewsScheduler
from config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to start the bot with 24/7 reliability"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Initialize configuration
            config = Config()
            
            # Validate required environment variables
            if not config.TELEGRAM_BOT_TOKEN:
                logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
                sys.exit(1)
                
            if not config.TELEGRAM_CHAT_ID:
                logger.error("TELEGRAM_CHAT_ID environment variable is required")
                sys.exit(1)
            
            logger.info(f"Starting CryptoGoldAlertBot... (attempt {retry_count + 1})")
            
            # Initialize Telegram bot
            telegram_bot = TelegramBot(config)
            
            # Test connection first
            test_message = f"Bot starting - {retry_count + 1} attempt"
            if not telegram_bot.send_message(test_message):
                logger.warning("Initial Telegram connection test failed")
            
            # Initialize and start scheduler
            scheduler = NewsScheduler(telegram_bot, config)
            scheduler.start()
            
            # Start the Telegram bot
            telegram_bot.start()
            
            # If we reach here, break the retry loop
            break
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Fatal error (attempt {retry_count}): {e}")
            
            if retry_count < max_retries:
                import time
                wait_time = retry_count * 30  # Progressive backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("Max retries reached. Bot shutting down.")
                sys.exit(1)

if __name__ == "__main__":
    main()
