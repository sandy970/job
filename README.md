# Job Dashboard - AI-Enhanced Real-Time Job Search Platform

A modern, full-stack job application dashboard that combines real-time web scraping, AI-powered job matching, and a beautiful user interface to help you find your next opportunity.

![Job Dashboard Preview](https://via.placeholder.com/800x400/2563eb/ffffff?text=Job+Dashboard+Preview)

## ✨ Features

### 🚀 Real-Time Job Scraping
- **Multi-source scraping** from various job boards
- **Intelligent deduplication** to avoid duplicate listings
- **Background processing** for non-blocking operations
- **Rate limiting** and respectful scraping practices

### 🤖 AI-Powered Insights
- **Job summarization** using OpenAI GPT models
- **Skill matching** and compatibility scoring
- **Personalized recommendations** based on your preferences
- **Automatic job analysis** and categorization

### 💻 Modern Frontend
- **Real-time updates** with live job notifications
- **Responsive design** that works on all devices
- **Advanced filtering** and search capabilities
- **Beautiful UI** with smooth animations

### 📊 Smart Analytics
- **Job market insights** and trending skills
- **Match score visualization** for quick decisions
- **Application tracking** and status management
- **Performance metrics** and success rates

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js App  │◄──►│   FastAPI       │◄──►│   Supabase      │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │  Web Scrapers   │    │  Real-time      │
         │              │  (Playwright)   │    │  Subscriptions  │
         │              └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   OpenAI API    │
│   (AI Features) │
└─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React Query** - Efficient data fetching and caching
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python API framework
- **Playwright** - Browser automation for dynamic sites
- **BeautifulSoup** - HTML parsing for static content
- **OpenAI API** - AI-powered job analysis
- **Pydantic** - Data validation and serialization

### Database & Infrastructure
- **Supabase** - PostgreSQL with real-time capabilities
- **Vercel** - Frontend deployment
- **Railway** - Backend deployment

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd job-dashboard
```

### 2. Setup Backend
```bash
cd job-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start the API server
python main.py
```

### 3. Setup Frontend
```bash
cd job-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚙️ Configuration

### Required Environment Variables

**Backend (`job-api/.env`)**:
```env
# Supabase (optional - uses mock data if not provided)
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key

# OpenAI (optional - uses mock AI if not provided)
OPENAI_API_KEY=your-openai-api-key
```

### Database Setup (Optional)

If you want to use Supabase for real data:

1. Create a [Supabase](https://supabase.com) account
2. Create a new project
3. Run the following SQL in the SQL editor:

```sql
-- Jobs table
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

-- User preferences table
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  skills TEXT[],
  preferred_locations TEXT[],
  salary_min INTEGER,
  job_types TEXT[]
);

-- Enable Row Level Security
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Allow public read access to jobs
CREATE POLICY "Public jobs access" ON jobs FOR SELECT USING (true);
CREATE POLICY "Public jobs insert" ON jobs FOR INSERT WITH CHECK (true);
CREATE POLICY "Public jobs update" ON jobs FOR UPDATE USING (true);

-- Allow public access to user preferences (demo mode)
CREATE POLICY "Public preferences access" ON user_preferences FOR ALL USING (true);
```

4. Copy your project URL and anon key to the `.env` file

## 📖 Usage Guide

### 1. Search for Jobs
- Enter keywords like "React Developer", "Python", or "Machine Learning"
- Optionally specify a location
- Click "Scrape New Jobs" to fetch fresh listings

### 2. Set Your Preferences
- Click the "Preferences" button
- Add your skills, preferred locations, and salary requirements
- Save to get personalized match scores

### 3. Browse and Analyze
- View jobs in the dashboard with AI summaries
- Click on any job for detailed information
- Use the "Generate AI Analysis" button for deeper insights

### 4. Track Applications
- Click "View Original Job" to apply
- Monitor your application status
- Review match scores to prioritize applications

## 🎯 Key Features Demo

### Real-Time Job Scraping
```bash
# The app demonstrates scraping with mock data
# In production, it would scrape from:
# - Job boards like Indeed, LinkedIn
# - Company career pages
# - Remote work platforms
```

### AI-Powered Matching
```javascript
// Example match score calculation
const matchScore = calculateMatch(job, userPreferences);
// Factors: skills overlap, location preference, salary range
```

### Live Updates
```javascript
// Real-time job updates using Supabase subscriptions
supabase
  .channel('jobs')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'jobs' },
    (payload) => updateJobsList(payload.new)
  )
  .subscribe();
```

## 🔧 Development

### Project Structure
```
job-dashboard/
├── job-api/                 # FastAPI backend
│   ├── main.py             # API entry point
│   ├── database.py         # Database operations
│   ├── scraper.py          # Web scraping logic
│   ├── ai_service.py       # AI integration
│   └── requirements.txt    # Python dependencies
├── job-dashboard/          # Next.js frontend
│   ├── src/app/           # App Router pages
│   ├── src/components/    # React components
│   └── package.json       # Node dependencies
└── README.md              # This file
```

### Adding New Features

1. **New Job Sources**: Extend `scraper.py` with new source methods
2. **AI Features**: Add methods to `ai_service.py`
3. **UI Components**: Create new components in `src/components/`
4. **API Endpoints**: Add routes to `main.py`

### Testing

```bash
# Backend tests
cd job-api
python -m pytest

# Frontend tests
cd job-dashboard
npm test
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd job-dashboard
npm run build
vercel --prod
```

### Backend (Railway)
```bash
cd job-api
railway login
railway init
railway up
```

### Environment Variables for Production
Update your deployment platforms with the same environment variables from your `.env` files.

## 📊 Performance & Monitoring

### Metrics Tracked
- Job scraping success rates
- API response times
- User engagement metrics
- Match score accuracy

### Monitoring Tools
- Sentry for error tracking
- Vercel Analytics for frontend metrics
- Custom logging for scraping operations

## 🔒 Legal & Ethical Considerations

### Web Scraping Best Practices
- Respect robots.txt files
- Implement rate limiting
- Use official APIs when available
- Check terms of service
- Cache responses to reduce server load

### Data Privacy
- No personal data collection without consent
- Secure API key storage
- GDPR compliance considerations
- Regular security audits

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper testing
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines
- Use TypeScript for type safety
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

### Getting Help
- Check the [Issues](../../issues) for common problems
- Read the documentation in each service directory
- Review the API documentation at `/docs`

### Feature Requests
- Open an issue with the "enhancement" label
- Describe the use case and expected behavior
- Include mockups or examples if helpful

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide error messages and logs
- Specify your environment details

## 🎉 Acknowledgments

- **OpenAI** for providing powerful AI capabilities
- **Supabase** for the excellent real-time database
- **Vercel** and **Railway** for reliable hosting
- **The open-source community** for amazing tools and libraries

---

**Built with ❤️ by developers, for developers**

*Happy job hunting! 🎯*