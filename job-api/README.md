# Job Dashboard API

A FastAPI-based backend for the real-time job application dashboard with AI-powered job matching and web scraping capabilities.

## Features

- **Real-time Job Scraping**: Scrape jobs from multiple sources using BeautifulSoup and Playwright
- **AI-Powered Analysis**: Generate job summaries and match scores using OpenAI
- **Supabase Integration**: Real-time database with automatic syncing
- **RESTful API**: Clean, documented API endpoints
- **Background Processing**: Asynchronous job scraping and processing

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required for full functionality:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

**Optional (will use mock data if not provided):**
- `OPENAI_API_KEY`: For AI summaries and analysis

### 3. Run the API

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Jobs
- `GET /jobs` - Get all jobs with pagination
- `GET /jobs/{job_id}` - Get specific job
- `GET /jobs/search` - Search jobs with filters
- `POST /jobs/{job_id}/analyze` - Generate AI analysis

### Scraping
- `POST /scrape` - Trigger job scraping

### User Preferences
- `POST /user/preferences` - Update user preferences

### Utility
- `GET /` - API status
- `GET /health` - Health check

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## Database Schema

The app uses Supabase (PostgreSQL) with the following tables:

### Jobs Table
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  salary_range TEXT,
  description TEXT,
  requirements TEXT[],
  url TEXT UNIQUE,
  source TEXT,
  posted_date TIMESTAMP,
  scraped_at TIMESTAMP DEFAULT NOW(),
  ai_summary TEXT,
  match_score FLOAT
);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  skills TEXT[],
  preferred_locations TEXT[],
  salary_min INTEGER,
  job_types TEXT[]
);
```

## Demo Mode

The application works without external services by using mock data:

- **Without Supabase**: Returns demo job listings
- **Without OpenAI**: Generates mock AI summaries
- **Scraping**: Creates realistic mock jobs

## Architecture

```
FastAPI Application
├── main.py              # Application entry point
├── database.py          # Supabase integration
├── scraper.py           # Web scraping (Playwright + BeautifulSoup)
├── ai_service.py        # OpenAI integration
└── requirements.txt     # Dependencies
```

## Scraping Strategy

1. **Multiple Sources**: Supports various job boards
2. **Rate Limiting**: Respectful scraping with delays
3. **Anti-Detection**: Realistic browser headers and behavior
4. **Deduplication**: Prevents duplicate job entries
5. **Background Processing**: Non-blocking scraping operations

## Development

### Adding New Job Sources

1. Extend `JobScraper` class in `scraper.py`
2. Implement source-specific scraping methods
3. Add to `scrape_all_sources()` method

### Extending AI Features

1. Add new methods to `AIService` class
2. Implement corresponding API endpoints
3. Update frontend to consume new features

## Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

The API includes built-in monitoring:
- Health check endpoint at `/health`
- Request logging
- Error tracking
- Performance metrics

## Legal Considerations

- Always respect `robots.txt`
- Implement appropriate rate limiting
- Check website terms of service
- Consider using official APIs when available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details