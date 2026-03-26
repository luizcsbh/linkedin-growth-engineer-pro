from app.core.config import Config
from app.utils.logger import setup_logger

logger = setup_logger('safe_rules')

class SafeAutomationRules:
    def __init__(self):
        self.max_actions_per_day = Config.MAX_ACTIONS_PER_DAY
        self.max_likes = Config.MAX_LIKES
        self.max_profile_visits = Config.MAX_PROFILE_VISITS
        
        # Current session tracking
        self.daily_actions = 0
        self.daily_likes = 0
        self.daily_profile_visits = 0

    def can_perform_action(self, action_type):
        """Check if an action can be performed based on daily limits."""
        if self.daily_actions >= self.max_actions_per_day:
            logger.warning("Daily action limit reached.")
            return False
            
        if action_type == 'like' and self.daily_likes >= self.max_likes:
            logger.warning("Daily like limit reached.")
            return False
            
        if action_type == 'profile_visit' and self.daily_profile_visits >= self.max_profile_visits:
            logger.warning("Daily profile visit limit reached.")
            return False
            
        return True

    def record_action(self, action_type):
        """Record an action and increment counters."""
        self.daily_actions += 1
        if action_type == 'like':
            self.daily_likes += 1
        elif action_type == 'profile_visit':
            self.daily_profile_visits += 1
        
        logger.info(f"Action recorded: {action_type}. Total daily actions: {self.daily_actions}")

    def apply_cooldown(self, action_type):
        """Apply a cooldown after an action."""
        import time
        import random
        
        cooldown_time = random.uniform(10, 30)
        if action_type in ['like', 'profile_visit']:
            cooldown_time = random.uniform(30, 60)
            
        logger.info(f"Applying cooldown of {cooldown_time:.2f} seconds after {action_type}...")
        time.sleep(cooldown_time)
