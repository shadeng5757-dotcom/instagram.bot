import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Instagram credentials
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')
    
    # Bot settings - CHANGE THESE TO YOUR TARGET ACCOUNTS
    TARGET_ACCOUNTS = [
        "instagram", "tech", "programming", 
        "python", "developer", "coding"
    ]
    
    # Limits - START WITH LOW NUMBERS FOR SAFETY
    DAILY_FOLLOW_LIMIT = 10
    DAILY_UNFOLLOW_LIMIT = 8
    STORY_REPLY_LIMIT = 5
    COMMENT_LIMIT = 3
    
    # Timing (24-hour format)
    OPERATION_HOURS = [9, 14, 18]  # 9AM, 2PM, 6PM
    CHECK_INTERVAL_MINUTES = 60
    
    # Story responses
    STORY_RESPONSES = [
        "Great story! 👏",
        "Amazing content! 💫",
        "Love this! ❤️",
        "So inspiring! ✨",
        "Awesome! 😍",
        "Nice! 👍",
        "Cool story! 😎",
        "Well done! 🙌"
    ]
    
    # DM auto-responses
    AUTO_RESPONSES = {
        "hello": "Hi there! Thanks for messaging! 😊",
        "hi": "Hello! How can I help you? 👋",
        "hey": "Hey! What's up? 😄",
        "price": "Please check our website for pricing details! 💰",
        "help": "I'm here to help! What do you need assistance with? 🤗",
        "thanks": "You're welcome! Have a great day! 🌟",
        "thank you": "You're welcome! Feel free to ask anything! 😄",
        "how are you": "I'm doing great! Thanks for asking! 😊",
        "what's up": "Just here managing the account! How about you? 😄"
    }
    
    # Comment templates
    COMMENT_TEMPLATES = [
        "Great post! 👏",
        "Amazing content! 💫",
        "Love this! ❤️",
        "So inspiring! ✨",
        "Awesome work! 😍",
        "Nice post! 👍",
        "Cool content! 😎",
        "Well done! 🙌"
    ]
