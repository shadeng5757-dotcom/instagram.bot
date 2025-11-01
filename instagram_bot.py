import os
import time
import random
import schedule
import json
from datetime import datetime, timedelta
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
import logging
from config import Config

class InstagramBot:
    def __init__(self):
        self.client = Client()
        self.config = Config()
        self.followed_users = self.load_followed_users()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_activity.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_followed_users(self):
        """Load followed users from file"""
        try:
            if os.path.exists('followed_users.json'):
                with open('followed_users.json', 'r') as f:
                    data = json.load(f)
                    # Convert string dates back to datetime objects
                    return {k: datetime.fromisoformat(v) for k, v in data.items()}
        except:
            pass
        return {}
    
    def save_followed_users(self):
        """Save followed users to file"""
        try:
            # Convert datetime objects to strings for JSON
            data = {k: v.isoformat() for k, v in self.followed_users.items()}
            with open('followed_users.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving followed users: {e}")
    
    def login(self):
        """Enhanced login with session handling"""
        try:
            # Try to load existing session
            if os.path.exists('session.json'):
                self.client.load_settings('session.json')
                self.client.login(self.config.INSTAGRAM_USERNAME, self.config.INSTAGRAM_PASSWORD)
                self.logger.info("Logged in using saved session")
            else:
                # New login
                self.client.login(self.config.INSTAGRAM_USERNAME, self.config.INSTAGRAM_PASSWORD)
                self.client.dump_settings('session.json')
                self.logger.info("Successfully logged in and saved session")
            
            # Verify login
            user_id = self.client.user_id
            self.logger.info(f"Logged in as user ID: {user_id}")
            return True
            
        except (LoginRequired, ChallengeRequired) as e:
            self.logger.error(f"Login required or challenge: {e}")
            return self.alternative_login()
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def alternative_login(self):
        """Alternative login method"""
        try:
            self.client.set_settings({
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            })
            self.client.login(self.config.INSTAGRAM_USERNAME, self.config.INSTAGRAM_PASSWORD)
            self.client.dump_settings('session.json')
            self.logger.info("Successfully logged in with alternative method")
            return True
        except Exception as e:
            self.logger.error(f"Alternative login also failed: {e}")
            return False
    
    def get_target_account_followers(self, account_username, count=50):
        """Get followers from target account"""
        try:
            user_id = self.client.user_id_from_username(account_username)
            followers = self.client.user_followers(user_id, amount=count)
            return list(followers.values())
        except Exception as e:
            self.logger.error(f"Error getting followers from {account_username}: {e}")
            return []
    
    def follow_users(self):
        """Follow users from target accounts - EXACTLY AS YOU REQUESTED"""
        try:
            # Randomly select target account
            target_account = random.choice(self.config.TARGET_ACCOUNTS)
            self.logger.info(f"Targeting followers from: {target_account}")
            
            followers = self.get_target_account_followers(target_account, self.config.DAILY_FOLLOW_LIMIT + 10)
            
            followed_count = 0
            for user in followers:
                if followed_count >= self.config.DAILY_FOLLOW_LIMIT:
                    break
                    
                try:
                    # Check if not already followed and not private
                    if not user.is_followed and not user.is_private:
                        self.client.user_follow(user.pk)
                        self.followed_users[user.pk] = datetime.now()
                        self.logger.info(f"Followed: {user.username} (from {target_account})")
                        followed_count += 1
                        
                        # Save after each follow
                        self.save_followed_users()
                        
                        # Random delay (30-90 seconds)
                        time.sleep(random.uniform(30, 90))
                        
                except Exception as e:
                    self.logger.error(f"Error following {user.username}: {e}")
                    continue
            
            self.logger.info(f"✅ Successfully followed {followed_count} users from {target_account}")
            
        except Exception as e:
            self.logger.error(f"Error in follow_users: {e}")
    
    def unfollow_non_followers(self):
        """Unfollow users who didn't follow back after 2 days - EXACTLY AS YOU REQUESTED"""
        try:
            current_time = datetime.now()
            to_unfollow = []
            
            for user_id, follow_time in self.followed_users.items():
                # Check if 2 days have passed
                if (current_time - follow_time) >= timedelta(days=2):
                    try:
                        # Check if they followed back
                        friendship = self.client.user_friendship(user_id)
                        if not friendship.followed_by:  # They didn't follow back
                            to_unfollow.append(user_id)
                    except Exception as e:
                        self.logger.error(f"Error checking friendship for {user_id}: {e}")
                        continue
            
            unfollowed_count = 0
            for user_id in to_unfollow:
                if unfollowed_count >= self.config.DAILY_UNFOLLOW_LIMIT:
                    break
                    
                try:
                    self.client.user_unfollow(user_id)
                    del self.followed_users[user_id]
                    self.logger.info(f"Unfollowed user ID: {user_id} (didn't follow back)")
                    unfollowed_count += 1
                    
                    # Save after each unfollow
                    self.save_followed_users()
                    
                    # Random delay (30-60 seconds)
                    time.sleep(random.uniform(30, 60))
                    
                except Exception as e:
                    self.logger.error(f"Error unfollowing {user_id}: {e}")
            
            self.logger.info(f"✅ Successfully unfollowed {unfollowed_count} users who didn't follow back")
            
        except Exception as e:
            self.logger.error(f"Error in unfollow_non_followers: {e}")
    
    def reply_to_stories(self):
        """Reply to followers' stories with your predefined messages"""
        try:
            stories = self.client.get_following_stories()
            replied_count = 0
            
            for user_stories in stories:
                for story in user_stories:
                    if replied_count >= self.config.STORY_REPLY_LIMIT:
                        break
                    
                    try:
                        response = random.choice(self.config.STORY_RESPONSES)
                        self.client.story_react(story.id, response)
                        self.logger.info(f"Replied to story: {response}")
                        replied_count += 1
                        
                        time.sleep(random.uniform(20, 40))
                        
                    except Exception as e:
                        self.logger.error(f"Error replying to story: {e}")
                        continue
            
            self.logger.info(f"✅ Replied to {replied_count} stories")
            
        except Exception as e:
            self.logger.error(f"Error in reply_to_stories: {e}")
    
    def handle_direct_messages(self):
        """Handle DMs with your predefined responses"""
        try:
            threads = self.client.get_threads(20)  # Get last 20 threads
            
            responded_count = 0
            for thread in threads:
                if thread.last_permanent_item and hasattr(thread.last_permanent_item, 'text'):
                    last_message = thread.last_permanent_item.text.lower()
                    
                    # Check for auto-response triggers
                    for trigger, response in self.config.AUTO_RESPONSES.items():
                        if trigger in last_message:
                            try:
                                self.client.direct_send(response, thread_ids=[thread.id])
                                self.logger.info(f"Sent DM response: {response}")
                                responded_count += 1
                                time.sleep(random.uniform(10, 20))
                                break
                            except Exception as e:
                                self.logger.error(f"Error sending DM response: {e}")
            
            self.logger.info(f"✅ Handled {responded_count} DM conversations")
            
        except Exception as e:
            self.logger.error(f"Error in handle_direct_messages: {e}")
    
    def comment_on_posts(self):
        """Comment on posts from target accounts"""
        try:
            target_account = random.choice(self.config.TARGET_ACCOUNTS)
            user_id = self.client.user_id_from_username(target_account)
            posts = self.client.user_medias(user_id, amount=5)
            
            commented_count = 0
            for post in posts:
                if commented_count >= self.config.COMMENT_LIMIT:
                    break
                
                try:
                    comment = random.choice(self.config.COMMENT_TEMPLATES)
                    self.client.media_comment(post.id, comment)
                    self.logger.info(f"Commented on {target_account}'s post: {comment}")
                    commented_count += 1
                    
                    time.sleep(random.uniform(60, 120))
                    
                except Exception as e:
                    self.logger.error(f"Error commenting on post: {e}")
                    continue
            
            self.logger.info(f"✅ Commented on {commented_count} posts from {target_account}")
            
        except Exception as e:
            self.logger.error(f"Error in comment_on_posts: {e}")
    
    def daily_operations(self):
        """Execute all daily operations"""
        self.logger.info("🟢 Starting daily operations")
        
        if not self.login():
            self.logger.error("🔴 Failed to login, skipping operations")
            return
        
        try:
            # Follow new users
            self.follow_users()
            time.sleep(random.uniform(300, 600))
            
            # Unfollow those who didn't follow back
            self.unfollow_non_followers()
            time.sleep(random.uniform(300, 600))
            
            # Reply to stories
            self.reply_to_stories()
            time.sleep(random.uniform(300, 600))
            
            # Handle DMs
            self.handle_direct_messages()
            time.sleep(random.uniform(300, 600))
            
            # Comment on posts
            self.comment_on_posts()
            
            self.logger.info("✅ Completed all daily operations successfully")
            
        except Exception as e:
            self.logger.error(f"🔴 Error during daily operations: {e}")
    
    def run_scheduler(self):
        """Run the scheduler for daily operations"""
        # Schedule daily operations at specified hours
        for hour in self.config.OPERATION_HOURS:
            schedule.every().day.at(f"{hour:02d}:00").do(self.daily_operations)
            self.logger.info(f"Scheduled daily operation at {hour:02d}:00")
        
        self.logger.info("⏰ Scheduler started - Bot is running 24/7")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(300)
