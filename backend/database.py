import sqlite3
import asyncio
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiosqlite

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database manager for job listings with duplicate prevention
    
    Handles job storage, duplicate detection, and basic analytics.
    Uses SQLite for simplicity but can be easily adapted for PostgreSQL/MySQL.
    """
    
    def __init__(self, db_path: str = "jobs.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        
    async def initialize_db(self):
        """Initialize database tables if they don't exist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create jobs table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_title TEXT NOT NULL,
                        company_name TEXT NOT NULL,
                        location TEXT NOT NULL,
                        job_url TEXT,
                        source TEXT NOT NULL,
                        job_type TEXT NOT NULL,
                        job_hash TEXT UNIQUE NOT NULL,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create index on job_hash for fast duplicate checking
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_job_hash ON jobs(job_hash)
                """)
                
                # Create index on job_type for filtering
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_job_type ON jobs(job_type)
                """)
                
                # Create index on scraped_at for time-based queries
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_scraped_at ON jobs(scraped_at)
                """)
                
                await db.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def _generate_job_hash(self, job: Dict[str, Any]) -> str:
        """
        Generate a unique hash for a job to detect duplicates
        
        Uses job_title, company_name, and location as the basis for uniqueness
        
        Args:
            job: Job dictionary
            
        Returns:
            MD5 hash string
        """
        # Normalize the fields for consistent hashing
        title = str(job.get('job_title', '')).lower().strip()
        company = str(job.get('company_name', '')).lower().strip()
        location = str(job.get('location', '')).lower().strip()
        
        # Create hash from key fields
        hash_string = f"{title}|{company}|{location}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    async def job_exists(self, job_hash: str) -> bool:
        """
        Check if a job already exists in the database
        
        Args:
            job_hash: Hash of the job to check
            
        Returns:
            True if job exists, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT 1 FROM jobs WHERE job_hash = ? AND is_active = TRUE",
                    (job_hash,)
                )
                result = await cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Error checking job existence: {str(e)}")
            return False
    
    async def save_job(self, job: Dict[str, Any], job_type: str) -> bool:
        """
        Save a single job to the database
        
        Args:
            job: Job dictionary
            job_type: Type of job (software-engineer, security-engineer, data-engineer)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Generate hash for duplicate detection
            job_hash = self._generate_job_hash(job)
            
            # Check if job already exists
            if await self.job_exists(job_hash):
                logger.debug(f"Job already exists: {job.get('job_title')} at {job.get('company_name')}")
                return False
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO jobs (
                        job_title, company_name, location, job_url, 
                        source, job_type, job_hash, scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.get('job_title', ''),
                    job.get('company_name', ''),
                    job.get('location', ''),
                    job.get('job_url', ''),
                    job.get('source', ''),
                    job_type,
                    job_hash,
                    datetime.fromtimestamp(job.get('scraped_at', datetime.now().timestamp()))
                ))
                
                await db.commit()
                logger.debug(f"Saved job: {job.get('job_title')} at {job.get('company_name')}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False
    
    async def filter_and_save_jobs(self, jobs: List[Dict[str, Any]], job_type: str) -> List[Dict[str, Any]]:
        """
        Filter out duplicate jobs and save new ones to database
        
        Args:
            jobs: List of job dictionaries
            job_type: Type of job (software-engineer, security-engineer, data-engineer)
            
        Returns:
            List of unique jobs that were saved
        """
        # Initialize database if needed
        await self.initialize_db()
        
        unique_jobs = []
        saved_count = 0
        
        try:
            for job in jobs:
                # Validate job data
                if not self._validate_job_data(job):
                    continue
                
                # Clean job data
                cleaned_job = self._clean_job_data(job)
                
                # Try to save job (will skip if duplicate)
                if await self.save_job(cleaned_job, job_type):
                    unique_jobs.append(cleaned_job)
                    saved_count += 1
                else:
                    # Still include in results even if not saved (was duplicate)
                    unique_jobs.append(cleaned_job)
            
            logger.info(f"Saved {saved_count} new jobs out of {len(jobs)} scraped jobs")
            
        except Exception as e:
            logger.error(f"Error filtering and saving jobs: {str(e)}")
        
        return unique_jobs
    
    def _validate_job_data(self, job: Dict[str, Any]) -> bool:
        """
        Validate job data before saving
        
        Args:
            job: Job dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['job_title', 'company_name', 'location']
        
        for field in required_fields:
            if field not in job or not job[field] or str(job[field]).strip() == "":
                logger.warning(f"Job missing required field: {field}")
                return False
        
        return True
    
    def _clean_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
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
                cleaned_value = ' '.join(str(job[field]).split())
                cleaned_job[field] = cleaned_value
            else:
                cleaned_job[field] = ""
        
        # Preserve other fields
        for field in ['job_url', 'source', 'scraped_at']:
            cleaned_job[field] = job.get(field, "")
        
        return cleaned_job
    
    async def get_jobs_by_type(self, job_type: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve jobs by type from database
        
        Args:
            job_type: Type of job to retrieve
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            
        Returns:
            List of job dictionaries
        """
        try:
            await self.initialize_db()
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT * FROM jobs 
                    WHERE job_type = ? AND is_active = TRUE 
                    ORDER BY scraped_at DESC 
                    LIMIT ? OFFSET ?
                """, (job_type, limit, offset))
                
                rows = await cursor.fetchall()
                
                jobs = []
                for row in rows:
                    job = dict(row)
                    jobs.append(job)
                
                return jobs
                
        except Exception as e:
            logger.error(f"Error retrieving jobs: {str(e)}")
            return []
    
    async def get_recent_jobs(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get jobs scraped in the last N hours
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of jobs to return
            
        Returns:
            List of recent job dictionaries
        """
        try:
            await self.initialize_db()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT * FROM jobs 
                    WHERE scraped_at >= ? AND is_active = TRUE 
                    ORDER BY scraped_at DESC 
                    LIMIT ?
                """, (cutoff_time, limit))
                
                rows = await cursor.fetchall()
                
                jobs = []
                for row in rows:
                    job = dict(row)
                    jobs.append(job)
                
                return jobs
                
        except Exception as e:
            logger.error(f"Error retrieving recent jobs: {str(e)}")
            return []
    
    async def get_scraping_stats(self) -> Dict[str, Any]:
        """
        Get statistics about scraped jobs
        
        Returns:
            Dictionary with various statistics
        """
        try:
            await self.initialize_db()
            
            async with aiosqlite.connect(self.db_path) as db:
                # Total jobs
                cursor = await db.execute("SELECT COUNT(*) FROM jobs WHERE is_active = TRUE")
                total_jobs = (await cursor.fetchone())[0]
                
                # Jobs by type
                cursor = await db.execute("""
                    SELECT job_type, COUNT(*) as count 
                    FROM jobs 
                    WHERE is_active = TRUE 
                    GROUP BY job_type
                """)
                jobs_by_type = dict(await cursor.fetchall())
                
                # Jobs by source
                cursor = await db.execute("""
                    SELECT source, COUNT(*) as count 
                    FROM jobs 
                    WHERE is_active = TRUE 
                    GROUP BY source
                """)
                jobs_by_source = dict(await cursor.fetchall())
                
                # Recent activity (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM jobs 
                    WHERE scraped_at >= ? AND is_active = TRUE
                """, (cutoff_time,))
                recent_jobs = (await cursor.fetchone())[0]
                
                return {
                    'total_jobs': total_jobs,
                    'jobs_by_type': jobs_by_type,
                    'jobs_by_source': jobs_by_source,
                    'recent_jobs_24h': recent_jobs,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                'total_jobs': 0,
                'jobs_by_type': {},
                'jobs_by_source': {},
                'recent_jobs_24h': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    async def cleanup_old_jobs(self, days: int = 30) -> int:
        """
        Mark old jobs as inactive to keep database size manageable
        
        Args:
            days: Jobs older than this many days will be marked inactive
            
        Returns:
            Number of jobs marked as inactive
        """
        try:
            await self.initialize_db()
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    UPDATE jobs 
                    SET is_active = FALSE 
                    WHERE scraped_at < ? AND is_active = TRUE
                """, (cutoff_time,))
                
                await db.commit()
                cleaned_count = cursor.rowcount
                
                logger.info(f"Marked {cleaned_count} old jobs as inactive")
                return cleaned_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {str(e)}")
            return 0

# Database connection placeholder for production systems
class ProductionDatabaseManager:
    """
    Placeholder for production database implementation
    
    This would typically connect to PostgreSQL, MySQL, or MongoDB
    in a production environment with proper connection pooling,
    migrations, and advanced querying capabilities.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize production database connection
        
        Args:
            connection_string: Database connection string
                Example for PostgreSQL: "postgresql://user:password@localhost/dbname"
                Example for MongoDB: "mongodb://localhost:27017/jobdb"
        """
        self.connection_string = connection_string
        self.connection_pool = None
        
        # TODO: Implement actual database connections
        logger.info(f"Production database manager initialized with: {connection_string}")
    
    async def connect(self):
        """Establish database connection pool"""
        # TODO: Implement connection pooling
        # For PostgreSQL: asyncpg.create_pool()
        # For MySQL: aiomysql.create_pool()
        # For MongoDB: motor.motor_asyncio.AsyncIOMotorClient()
        pass
    
    async def save_jobs_batch(self, jobs: List[Dict[str, Any]], job_type: str) -> int:
        """
        Save multiple jobs in a single batch operation for better performance
        
        Args:
            jobs: List of job dictionaries
            job_type: Type of jobs being saved
            
        Returns:
            Number of jobs successfully saved
        """
        # TODO: Implement batch insert with UPSERT/ON CONFLICT handling
        # This would be much more efficient for large datasets
        pass
    
    async def get_jobs_with_filters(self, 
                                   job_type: Optional[str] = None,
                                   location: Optional[str] = None,
                                   company: Optional[str] = None,
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """
        Advanced job filtering and search capabilities
        
        Args:
            job_type: Filter by job type
            location: Filter by location (supports partial matching)
            company: Filter by company name
            limit: Maximum results to return
            
        Returns:
            Filtered list of jobs
        """
        # TODO: Implement advanced filtering with full-text search
        pass
    
    async def get_analytics(self) -> Dict[str, Any]:
        """
        Advanced analytics and reporting
        
        Returns:
            Comprehensive analytics data
        """
        # TODO: Implement advanced analytics:
        # - Job posting trends over time
        # - Top companies by job postings
        # - Location-based statistics
        # - Salary analysis (if available)
        # - Skills analysis from job descriptions
        pass