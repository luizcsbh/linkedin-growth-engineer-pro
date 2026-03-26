from datetime import datetime, timedelta
from app.analytics.database import DatabaseManager
from app.utils.logger import setup_logger

logger = setup_logger('ssi_estimator')

class SSIEstimator:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def calculate_daily_ssi(self, date_str=None):
        """Calculate SSI components for a specific date."""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        # 1. Professional Activity (based on job views and profile visits)
        activity_score = self._get_activity_score(date_str)
        
        # 2. Network Interaction (based on company follows and recruiter visits)
        network_score = self._get_network_score(date_str)
        
        # 3. Content Engagement (based on likes)
        content_score = self._get_content_score(date_str)
        
        # 4. Consistency (based on activity in the last 7 days)
        consistency_score = self._get_consistency_score(date_str)
        
        # Formula: (activity * 0.3) + (network * 0.3) + (content * 0.2) + (consistency * 0.2)
        ssi_score = (activity_score * 0.3) + (network_score * 0.3) + (content_score * 0.2) + (consistency_score * 0.2)
        
        # Normalize to 0-100
        ssi_score = min(100, max(0, ssi_score * 10))
        
        logger.info(f"SSI Score for {date_str}: {ssi_score:.2f}")
        
        # Calculate Growth Score (simplified version for now)
        growth_score = (ssi_score + consistency_score * 10) / 2
        
        # Update database
        activity_count = self._get_total_actions(date_str)
        self.db.update_daily_metrics(date_str, growth_score, ssi_score, consistency_score * 10, activity_count)
        
        return ssi_score

    def _get_activity_score(self, date_str):
        """Calculate activity score based on job views and profile visits."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM actions 
                WHERE date(timestamp) = ? AND action_type IN ('jobs_view', 'profile_visit')
            ''', (date_str,))
            count = cursor.fetchone()[0]
            return min(10, count)

    def _get_network_score(self, date_str):
        """Calculate network score based on company follows and recruiter visits."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM actions 
                WHERE date(timestamp) = ? AND action_type IN ('company_follow', 'recruiter_visit')
            ''', (date_str,))
            count = cursor.fetchone()[0]
            return min(10, count * 2)

    def _get_content_score(self, date_str):
        """Calculate content score based on likes."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM actions 
                WHERE date(timestamp) = ? AND action_type = 'post_like'
            ''', (date_str,))
            count = cursor.fetchone()[0]
            return min(10, count * 1.5)

    def _get_consistency_score(self, date_str):
        """Calculate consistency score based on activity in the last 7 days."""
        end_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = end_date - timedelta(days=6)
        
        active_days = 0
        current_date = start_date
        while current_date <= end_date:
            d_str = current_date.strftime('%Y-%m-%d')
            if self._get_total_actions(d_str) > 0:
                active_days += 1
            current_date += timedelta(days=1)
            
        return (active_days / 7) * 10

    def _get_total_actions(self, date_str):
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM actions WHERE date(timestamp) = ?', (date_str,))
            return cursor.fetchone()[0]
