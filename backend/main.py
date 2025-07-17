from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

from scraper import JobScraper
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Job Dashboard API",
    description="A web scraping API for job listings across different engineering roles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
job_scraper = JobScraper()
db_manager = DatabaseManager()

# Job search configurations for different roles
JOB_CONFIGS = {
    "software-engineer": {
        "linkedin_query": "Full Stack Java Engineer",
        "indeed_query": "Software Engineer",
        "description": "Full-stack and software development positions"
    },
    "security-engineer": {
        "linkedin_query": "Cybersecurity Engineer",
        "indeed_query": "Security Engineer",
        "description": "Information security and cybersecurity positions"
    },
    "data-engineer": {
        "linkedin_query": "Data Engineer",
        "indeed_query": "Data Engineer",
        "description": "Data engineering and analytics positions"
    }
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Job Dashboard API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/jobs/all")
async def get_all_jobs(source: str = "linkedin", limit_per_type: int = 10):
    """
    Get jobs from all engineering categories
    
    Args:
        source: Job board to scrape from (linkedin, indeed)
        limit_per_type: Maximum number of jobs per category
        
    Returns:
        Dictionary with jobs grouped by type
    """
    try:
        # Validate source
        if source not in ["linkedin", "indeed"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid source. Must be 'linkedin' or 'indeed'"
            )
        
        all_jobs = {}
        
        # Scrape jobs for each category sequentially to avoid overwhelming the servers
        for job_type in JOB_CONFIGS.keys():
            try:
                logger.info(f"Starting job scraping for {job_type} from {source}")
                
                # Get job configuration
                config = JOB_CONFIGS[job_type]
                query = config[f"{source}_query"]
                
                # Build search URL based on source
                if source == "linkedin":
                    search_url = job_scraper.build_linkedin_url(query)
                else:  # indeed
                    search_url = job_scraper.build_indeed_url(query)
                
                logger.info(f"Scraping URL: {search_url}")
                
                # Scrape jobs
                jobs = await job_scraper.scrape_jobs(search_url, source, limit_per_type)
                
                # Check for duplicates and save to database
                unique_jobs = await db_manager.filter_and_save_jobs(jobs, job_type)
                
                logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs for {job_type}")
                
                all_jobs[job_type] = unique_jobs
                
            except Exception as e:
                logger.error(f"Error scraping {job_type}: {str(e)}")
                all_jobs[job_type] = []
        
        # Calculate total count
        total_jobs = sum(len(jobs) for jobs in all_jobs.values())
        
        return {
            "jobs": all_jobs,
            "total_count": total_jobs,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 errors) as-is
        raise
    except Exception as e:
        logger.error(f"Error in get_all_jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching all jobs: {str(e)}")

@app.get("/jobs/software-engineer")
async def get_software_engineer_jobs(source: str = "linkedin", limit: int = 20):
    """
    Get software engineering jobs
    
    Searches for Full Stack Java Engineer positions and related software development roles
    """
    return await get_jobs("software-engineer", source, limit)

@app.get("/jobs/security-engineer")
async def get_security_engineer_jobs(source: str = "linkedin", limit: int = 20):
    """
    Get security engineering jobs
    
    Searches for Cybersecurity Engineer positions and related information security roles
    """
    return await get_jobs("security-engineer", source, limit)

@app.get("/jobs/data-engineer")
async def get_data_engineer_jobs(source: str = "linkedin", limit: int = 20):
    """
    Get data engineering jobs
    
    Searches for Data Engineer positions and related data analytics roles
    """
    return await get_jobs("data-engineer", source, limit)

@app.get("/jobs/{job_type}", response_model=List[Dict[str, Any]])
async def get_jobs(job_type: str, source: str = "linkedin", limit: int = 20):
    """
    Scrape jobs for a specific engineering role
    
    Args:
        job_type: Type of engineering job (software-engineer, security-engineer, data-engineer)
        source: Job board to scrape from (linkedin, indeed)
        limit: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries with job_title, company_name, location, job_url
    """
    try:
        # Validate job type
        if job_type not in JOB_CONFIGS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid job type. Must be one of: {list(JOB_CONFIGS.keys())}"
            )
        
        # Validate source
        if source not in ["linkedin", "indeed"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid source. Must be 'linkedin' or 'indeed'"
            )
        
        logger.info(f"Starting job scraping for {job_type} from {source}")
        
        # Get job configuration
        config = JOB_CONFIGS[job_type]
        query = config[f"{source}_query"]
        
        # Build search URL based on source
        if source == "linkedin":
            search_url = job_scraper.build_linkedin_url(query)
        else:  # indeed
            search_url = job_scraper.build_indeed_url(query)
        
        logger.info(f"Scraping URL: {search_url}")
        
        # Scrape jobs
        jobs = await job_scraper.scrape_jobs(search_url, source, limit)
        
        # Check for duplicates and save to database
        unique_jobs = await db_manager.filter_and_save_jobs(jobs, job_type)
        
        logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs for {job_type}")
        
        return unique_jobs
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 errors) as-is
        raise
    except Exception as e:
        logger.error(f"Error scraping jobs for {job_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scraping jobs: {str(e)}")

@app.get("/config")
async def get_job_configs():
    """Get available job configurations"""
    return {
        "job_types": JOB_CONFIGS,
        "supported_sources": ["linkedin", "indeed"]
    }

@app.get("/stats")
async def get_scraping_stats():
    """Get scraping statistics from database"""
    try:
        stats = await db_manager.get_scraping_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)