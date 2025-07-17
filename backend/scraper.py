import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import logging
import time
import random
from urllib.parse import urlencode, quote_plus
import re

# Configure logging
logger = logging.getLogger(__name__)

class JobScraper:
    """
    Web scraper for job listings from LinkedIn and Indeed
    
    Handles HTTP requests, HTML parsing, and data extraction with error handling
    and rate limiting to avoid being blocked.
    """
    
    def __init__(self):
        """Initialize the scraper with default settings"""
        # User agents to rotate for avoiding detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Request settings
        self.session_timeout = 30
        self.rate_limit_delay = (1, 3)  # Random delay between 1-3 seconds
        
    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers for HTTP requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def build_linkedin_url(self, query: str, location: str = "United States") -> str:
        """
        Build LinkedIn job search URL
        
        Args:
            query: Job search query (e.g., "Full Stack Java Engineer")
            location: Location to search in
            
        Returns:
            Complete LinkedIn search URL
        """
        base_url = "https://www.linkedin.com/jobs/search"
        params = {
            'keywords': query,
            'location': location,
            'f_TPR': 'r86400',  # Posted in last 24 hours
            'f_JT': 'F',  # Full-time only
            'start': 0
        }
        
        url = f"{base_url}?{urlencode(params)}"
        logger.info(f"Built LinkedIn URL: {url}")
        return url
    
    def build_indeed_url(self, query: str, location: str = "United States") -> str:
        """
        Build Indeed job search URL
        
        Args:
            query: Job search query (e.g., "Software Engineer")
            location: Location to search in
            
        Returns:
            Complete Indeed search URL
        """
        base_url = "https://www.indeed.com/jobs"
        params = {
            'q': query,
            'l': location,
            'fromage': '1',  # Posted in last day
            'jt': 'fulltime',  # Full-time only
            'start': 0
        }
        
        url = f"{base_url}?{urlencode(params)}"
        logger.info(f"Built Indeed URL: {url}")
        return url
    
    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """
        Fetch a web page with error handling and rate limiting
        
        Args:
            session: Aiohttp session
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            # Add random delay to avoid rate limiting
            delay = random.uniform(*self.rate_limit_delay)
            await asyncio.sleep(delay)
            
            headers = self._get_headers()
            
            async with session.get(url, headers=headers, timeout=self.session_timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"Successfully fetched page: {url}")
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None
    
    def _extract_linkedin_jobs(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract job data from LinkedIn HTML
        
        Args:
            html_content: Raw HTML from LinkedIn jobs page
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # LinkedIn job cards are typically in elements with specific classes
            # Note: LinkedIn frequently changes their class names, so this may need updates
            job_elements = soup.find_all('div', {'class': 'job-search-card'}) or \
                          soup.find_all('div', {'data-entity-urn': True}) or \
                          soup.find_all('li', {'class': 'result-card'})
            
            logger.info(f"Found {len(job_elements)} job elements on LinkedIn")
            
            for job_element in job_elements:
                try:
                    job_data = self._parse_linkedin_job_element(job_element)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job element: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing LinkedIn HTML: {str(e)}")
            
        return jobs
    
    def _parse_linkedin_job_element(self, job_element) -> Optional[Dict[str, Any]]:
        """
        Parse individual LinkedIn job element
        
        Args:
            job_element: BeautifulSoup element containing job data
            
        Returns:
            Job dictionary or None if parsing fails
        """
        try:
            # Extract job title
            title_element = job_element.find('h3') or \
                           job_element.find('a', {'data-control-name': 'job_search_job_title'}) or \
                           job_element.find('span', {'title': True})
            
            job_title = None
            job_url = None
            
            if title_element:
                # Try to get title from text or title attribute
                job_title = title_element.get_text(strip=True) or title_element.get('title', '').strip()
                
                # Try to get URL from href attribute
                link_element = title_element.find('a') if title_element.name != 'a' else title_element
                if link_element and link_element.get('href'):
                    job_url = link_element['href']
                    if job_url.startswith('/'):
                        job_url = f"https://www.linkedin.com{job_url}"
            
            # Extract company name
            company_element = job_element.find('h4') or \
                             job_element.find('a', {'data-control-name': 'job_search_company_name'}) or \
                             job_element.find('span', class_=re.compile(r'company'))
            
            company_name = company_element.get_text(strip=True) if company_element else "Unknown Company"
            
            # Extract location
            location_element = job_element.find('span', class_=re.compile(r'location')) or \
                              job_element.find('div', class_=re.compile(r'location'))
            
            location = location_element.get_text(strip=True) if location_element else "Unknown Location"
            
            # Validate required fields
            if not job_title or job_title == "":
                logger.warning("Job title not found, skipping job")
                return None
                
            return {
                'job_title': job_title,
                'company_name': company_name,
                'location': location,
                'job_url': job_url or '',
                'source': 'linkedin',
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing LinkedIn job element: {str(e)}")
            return None
    
    def _extract_indeed_jobs(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract job data from Indeed HTML
        
        Args:
            html_content: Raw HTML from Indeed jobs page
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Indeed job cards are typically in specific div containers
            job_elements = soup.find_all('div', {'class': 'job_seen_beacon'}) or \
                          soup.find_all('div', {'data-jk': True}) or \
                          soup.find_all('td', {'class': 'resultContent'})
            
            logger.info(f"Found {len(job_elements)} job elements on Indeed")
            
            for job_element in job_elements:
                try:
                    job_data = self._parse_indeed_job_element(job_element)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error parsing Indeed job element: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Indeed HTML: {str(e)}")
            
        return jobs
    
    def _parse_indeed_job_element(self, job_element) -> Optional[Dict[str, Any]]:
        """
        Parse individual Indeed job element
        
        Args:
            job_element: BeautifulSoup element containing job data
            
        Returns:
            Job dictionary or None if parsing fails
        """
        try:
            # Extract job title and URL
            title_element = job_element.find('h2', {'class': 'jobTitle'}) or \
                           job_element.find('a', {'data-testid': 'job-title'}) or \
                           job_element.find('span', {'title': True})
            
            job_title = None
            job_url = None
            
            if title_element:
                # Get title text
                title_link = title_element.find('a') if title_element.name != 'a' else title_element
                if title_link:
                    job_title = title_link.get_text(strip=True) or title_link.get('title', '').strip()
                    if title_link.get('href'):
                        job_url = f"https://www.indeed.com{title_link['href']}"
                else:
                    job_title = title_element.get_text(strip=True)
            
            # Extract company name
            company_element = job_element.find('span', {'class': 'companyName'}) or \
                             job_element.find('a', {'data-testid': 'company-name'}) or \
                             job_element.find('div', class_=re.compile(r'company'))
            
            company_name = "Unknown Company"
            if company_element:
                company_link = company_element.find('a') if company_element.name != 'a' else company_element
                company_name = (company_link or company_element).get_text(strip=True)
            
            # Extract location
            location_element = job_element.find('div', {'data-testid': 'job-location'}) or \
                              job_element.find('span', class_=re.compile(r'location')) or \
                              job_element.find('div', class_=re.compile(r'location'))
            
            location = location_element.get_text(strip=True) if location_element else "Unknown Location"
            
            # Validate required fields
            if not job_title or job_title == "":
                logger.warning("Job title not found, skipping job")
                return None
                
            return {
                'job_title': job_title,
                'company_name': company_name,
                'location': location,
                'job_url': job_url or '',
                'source': 'indeed',
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing Indeed job element: {str(e)}")
            return None
    
    async def scrape_jobs(self, url: str, source: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Main scraping function that fetches and parses job listings
        
        Args:
            url: URL to scrape
            source: Source name (linkedin, indeed)
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Create aiohttp session with proper settings
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=self.session_timeout)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # Fetch the page
                html_content = await self._fetch_page(session, url)
                
                if not html_content:
                    logger.error(f"Failed to fetch content from {url}")
                    return []
                
                # Parse jobs based on source
                if source.lower() == 'linkedin':
                    jobs = self._extract_linkedin_jobs(html_content)
                elif source.lower() == 'indeed':
                    jobs = self._extract_indeed_jobs(html_content)
                else:
                    logger.error(f"Unsupported source: {source}")
                    return []
                
                # Limit results
                jobs = jobs[:limit]
                
                logger.info(f"Successfully scraped {len(jobs)} jobs from {source}")
                
                return jobs
                
        except Exception as e:
            logger.error(f"Error in scrape_jobs: {str(e)}")
            return []
    
    def validate_job_data(self, job: Dict[str, Any]) -> bool:
        """
        Validate that a job dictionary has required fields
        
        Args:
            job: Job dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['job_title', 'company_name', 'location']
        
        for field in required_fields:
            if field not in job or not job[field] or job[field].strip() == "":
                logger.warning(f"Job missing required field: {field}")
                return False
                
        return True
    
    def clean_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize job data
        
        Args:
            job: Raw job dictionary
            
        Returns:
            Cleaned job dictionary
        """
        cleaned_job = {}
        
        # Clean text fields
        text_fields = ['job_title', 'company_name', 'location']
        for field in text_fields:
            if field in job:
                # Remove extra whitespace and normalize
                cleaned_value = re.sub(r'\s+', ' ', str(job[field])).strip()
                cleaned_job[field] = cleaned_value
            else:
                cleaned_job[field] = ""
        
        # Preserve other fields
        for field in ['job_url', 'source', 'scraped_at']:
            cleaned_job[field] = job.get(field, "")
        
        return cleaned_job