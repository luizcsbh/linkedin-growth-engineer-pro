import asyncio
from app.automation.routine_engine import AdaptiveRoutineEngine
from app.analytics.database import DatabaseManager
from app.ai.learning_engine import LearningEngine

async def test():
    db = DatabaseManager()
    ai = LearningEngine(db)
    engine = AdaptiveRoutineEngine(db, ai)
    await engine.run_daily_routine()

if __name__ == "__main__":
    asyncio.run(test())
