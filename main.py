from instagram_bot import InstagramBot
import time
import logging

def main():
    print("🤖 Starting Instagram Bot...")
    
    # Initialize bot
    bot = InstagramBot()
    
    # Test login first
    print("🔐 Attempting to login...")
    if bot.login():
        print("✅ Login successful!")
        
        # Run one cycle immediately for testing
        print("🚀 Running initial operations...")
        bot.daily_operations()
        
        # Start scheduler for continuous operation
        print("⏰ Starting 24/7 scheduler...")
        print("Bot will run daily at:", bot.config.OPERATION_HOURS)
        bot.run_scheduler()
    else:
        print("❌ Login failed. Please check:")
        print("   - Your Instagram credentials in .env file")
        print("   - Internet connection")
        print("   - If 2FA is enabled, temporarily disable it")
        logging.error("Login failed - check credentials and connection")

if __name__ == "__main__":
    main()
