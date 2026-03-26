import time
import random
import numpy as np
from app.utils.logger import setup_logger

logger = setup_logger('human_simulator')

class HumanSimulator:
    @staticmethod
    def wait(min_seconds=2, max_seconds=5):
        """Gaussian delay between actions."""
        delay = np.random.normal((min_seconds + max_seconds) / 2, (max_seconds - min_seconds) / 4)
        delay = max(min_seconds, min(max_seconds, delay))
        logger.debug(f"Waiting for {delay:.2f} seconds...")
        time.sleep(delay)

    @staticmethod
    async def human_scroll(page):
        """Irregular scroll behavior."""
        logger.debug("Simulating human scroll...")
        total_height = await page.evaluate("document.body.scrollHeight")
        current_scroll = 0
        
        while current_scroll < total_height:
            scroll_step = random.randint(200, 600)
            current_scroll += scroll_step
            await page.evaluate(f"window.scrollTo(0, {current_scroll})")
            HumanSimulator.wait(0.5, 1.5)
            
            # Random pause during scroll
            if random.random() < 0.2:
                HumanSimulator.wait(2, 4)
            
            # Update total height in case of lazy loading
            total_height = await page.evaluate("document.body.scrollHeight")

    @staticmethod
    def random_pause():
        """Simulate a natural pause (e.g., reading or thinking)."""
        if random.random() < 0.3:
            pause_time = random.uniform(5, 15)
            logger.info(f"Taking a natural pause for {pause_time:.2f} seconds...")
            time.sleep(pause_time)

    @staticmethod
    def idle_simulation():
        """Simulate idle time."""
        if random.random() < 0.1:
            idle_time = random.uniform(30, 60)
            logger.info(f"Simulating idle time for {idle_time:.2f} seconds...")
            time.sleep(idle_time)
