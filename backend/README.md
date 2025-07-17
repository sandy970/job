# Job Dashboard Backend

A robust FastAPI-based web scraping backend for job listings across different engineering roles. This backend scrapes job data from LinkedIn and Indeed, stores it in a database with duplicate prevention, and provides RESTful API endpoints for accessing the data.

## Features

- 🔍 **Web Scraping**: Scrapes job listings from LinkedIn and Indeed using BeautifulSoup
- 📊 **Multiple Job Types**: Supports software engineering, security engineering, and data engineering roles
- 🗄️ **Database Integration**: SQLite database with duplicate prevention and data analytics
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- ⚡ **Async Operations**: Asynchronous scraping for better performance
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 📈 **Rate Limiting**: Built-in delays to avoid being blocked by job sites
- 🧪 **Testing**: Comprehensive test suite included

## API Endpoints

### Core Job Endpoints

- `GET /jobs/software-engineer` - Get Full Stack Java Engineer and related software development jobs
- `GET /jobs/security-engineer` - Get Cybersecurity Engineer and related security jobs  
- `GET /jobs/data-engineer` - Get Data Engineer and related analytics jobs
- `GET /jobs/all` - Get jobs from all categories
- `GET /jobs/{job_type}` - Generic endpoint for any job type

### Utility Endpoints

- `GET /` - Health check and API status
- `GET /config` - Get available job types and sources
- `GET /stats` - Get scraping statistics and analytics

### Query Parameters

All job endpoints support these parameters:
- `source` (optional): Job board to scrape (`linkedin` or `indeed`, default: `linkedin`)
- `limit` (optional): Maximum number of jobs to return (default: `20`)

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 3. Test the API

```bash
# Test the health endpoint
curl http://localhost:8000/

# Get software engineering jobs
curl "http://localhost:8000/jobs/software-engineer?limit=5"

# Get security engineering jobs from Indeed
curl "http://localhost:8000/jobs/security-engineer?source=indeed&limit=10"

# Get all job types
curl "http://localhost:8000/jobs/all?limit_per_type=5"

# Get statistics
curl http://localhost:8000/stats
```

## Project Structure

```
backend/
├── main.py              # FastAPI application and API endpoints
├── scraper.py           # Web scraping logic with BeautifulSoup
├── database.py          # Database management and duplicate prevention
├── test_api.py          # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── jobs.db             # SQLite database (created automatically)
```

## Architecture

### Job Scraper (`scraper.py`)

- **Multi-source support**: LinkedIn and Indeed job boards
- **Robust parsing**: Multiple fallback selectors for different page layouts
- **Rate limiting**: Random delays between requests to avoid blocking
- **Error handling**: Graceful handling of missing elements and network issues
- **User agent rotation**: Multiple user agents to appear more human-like

### Database Manager (`database.py`)

- **Duplicate prevention**: Hash-based deduplication using job title, company, and location
- **Data validation**: Ensures all required fields are present before saving
- **Analytics**: Built-in statistics and reporting capabilities
- **Cleanup**: Automatic cleanup of old job listings
- **Async operations**: Non-blocking database operations

### API Layer (`main.py`)

- **FastAPI framework**: Modern Python web framework with automatic docs
- **Async endpoints**: Non-blocking API endpoints for better performance
- **Error handling**: Comprehensive HTTP error responses
- **CORS support**: Cross-origin resource sharing for frontend integration
- **Logging**: Detailed logging for debugging and monitoring

## Job Search Configuration

The backend is configured to search for specific job types:

```python
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
```

You can easily modify these configurations to search for different job types or keywords.

## Database Schema

The SQLite database uses the following schema:

```sql
CREATE TABLE jobs (
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
);
```

## Testing

### Run All Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run the test suite
pytest test_api.py -v
```

### Manual Testing

```bash
# Run manual tests
python test_api.py
```

### Test Coverage

The test suite covers:
- All API endpoints
- Error handling scenarios
- Different parameter combinations
- Concurrent request handling
- Data validation

## API Examples

### Get Software Engineering Jobs

```bash
curl -X GET "http://localhost:8000/jobs/software-engineer?source=linkedin&limit=10" \
     -H "accept: application/json"
```

**Response:**
```json
[
  {
    "job_title": "Senior Full Stack Java Developer",
    "company_name": "Tech Company Inc",
    "location": "San Francisco, CA",
    "job_url": "https://www.linkedin.com/jobs/view/123456789",
    "source": "linkedin",
    "scraped_at": 1640995200.0
  }
]
```

### Get All Job Types

```bash
curl -X GET "http://localhost:8000/jobs/all?limit_per_type=5" \
     -H "accept: application/json"
```

**Response:**
```json
{
  "jobs": {
    "software-engineer": [...],
    "security-engineer": [...],
    "data-engineer": [...]
  },
  "total_count": 15,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Get Statistics

```bash
curl -X GET "http://localhost:8000/stats" \
     -H "accept: application/json"
```

**Response:**
```json
{
  "total_jobs": 150,
  "jobs_by_type": {
    "software-engineer": 60,
    "security-engineer": 45,
    "data-engineer": 45
  },
  "jobs_by_source": {
    "linkedin": 75,
    "indeed": 75
  },
  "recent_jobs_24h": 25,
  "last_updated": "2024-01-01T12:00:00"
}
```

## Configuration

### Environment Variables

You can configure the application using environment variables:

```bash
# Database path
export DB_PATH="./jobs.db"

# Log level
export LOG_LEVEL="INFO"

# Server settings
export HOST="0.0.0.0"
export PORT="8000"
```

### Customizing Search Queries

To modify search queries for different job types, edit the `JOB_CONFIGS` dictionary in `main.py`:

```python
JOB_CONFIGS = {
    "your-job-type": {
        "linkedin_query": "Your LinkedIn Search Term",
        "indeed_query": "Your Indeed Search Term", 
        "description": "Description of this job type"
    }
}
```

## Production Deployment

### Database Migration

For production, consider migrating from SQLite to PostgreSQL:

1. Install PostgreSQL dependencies:
```bash
pip install asyncpg psycopg2-binary
```

2. Update `database.py` to use the `ProductionDatabaseManager` class
3. Set the `DATABASE_URL` environment variable

### Performance Optimization

- Use Redis for caching frequently accessed data
- Implement proper rate limiting with `slowapi`
- Add monitoring with Sentry
- Use a reverse proxy like Nginx

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring and Logging

The application includes comprehensive logging:

- **INFO level**: Normal operation logs
- **WARNING level**: Non-critical issues (missing job elements)
- **ERROR level**: Critical errors requiring attention

Logs include:
- Scraping statistics
- Database operations
- API request handling
- Error details

## Rate Limiting and Ethics

The scraper includes several features to ensure ethical scraping:

- **Random delays**: 1-3 seconds between requests
- **User agent rotation**: Appears more human-like
- **Respectful parsing**: Only extracts public job listing information
- **Error handling**: Graceful handling of blocked requests

## Troubleshooting

### Common Issues

1. **No jobs returned**: Job sites may have changed their HTML structure. Check the scraper selectors in `scraper.py`.

2. **Database errors**: Ensure the SQLite database file is writable and the directory exists.

3. **Rate limiting**: If you're getting blocked, increase the delay in `scraper.py`.

4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`.

### Debug Mode

Enable debug logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest test_api.py`
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect the terms of service of job websites and implement appropriate rate limiting and ethical scraping practices.