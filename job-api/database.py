import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import asyncio

class DatabaseService:
    def __init__(self):
        # These would normally come from environment variables
        # For demo purposes, using placeholder values
        self.supabase_url = os.getenv("SUPABASE_URL", "your-supabase-url")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "your-supabase-anon-key")
        
        # Initialize Supabase client
        try:
            if self.supabase_url != "your-supabase-url":
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            else:
                self.supabase = None
                print("⚠️  Supabase not configured. Using mock data for demo.")
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            self.supabase = None

    async def get_jobs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get jobs with pagination"""
        if not self.supabase:
            return self._get_mock_jobs()[:limit]
        
        try:
            response = self.supabase.table("jobs").select("*").range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return self._get_mock_jobs()[:limit]

    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID"""
        if not self.supabase:
            mock_jobs = self._get_mock_jobs()
            return next((job for job in mock_jobs if job["id"] == job_id), None)
        
        try:
            response = self.supabase.table("jobs").select("*").eq("id", job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching job {job_id}: {e}")
            return None

    async def get_job_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Check if a job with this URL already exists"""
        if not self.supabase:
            mock_jobs = self._get_mock_jobs()
            return next((job for job in mock_jobs if job["url"] == url), None)
        
        try:
            response = self.supabase.table("jobs").select("*").eq("url", url).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error checking job URL: {e}")
            return None

    async def insert_job(self, job_data: Dict[str, Any]) -> str:
        """Insert a new job"""
        if not self.supabase:
            print(f"Mock: Would insert job {job_data['title']} at {job_data['company']}")
            return "mock-job-id"
        
        try:
            response = self.supabase.table("jobs").insert(job_data).execute()
            return response.data[0]["id"]
        except Exception as e:
            print(f"Error inserting job: {e}")
            return ""

    async def update_job_summary(self, job_id: str, summary: str) -> bool:
        """Update job with AI summary"""
        if not self.supabase:
            print(f"Mock: Would update job {job_id} with summary")
            return True
        
        try:
            self.supabase.table("jobs").update({"ai_summary": summary}).eq("id", job_id).execute()
            return True
        except Exception as e:
            print(f"Error updating job summary: {e}")
            return False

    async def update_job_match_score(self, job_id: str, score: float) -> bool:
        """Update job match score"""
        if not self.supabase:
            print(f"Mock: Would update job {job_id} with match score {score}")
            return True
        
        try:
            self.supabase.table("jobs").update({"match_score": score}).eq("id", job_id).execute()
            return True
        except Exception as e:
            print(f"Error updating match score: {e}")
            return False

    async def search_jobs(
        self, 
        query: Optional[str] = None,
        location: Optional[str] = None,
        min_salary: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search jobs with filters"""
        if not self.supabase:
            mock_jobs = self._get_mock_jobs()
            # Apply basic filtering for demo
            if query:
                mock_jobs = [job for job in mock_jobs if query.lower() in job["title"].lower()]
            return mock_jobs[:limit]
        
        try:
            query_builder = self.supabase.table("jobs").select("*")
            
            if query:
                query_builder = query_builder.ilike("title", f"%{query}%")
            if location:
                query_builder = query_builder.ilike("location", f"%{location}%")
            
            response = query_builder.limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

    async def update_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        if not self.supabase:
            print(f"Mock: Would update user preferences: {preferences}")
            return True
        
        try:
            # For demo, we'll use a fixed user ID
            user_id = "demo-user"
            existing = self.supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            
            preferences["user_id"] = user_id
            
            if existing.data:
                self.supabase.table("user_preferences").update(preferences).eq("user_id", user_id).execute()
            else:
                self.supabase.table("user_preferences").insert(preferences).execute()
            
            return True
        except Exception as e:
            print(f"Error updating user preferences: {e}")
            return False

    async def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs for processing"""
        if not self.supabase:
            return self._get_mock_jobs()
        
        try:
            response = self.supabase.table("jobs").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching all jobs: {e}")
            return []

    def _get_mock_jobs(self) -> List[Dict[str, Any]]:
        """Return mock job data for demo purposes"""
        return [
            {
                "id": "1",
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "salary_range": "$120,000 - $180,000",
                "description": "We are looking for a senior software engineer to join our team. You will be responsible for developing high-quality software solutions, mentoring junior developers, and collaborating with cross-functional teams.",
                "requirements": ["Python", "React", "PostgreSQL", "AWS"],
                "url": "https://example.com/job/1",
                "source": "demo",
                "posted_date": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "ai_summary": "Senior role with leadership responsibilities, focus on full-stack development",
                "match_score": 0.85
            },
            {
                "id": "2",
                "title": "Frontend Developer",
                "company": "StartupXYZ",
                "location": "Remote",
                "salary_range": "$80,000 - $120,000",
                "description": "Join our innovative startup as a frontend developer. You'll work on cutting-edge web applications using modern JavaScript frameworks.",
                "requirements": ["React", "TypeScript", "CSS", "Next.js"],
                "url": "https://example.com/job/2",
                "source": "demo",
                "posted_date": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "ai_summary": "Remote frontend position with modern tech stack",
                "match_score": 0.72
            },
            {
                "id": "3",
                "title": "Data Scientist",
                "company": "AI Solutions Ltd",
                "location": "New York, NY",
                "salary_range": "$100,000 - $150,000",
                "description": "We're seeking a data scientist to analyze large datasets and build machine learning models to drive business insights.",
                "requirements": ["Python", "Machine Learning", "SQL", "TensorFlow"],
                "url": "https://example.com/job/3",
                "source": "demo",
                "posted_date": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "ai_summary": "Data science role with ML focus, hybrid work environment",
                "match_score": 0.68
            },
            {
                "id": "4",
                "title": "DevOps Engineer",
                "company": "CloudTech Solutions",
                "location": "Austin, TX",
                "salary_range": "$95,000 - $140,000",
                "description": "Looking for a DevOps engineer to manage our cloud infrastructure and implement CI/CD pipelines.",
                "requirements": ["AWS", "Docker", "Kubernetes", "Terraform"],
                "url": "https://example.com/job/4",
                "source": "demo",
                "posted_date": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "ai_summary": "DevOps position with cloud infrastructure focus",
                "match_score": 0.79
            },
            {
                "id": "5",
                "title": "Product Manager",
                "company": "Innovation Inc",
                "location": "Seattle, WA",
                "salary_range": "$110,000 - $160,000",
                "description": "We need a product manager to drive product strategy and work closely with engineering and design teams.",
                "requirements": ["Product Strategy", "Agile", "User Research", "Analytics"],
                "url": "https://example.com/job/5",
                "source": "demo",
                "posted_date": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "ai_summary": "Strategic product management role with cross-functional collaboration",
                "match_score": 0.63
            }
        ]