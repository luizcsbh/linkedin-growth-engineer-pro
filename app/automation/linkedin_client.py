import asyncio
import random
from playwright.async_api import async_playwright
from app.core.config import Config
from app.core.human_simulator import HumanSimulator
from app.core.safe_rules import SafeAutomationRules
from app.utils.logger import setup_logger

logger = setup_logger('linkedin_client')

class LinkedInAutomation:
    def __init__(self, safe_rules: SafeAutomationRules):
        self.safe_rules = safe_rules
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """Initialize Playwright and browser."""
        logger.info("Starting Playwright...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=Config.HEADLESS)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        logger.info("Browser started.")

    async def stop(self):
        """Close browser and Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped.")

    async def login(self):
        """Login to LinkedIn."""
        logger.info("Logging in to LinkedIn...")
        await self.page.goto("https://www.linkedin.com/login")
        await self.page.fill("#username", Config.LINKEDIN_EMAIL)
        await self.page.fill("#password", Config.LINKEDIN_PASSWORD)
        await self.page.click("button[type='submit']")
        HumanSimulator.wait(5, 10)
        
        # Check if login was successful
        if "feed" in self.page.url:
            logger.info("Login successful.")
            return True
        else:
            logger.error("Login failed. Please check credentials or manual verification.")
            return False

    async def search_jobs(self, keyword="Desenvolvedor PHP Laravel"):
        """Search and view jobs."""
        if not self.safe_rules.can_perform_action('jobs_view'):
            return []
            
        logger.info(f"Searching for jobs: {keyword}")
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
        await self.page.goto(search_url)
        HumanSimulator.wait(3, 6)
        
        # Find job cards
        job_cards = await self.page.query_selector_all(".job-card-container")
        num_to_view = random.randint(3, 7)
        actions_data = []
        
        for i in range(min(len(job_cards), num_to_view)):
            if not self.safe_rules.can_perform_action('jobs_view'):
                break
                
            logger.info(f"Viewing job {i+1}/{num_to_view}...")
            
            # Get job title and link
            title_elem = await job_cards[i].query_selector(".disabled.ember-view.job-card-container__link")
            title = await title_elem.inner_text() if title_elem else "Unknown Job"
            link = await title_elem.get_attribute("href") if title_elem else self.page.url
            if link and not link.startswith("http"):
                link = "https://www.linkedin.com" + link
            
            await job_cards[i].click()
            HumanSimulator.wait(2, 4)
            
            # Check PHP relevance
            content = await self.page.content()
            is_php = 1 if any(kw in content.lower() for kw in ["php", "laravel", "symfony", "backend"]) else 0
            
            await HumanSimulator.human_scroll(self.page)
            HumanSimulator.random_pause()
            
            self.safe_rules.record_action('jobs_view')
            actions_data.append({
                'type': 'jobs_view',
                'url': link,
                'title': title.strip(),
                'is_php': is_php
            })
            
        return actions_data

    async def visit_recruiters(self):
        """Visit recruiter profiles."""
        if not self.safe_rules.can_perform_action('profile_visit'):
            return []
            
        logger.info("Visiting recruiter profiles...")
        search_url = "https://www.linkedin.com/search/results/people/?keywords=Recruiter%20Tech"
        await self.page.goto(search_url)
        HumanSimulator.wait(4, 8)
        
        profile_links = await self.page.query_selector_all(".entity-result__title-text a")
        num_to_visit = random.randint(2, 4)
        actions_data = []
        
        for i in range(min(len(profile_links), num_to_visit)):
            if not self.safe_rules.can_perform_action('profile_visit'):
                break
                
            profile_url = await profile_links[i].get_attribute("href")
            name = await profile_links[i].inner_text()
            
            logger.info(f"Visiting profile: {profile_url}")
            await self.page.goto(profile_url)
            HumanSimulator.wait(3, 6)
            
            # Check PHP relevance in profile
            content = await self.page.content()
            is_php = 1 if any(kw in content.lower() for kw in ["php", "laravel", "backend"]) else 0
            
            await HumanSimulator.human_scroll(self.page)
            HumanSimulator.random_pause()
            
            self.safe_rules.record_action('profile_visit')
            actions_data.append({
                'type': 'profile_visit',
                'url': profile_url,
                'title': name.strip(),
                'is_php': is_php
            })
            
            await self.page.goto(search_url)
            HumanSimulator.wait(2, 4)
            
        return actions_data

    async def interact_with_feed(self):
        """Interact with the feed (likes)."""
        if not self.safe_rules.can_perform_action('post_like'):
            return []
            
        logger.info("Interacting with feed...")
        await self.page.goto("https://www.linkedin.com/feed/")
        HumanSimulator.wait(3, 6)
        
        num_likes = random.randint(3, 6)
        actions_data = []
        
        for _ in range(num_likes):
            if not self.safe_rules.can_perform_action('post_like'):
                break
                
            # Find posts
            posts = await self.page.query_selector_all(".feed-shared-update-v2")
            if not posts: break
            
            post = random.choice(posts[:5])
            like_button = await post.query_selector("button.react-button__trigger:not(.react-button__trigger--active)")
            
            if like_button:
                # 1. Get post author (actor)
                author_elem = await post.query_selector(".update-components-actor__title span span:first-child")
                author = await author_elem.inner_text() if author_elem else "LinkedIn User"
                
                # 2. Get post text for PHP check and snippet
                post_text = await post.inner_text()
                is_php = 1 if any(kw in post_text.lower() for kw in ["php", "laravel", "backend", "software architecture"]) else 0
                
                # 3. Get post permalink (usually from the time link)
                # Typical selector is .update-components-actor__sub-description a or .feed-shared-actor__sub-description a
                link_elem = await post.query_selector(".update-components-actor__sub-description a, .feed-shared-actor__sub-description a")
                permalink = await link_elem.get_attribute("href") if link_elem else self.page.url
                if permalink and not permalink.startswith("http"):
                    permalink = "https://www.linkedin.com" + permalink
                
                await like_button.scroll_into_view_if_needed()
                HumanSimulator.wait(1, 2)
                await like_button.click()
                logger.info(f"Liked post by {author}")
                
                self.safe_rules.record_action('post_like')
                actions_data.append({
                    'type': 'post_like',
                    'url': permalink,
                    'title': f"{author}: {post_text[:60].strip()}...",
                    'is_php': is_php
                })
                
                await HumanSimulator.human_scroll(self.page)
                HumanSimulator.random_pause()
            
        return actions_data

    async def follow_companies(self):
        """Follow tech companies."""
        if not self.safe_rules.can_perform_action('company_follow'):
            return 0
            
        logger.info("Following tech companies...")
        search_url = "https://www.linkedin.com/search/results/companies/?keywords=Tech%20Software"
        await self.page.goto(search_url)
        HumanSimulator.wait(4, 8)
        
        follow_buttons = await self.page.query_selector_all("button.artdeco-button--secondary")
        followed_count = 0
        
        for button in follow_buttons:
            if not self.safe_rules.can_perform_action('company_follow'):
                break
                
            # 15% probability to follow
            if random.random() < 0.15:
                await button.scroll_into_view_if_needed()
                HumanSimulator.wait(1, 2)
                await button.click()
                logger.info("Followed a company.")
                self.safe_rules.record_action('company_follow')
                followed_count += 1
                HumanSimulator.wait(2, 4)
                
            if followed_count >= 2: # Limit per session
                break
                
        return followed_count
