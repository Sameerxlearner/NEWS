#!/usr/bin/env python3
"""
Keep-alive monitor for CryptoGoldAlertBot
Ensures the bot stays online 24/7 with health checks and automatic restarts
"""

import os
import sys
import time
import subprocess
import logging
import signal
import requests
from datetime import datetime, timedelta
from config import Config

class BotMonitor:
    """Monitors bot health and restarts if needed"""
    
    def __init__(self):
        self.config = Config()
        self.last_activity_file = "data/last_activity.txt"
        self.max_inactive_minutes = 10  # Restart if no activity for 10 minutes
        self.health_check_interval = 60  # Check every minute
        self.bot_process = None
        self.running = True
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - KeepAlive - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('keepalive.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Handle shutdown signals
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def check_telegram_connectivity(self):
        """Test if Telegram API is reachable"""
        try:
            base_url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}"
            response = requests.get(f"{base_url}/getMe", timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Telegram connectivity test failed: {e}")
            return False
    
    def check_bot_activity(self):
        """Check if bot has been active recently"""
        try:
            if not os.path.exists(self.last_activity_file):
                return False
            
            with open(self.last_activity_file, 'r') as f:
                last_activity_str = f.read().strip()
            
            last_activity = datetime.fromisoformat(last_activity_str)
            inactive_time = datetime.now() - last_activity
            
            return inactive_time.total_seconds() < (self.max_inactive_minutes * 60)
            
        except Exception as e:
            self.logger.error(f"Error checking bot activity: {e}")
            return False
    
    def update_activity_timestamp(self):
        """Update the last activity timestamp"""
        try:
            os.makedirs(os.path.dirname(self.last_activity_file), exist_ok=True)
            with open(self.last_activity_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            self.logger.error(f"Error updating activity timestamp: {e}")
    
    def start_bot(self):
        """Start the main bot process"""
        try:
            self.logger.info("Starting bot process...")
            self.bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.logger.info(f"Bot started with PID: {self.bot_process.pid}")
            self.update_activity_timestamp()
            return True
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if self.bot_process and self.bot_process.poll() is None:
            try:
                self.logger.info("Stopping bot process...")
                self.bot_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Bot didn't stop gracefully, forcing shutdown...")
                    self.bot_process.kill()
                    self.bot_process.wait()
                
                self.logger.info("Bot process stopped")
                return True
            except Exception as e:
                self.logger.error(f"Error stopping bot: {e}")
                return False
        return True
    
    def restart_bot(self):
        """Restart the bot process"""
        self.logger.info("Restarting bot...")
        self.stop_bot()
        time.sleep(5)  # Wait before restart
        return self.start_bot()
    
    def send_status_notification(self, message):
        """Send status notification via Telegram"""
        try:
            base_url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}"
            data = {
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': f"🤖 Bot Monitor: {message}",
                'disable_web_page_preview': True
            }
            response = requests.post(f"{base_url}/sendMessage", data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        consecutive_failures = 0
        last_connectivity_check = datetime.now()
        
        while self.running:
            try:
                # Check if bot process is running
                if not self.bot_process or self.bot_process.poll() is not None:
                    self.logger.warning("Bot process not running, starting...")
                    if self.start_bot():
                        consecutive_failures = 0
                        self.send_status_notification("Bot restarted successfully")
                    else:
                        consecutive_failures += 1
                
                # Check bot activity
                elif not self.check_bot_activity():
                    self.logger.warning("Bot appears inactive, restarting...")
                    if self.restart_bot():
                        consecutive_failures = 0
                        self.send_status_notification("Bot restarted due to inactivity")
                    else:
                        consecutive_failures += 1
                
                # Periodic connectivity check (every 5 minutes)
                if datetime.now() - last_connectivity_check > timedelta(minutes=5):
                    if not self.check_telegram_connectivity():
                        self.logger.warning("Telegram connectivity lost")
                        consecutive_failures += 1
                    else:
                        self.logger.info("Telegram connectivity OK")
                    last_connectivity_check = datetime.now()
                
                # Alert on consecutive failures
                if consecutive_failures >= 3:
                    error_msg = f"Bot has failed {consecutive_failures} times"
                    self.logger.error(error_msg)
                    self.send_status_notification(f"ALERT: {error_msg}")
                    consecutive_failures = 0  # Reset to avoid spam
                
                # Sleep before next check
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(30)  # Wait longer on errors
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        self.logger.info("Shutting down monitor...")
        self.running = False
        self.stop_bot()
        sys.exit(0)
    
    def start(self):
        """Start the monitoring system"""
        self.logger.info("Starting 24/7 bot monitor...")
        self.send_status_notification("24/7 monitoring started")
        
        # Start initial bot
        if not self.start_bot():
            self.logger.error("Failed to start initial bot process")
            return False
        
        # Start monitoring
        try:
            self.monitor_loop()
        except KeyboardInterrupt:
            self.logger.info("Monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Monitor crashed: {e}")
            self.send_status_notification(f"Monitor crashed: {e}")
        finally:
            self.shutdown()

if __name__ == "__main__":
    monitor = BotMonitor()
    monitor.start()