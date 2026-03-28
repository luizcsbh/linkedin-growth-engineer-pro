import random
import asyncio
from datetime import datetime
from app.automation.linkedin_client import LinkedInAutomation
from app.core.safe_rules import SafeAutomationRules
from app.analytics.database import DatabaseManager
from app.analytics.ssi_estimator import SSIEstimator
from app.ai.learning_engine import LearningEngine
from app.utils.logger import setup_logger

logger = setup_logger('routine_engine')

class AdaptiveRoutineEngine:
    def __init__(self, db_manager: DatabaseManager, learning_engine: LearningEngine):
        self.db = db_manager
        self.learning_engine = learning_engine
        self.safe_rules = SafeAutomationRules()
        self.ssi_estimator = SSIEstimator(db_manager)
        self.client = LinkedInAutomation(self.safe_rules, db_manager=self.db)

    async def run_daily_routine(self):
        """Run the daily routine with an adaptive plan."""
        start_time = datetime.now()
        logger.info(f"Starting daily routine at {start_time}...")
        
        # 1. Start browser and login
        await self.client.start()
        if not await self.client.login():
            await self.client.stop()
            return

        # 2. Choose a plan
        plan_type = random.choice(['A', 'B', 'C'])
        logger.info(f"Executing Plan {plan_type}...")
        
        try:
            all_actions = []
            if plan_type == 'A':
                # Plan A: feed → jobs → recruiters
                all_actions.extend(await self.client.interact_with_feed())
                all_actions.extend(await self.client.search_jobs())
                all_actions.extend(await self.client.visit_recruiters())
            elif plan_type == 'B':
                # Plan B: companies → feed → jobs
                # Note: follow_companies still returns count for now, could be updated later
                await self.client.follow_companies() 
                all_actions.extend(await self.client.interact_with_feed())
                all_actions.extend(await self.client.search_jobs())
            elif plan_type == 'C':
                # Plan C: recruiters → feed
                all_actions.extend(await self.client.visit_recruiters())
                all_actions.extend(await self.client.interact_with_feed())
                
            # 3. Log execution and update metrics
            duration = (datetime.now() - start_time).total_seconds()
            execution_id = self.db.log_execution(duration, "SUCCESS")
            
            # 4. Record detailed actions in DB
            for action in all_actions:
                score = self.learning_engine.estimate_result_score(action['type'])
                self.db.log_action(
                    execution_id, 
                    action['type'], 
                    score, 
                    detail_url=action.get('url'), 
                    detail_title=action.get('title'),
                    is_php_relevant=action.get('is_php', 0)
                )
            
            # 5. Update SSI and Growth Score
            self.ssi_estimator.calculate_daily_ssi()
            
            logger.info("Daily routine completed successfully.")
            
        except Exception as e:
            logger.error(f"Error during daily routine: {e}")
            self.db.log_execution((datetime.now() - start_time).total_seconds(), f"FAILED: {e}")
        finally:
            await self.client.stop()

    # _log_actions_to_db is now integrated into run_daily_routine for detailed logging
