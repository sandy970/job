import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re

class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    async def scrape_all_sources(
        self, 
        keywords: str, 
        location: Optional[str] = None, 
        max_jobs: int = 50
    ) -> List[Dict[str, Any]]:
        """Scrape jobs from multiple sources"""
        all_jobs = []
        
        # Scrape from different sources
        jobs_per_source = max_jobs // 3
        
        try:
            # Source 1: Mock job board (simulated scraping)
            mock_jobs = await self._scrape_mock_jobs(keywords, location, jobs_per_source)
            all_jobs.extend(mock_jobs)
            
            # Source 2: Stack Overflow Jobs (if available)
            # so_jobs = await self._scrape_stackoverflow_jobs(keywords, location, jobs_per_source)
            # all_jobs.extend(so_jobs)
            
            # Source 3: AngelList (if available)
            # angel_jobs = await self._scrape_angellist_jobs(keywords, location, jobs_per_source)
            # all_jobs.extend(angel_jobs)
            
            print(f"Total jobs scraped: {len(all_jobs)}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        return all_jobs[:max_jobs]

    async def _scrape_mock_jobs(
        self, 
        keywords: str, 
        location: Optional[str], 
        max_jobs: int
    ) -> List[Dict[str, Any]]:
        """Generate mock jobs for demonstration"""
        print(f"Generating mock jobs for: {keywords}")
        
        # Simulate network delay
        await asyncio.sleep(1)
        
        job_titles = [
            f"Senior {keywords} Developer",
            f"{keywords} Engineer",
            f"Lead {keywords} Specialist",
            f"Full Stack Developer with {keywords}",
            f"{keywords} Architect",
            f"Junior {keywords} Developer",
            f"{keywords} Team Lead",
            f"Principal {keywords} Engineer"
        ]
        
        companies = [
            "TechStart Inc", "Innovation Labs", "CodeCorp", "DevSolutions",
            "FutureTech", "AgileWorks", "CloudFirst", "DataDriven Co"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Denver, CO", "Remote", "Los Angeles, CA"
        ]
        
        mock_jobs = []
        
        for i in range(min(max_jobs, len(job_titles))):
            job = {
                "title": job_titles[i % len(job_titles)],
                "company": companies[i % len(companies)],
                "location": location if location else locations[i % len(locations)],
                "salary_range": self._generate_salary_range(),
                "description": self._generate_job_description(keywords),
                "requirements": self._generate_requirements(keywords),
                "url": f"https://mockjobboard.com/job/{i+100}",
                "source": "mockjobboard",
                "posted_date": datetime.now(),
                "scraped_at": datetime.now()
            }
            mock_jobs.append(job)
        
        return mock_jobs

    async def _scrape_with_playwright(self, url: str) -> List[Dict[str, Any]]:
        """Scrape JavaScript-heavy sites with Playwright"""
        jobs = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set realistic headers
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                await page.goto(url, wait_until='networkidle')
                
                # Wait for job listings to load
                await page.wait_for_selector('.job-listing', timeout=10000)
                
                # Extract job data
                job_elements = await page.query_selector_all('.job-listing')
                
                for element in job_elements:
                    try:
                        title = await element.query_selector('.job-title')
                        company = await element.query_selector('.company-name')
                        location = await element.query_selector('.job-location')
                        
                        if title and company:
                            job = {
                                "title": await title.inner_text(),
                                "company": await company.inner_text(),
                                "location": await location.inner_text() if location else "Not specified",
                                "url": url,
                                "source": "playwright_scrape",
                                "scraped_at": datetime.now()
                            }
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job element: {e}")
                        continue
                
                await browser.close()
                
        except Exception as e:
            print(f"Playwright scraping error: {e}")
        
        return jobs

    def _scrape_with_beautifulsoup(self, url: str) -> List[Dict[str, Any]]:
        """Scrape static sites with BeautifulSoup"""
        jobs = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example selectors (would vary by site)
            job_listings = soup.find_all('div', class_=['job-item', 'job-listing', 'job-card'])
            
            for listing in job_listings:
                try:
                    title_elem = listing.find(['h2', 'h3', 'a'], class_=['job-title', 'title'])
                    company_elem = listing.find(['span', 'div'], class_=['company', 'company-name'])
                    location_elem = listing.find(['span', 'div'], class_=['location', 'job-location'])
                    
                    if title_elem and company_elem:
                        job = {
                            "title": title_elem.get_text(strip=True),
                            "company": company_elem.get_text(strip=True),
                            "location": location_elem.get_text(strip=True) if location_elem else "Not specified",
                            "url": url,
                            "source": "beautifulsoup_scrape",
                            "scraped_at": datetime.now()
                        }
                        jobs.append(job)
                except Exception as e:
                    print(f"Error parsing job listing: {e}")
                    continue
                    
        except Exception as e:
            print(f"BeautifulSoup scraping error: {e}")
        
        return jobs

    def _generate_salary_range(self) -> str:
        """Generate realistic salary ranges"""
        import random
        
        base_salaries = [60000, 80000, 100000, 120000, 150000, 180000]
        base = random.choice(base_salaries)
        high = base + random.randint(20000, 50000)
        
        return f"${base:,} - ${high:,}"

    def _generate_job_description(self, keywords: str) -> str:
        """Generate realistic job descriptions"""
        descriptions = [
            f"We are seeking a talented professional with expertise in {keywords} to join our growing team. You will work on exciting projects and collaborate with cross-functional teams.",
            f"Join our innovative company as a {keywords} specialist. This role offers opportunities to work with cutting-edge technology and make a significant impact.",
            f"We're looking for a skilled {keywords} developer to help build scalable solutions. You'll be part of a dynamic team working on challenging problems.",
            f"Exciting opportunity for a {keywords} expert to lead technical initiatives and mentor junior team members in a fast-paced environment."
        ]
        
        import random
        return random.choice(descriptions)

    def _generate_requirements(self, keywords: str) -> List[str]:
        """Generate realistic job requirements"""
        base_requirements = [
            f"3+ years experience with {keywords}",
            "Bachelor's degree in Computer Science or related field",
            "Strong problem-solving skills",
            "Excellent communication skills",
            "Experience with Agile methodologies"
        ]
        
        tech_requirements = [
            "JavaScript", "Python", "React", "Node.js", "PostgreSQL", 
            "AWS", "Docker", "Git", "REST APIs", "TypeScript"
        ]
        
        import random
        selected_tech = random.sample(tech_requirements, 3)
        
        return base_requirements + selected_tech

    async def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape detailed information for a specific job"""
        try:
            response = self.session.get(job_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed job information
            description_elem = soup.find(['div', 'section'], class_=['job-description', 'description'])
            requirements_elem = soup.find(['div', 'ul'], class_=['requirements', 'qualifications'])
            
            details = {
                "description": description_elem.get_text(strip=True) if description_elem else "",
                "requirements": [],
                "scraped_at": datetime.now()
            }
            
            # Extract requirements
            if requirements_elem:
                req_items = requirements_elem.find_all(['li', 'p'])
                details["requirements"] = [item.get_text(strip=True) for item in req_items]
            
            return details
            
        except Exception as e:
            print(f"Error scraping job details: {e}")
            return {"description": "", "requirements": [], "scraped_at": datetime.now()}