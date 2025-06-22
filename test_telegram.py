#!/usr/bin/env python3
"""
Test script to validate Telegram bot credentials and connection
"""

import os
import requests
import json

def test_telegram_bot():
    """Test Telegram bot configuration"""
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN is missing")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID is missing")
        return False
    
    print(f"✅ Token found: {token[:10]}...")
    print(f"✅ Chat ID found: {chat_id}")
    
    # Test bot info
    base_url = f"https://api.telegram.org/bot{token}"
    
    try:
        # Get bot info
        response = requests.get(f"{base_url}/getMe", timeout=10)
        print(f"\n📋 Bot Info Response: {response.status_code}")
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info['result']
                print(f"✅ Bot Name: {bot_data.get('first_name')}")
                print(f"✅ Bot Username: @{bot_data.get('username')}")
                print(f"✅ Bot ID: {bot_data.get('id')}")
            else:
                print(f"❌ Bot API Error: {bot_info.get('description')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False
    
    # Test sending a simple message
    try:
        test_message = "🤖 CryptoGoldAlertBot Test Message\n\nIf you can see this, the bot is working correctly!"
        
        data = {
            'chat_id': chat_id,
            'text': test_message,
            'disable_web_page_preview': True
        }
        
        response = requests.post(f"{base_url}/sendMessage", data=data, timeout=10)
        print(f"\n📤 Send Message Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Test message sent successfully!")
                return True
            else:
                print(f"❌ Telegram API Error: {result.get('description')}")
                print(f"Error Code: {result.get('error_code')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {error_data}")
            except:
                print(f"Response: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ Message Send Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Telegram Bot Configuration...\n")
    success = test_telegram_bot()
    
    if success:
        print("\n🎉 All tests passed! The bot is ready to send alerts.")
    else:
        print("\n❌ Tests failed. Please check your configuration:")
        print("1. Verify your TELEGRAM_BOT_TOKEN is correct")
        print("2. Make sure the bot has been started by sending /start to it")
        print("3. For group chats, add the bot to the group and make it an admin")
        print("4. Verify the TELEGRAM_CHAT_ID is correct")