import asyncio
import schedule
import time
from datetime import datetime

from app.automation.routine_engine import AdaptiveRoutineEngine
from app.analytics.database import DatabaseManager
from app.ai.learning_engine import LearningEngine
from app.core.config import Config
from app.utils.logger import setup_logger

logger = setup_logger("main")

async def main_routine():
    db_manager = DatabaseManager()
    learning_engine = LearningEngine(db_manager)
    routine_engine = AdaptiveRoutineEngine(db_manager, learning_engine)
    
    logger.info("Running daily LinkedIn routine...")
    await routine_engine.run_daily_routine()
    
    # After routine, check for self-optimization
    last_optimization_date = db_manager.get_last_optimization_date() # Assuming this method exists
    if not last_optimization_date or \
       (datetime.now() - last_optimization_date).days >= Config.OPTIMIZATION_INTERVAL_DAYS:
        logger.info("Performing self-optimization...")
        learning_engine.recalculate_weights()
        learning_engine.optimize_routine()
        db_manager.update_last_optimization_date(datetime.now()) # Assuming this method exists

def run_main_routine():
    asyncio.run(main_routine())

if __name__ == "__main__":
    # Schedule the main routine to run daily
    schedule.every().day.at("09:00").do(run_main_routine)
    logger.info("Daily routine scheduled for 09:00 AM.")

    # Schedule the dashboard to run in a separate process/thread if needed
    # For simplicity, we'll assume the dashboard is run separately or via gunicorn

    while True:
        schedule.run_pending()
        time.sleep(1)
