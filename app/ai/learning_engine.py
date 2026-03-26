from datetime import datetime, timedelta
from app.analytics.database import DatabaseManager
from app.utils.logger import setup_logger

logger = setup_logger('learning_engine')

class LearningEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def recalculate_weights(self):
        """Recalculate engagement weights based on historical performance."""
        logger.info("Recalculating engagement weights...")
        
        # Get all actions from the last 30 days
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT action_type, AVG(result_score) as avg_score, COUNT(*) as frequency
                FROM actions
                WHERE timestamp >= date('now', '-30 days')
                GROUP BY action_type
            ''')
            results = cursor.fetchall()
            
        if not results:
            logger.info("Not enough data to recalculate weights.")
            return

        # Update weights in the database
        for action_type, avg_score, frequency in results:
            # Simple formula: weight = avg_score * (1 + log(frequency))
            # This balances performance and statistical significance
            import math
            new_weight = avg_score * (1 + math.log10(frequency))
            
            # Normalize weight to a reasonable range (e.g., 1-10)
            new_weight = max(1.0, min(10.0, new_weight))
            
            self.db.update_engagement_weight(action_type, new_weight)
            logger.info(f"Updated weight for {action_type}: {new_weight:.2f}")

    def get_prioritized_actions(self):
        """Return actions sorted by their current weights."""
        weights = self.db.get_engagement_weights()
        # Sort by weight descending
        sorted_actions = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return [action[0] for action in sorted_actions]

    def optimize_routine(self):
        """Self-optimization: reduce actions with low efficacy."""
        logger.info("Optimizing routine...")
        weights = self.db.get_engagement_weights()
        
        # Identify low-performing actions (e.g., weight < 1.5)
        low_performing = [action for action, weight in weights.items() if weight < 1.5]
        
        if low_performing:
            logger.info(f"Low-performing actions identified: {low_performing}")
            # In a real scenario, we might reduce their frequency in the adaptive routine engine
        else:
            logger.info("No low-performing actions identified.")
            
    def estimate_result_score(self, action_type):
        """Estimate the result score for an action based on its type."""
        # Default scores if no data is available
        default_scores = {
            'jobs_view': 2.0,
            'profile_visit': 4.0,
            'post_like': 1.0,
            'company_follow': 3.0,
            'recruiter_visit': 5.0
        }
        return default_scores.get(action_type, 1.0)
