from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# Import our modules
from scraper import JobScraper
from ai_service import AIService
from database import DatabaseService

load_dotenv()

app = FastAPI(title="Job Dashboard API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_service = DatabaseService()
ai_service = AIService()
job_scraper = JobScraper()

# Pydantic models
class Job(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    description: str
    requirements: Optional[List[str]] = None
    url: str
    source: str
    posted_date: Optional[datetime] = None
    scraped_at: datetime = datetime.now()
    ai_summary: Optional[str] = None
    match_score: Optional[float] = None

class ScrapeRequest(BaseModel):
    keywords: str
    location: Optional[str] = None
    max_jobs: int = 50

class UserPreferences(BaseModel):
    skills: List[str]
    preferred_locations: List[str]
    salary_min: Optional[int] = None
    job_types: List[str]

@app.get("/")
async def root():
    return {"message": "Job Dashboard API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/jobs", response_model=List[Job])
async def get_jobs(limit: int = 50, offset: int = 0):
    """Get all jobs with pagination"""
    try:
        jobs = await db_service.get_jobs(limit=limit, offset=offset)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID"""
    try:
        job = await db_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")

@app.post("/scrape")
async def scrape_jobs(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Trigger job scraping in the background"""
    try:
        background_tasks.add_task(
            run_scraping_pipeline, 
            request.keywords, 
            request.location, 
            request.max_jobs
        )
        return {"message": "Scraping started in background", "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scrape: {str(e)}")

@app.post("/jobs/{job_id}/analyze")
async def analyze_job(job_id: str):
    """Generate AI analysis for a job"""
    try:
        job = await db_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Generate AI summary
        summary = await ai_service.generate_job_summary(job["description"])
        
        # Update job with AI summary
        await db_service.update_job_summary(job_id, summary)
        
        return {"message": "Job analyzed successfully", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job: {str(e)}")

@app.post("/user/preferences")
async def update_user_preferences(preferences: UserPreferences):
    """Update user job preferences"""
    try:
        await db_service.update_user_preferences(preferences.dict())
        
        # Recalculate match scores for existing jobs
        await recalculate_match_scores(preferences)
        
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")

@app.get("/jobs/search")
async def search_jobs(
    q: Optional[str] = None,
    location: Optional[str] = None,
    min_salary: Optional[int] = None,
    limit: int = 50
):
    """Search jobs with filters"""
    try:
        jobs = await db_service.search_jobs(
            query=q,
            location=location,
            min_salary=min_salary,
            limit=limit
        )
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

async def run_scraping_pipeline(keywords: str, location: Optional[str], max_jobs: int):
    """Background task to scrape jobs and process them"""
    try:
        print(f"Starting scraping for: {keywords}")
        
        # Scrape jobs from multiple sources
        scraped_jobs = await job_scraper.scrape_all_sources(
            keywords=keywords,
            location=location,
            max_jobs=max_jobs
        )
        
        print(f"Scraped {len(scraped_jobs)} jobs")
        
        # Process each job
        for job_data in scraped_jobs:
            try:
                # Check if job already exists
                existing_job = await db_service.get_job_by_url(job_data["url"])
                if existing_job:
                    continue
                
                # Generate AI summary
                if job_data.get("description"):
                    job_data["ai_summary"] = await ai_service.generate_job_summary(
                        job_data["description"]
                    )
                
                # Calculate match score (placeholder - would use user preferences)
                job_data["match_score"] = 0.0
                
                # Save to database
                await db_service.insert_job(job_data)
                
            except Exception as e:
                print(f"Error processing job: {e}")
                continue
        
        print("Scraping pipeline completed")
        
    except Exception as e:
        print(f"Error in scraping pipeline: {e}")

async def recalculate_match_scores(preferences: UserPreferences):
    """Recalculate match scores for all jobs based on user preferences"""
    try:
        jobs = await db_service.get_all_jobs()
        for job in jobs:
            score = ai_service.calculate_match_score(job, preferences.dict())
            await db_service.update_job_match_score(job["id"], score)
    except Exception as e:
        print(f"Error recalculating match scores: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)