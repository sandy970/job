# 🚀 Deployment Guide - Job Dashboard

This guide will help you deploy the Job Dashboard application to production.

## 📋 Prerequisites

- GitHub account
- Vercel account (for frontend)
- Railway account (for backend) 
- Supabase account (for database)
- OpenAI account (optional, for AI features)

## 🗄️ Database Setup (Supabase)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Click "New Project"
   - Choose organization and name your project
   - Wait for project to be ready

2. **Set up Database Schema**
   - Go to SQL Editor in your Supabase dashboard
   - Run the following SQL:

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

-- Create policies for public access (demo mode)
CREATE POLICY "Public jobs access" ON jobs FOR SELECT USING (true);
CREATE POLICY "Public jobs insert" ON jobs FOR INSERT WITH CHECK (true);
CREATE POLICY "Public jobs update" ON jobs FOR UPDATE USING (true);
CREATE POLICY "Public preferences access" ON user_preferences FOR ALL USING (true);
```

3. **Get Connection Details**
   - Go to Settings > API
   - Copy your `Project URL` and `anon` key
   - Save these for later

## 🔧 Backend Deployment (Railway)

1. **Prepare Backend for Deployment**
   ```bash
   cd job-api
   
   # Create Procfile for Railway
   echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
   
   # Create railway.json (optional)
   cat > railway.json << EOF
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn main:app --host 0.0.0.0 --port \$PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   EOF
   ```

2. **Deploy to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

3. **Set Environment Variables**
   - Go to your Railway dashboard
   - Click on your service
   - Go to Variables tab
   - Add the following variables:
     ```
     SUPABASE_URL=your-supabase-project-url
     SUPABASE_ANON_KEY=your-supabase-anon-key
     OPENAI_API_KEY=your-openai-api-key (optional)
     PORT=8000
     ```

4. **Get Backend URL**
   - Railway will provide a URL like `https://your-app.railway.app`
   - Save this URL for frontend configuration

## 🎨 Frontend Deployment (Vercel)

1. **Prepare Frontend for Deployment**
   ```bash
   cd job-dashboard
   
   # Update API URL for production
   # Edit src/components/JobSearch.tsx, JobList.tsx, etc.
   # Replace "http://localhost:8000" with your Railway backend URL
   ```

2. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy
   vercel --prod
   ```

   Or deploy via GitHub:
   - Push your code to GitHub
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically build and deploy

3. **Configure Environment Variables**
   - In Vercel dashboard, go to your project
   - Go to Settings > Environment Variables
   - Add if needed (currently no frontend env vars required)

## 🔑 Environment Variables Summary

### Backend (Railway)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
OPENAI_API_KEY=sk-your-openai-key (optional)
PORT=8000
```

### Frontend (Vercel)
```env
# No environment variables needed for current setup
# API URLs are configured directly in components
```

## 🔄 Update API URLs for Production

After deploying the backend, update the frontend to use the production API URL:

1. **Find and Replace in Frontend**
   ```bash
   cd job-dashboard
   
   # Replace localhost URLs with your Railway URL
   find src -name "*.tsx" -exec sed -i 's|http://localhost:8000|https://your-app.railway.app|g' {} +
   ```

2. **Redeploy Frontend**
   ```bash
   vercel --prod
   ```

## 📊 Testing Your Deployment

1. **Test Backend API**
   ```bash
   curl https://your-app.railway.app/health
   curl https://your-app.railway.app/jobs
   ```

2. **Test Frontend**
   - Visit your Vercel URL
   - Try searching for jobs
   - Check that API calls work in browser dev tools

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Add your Vercel domain to CORS origins in `main.py`
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000", 
           "https://your-app.vercel.app"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Database Connection Issues**
   - Verify Supabase environment variables
   - Check RLS policies are correctly set
   - Test connection from Railway logs

3. **Build Failures**
   - Check Railway build logs
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

## 📈 Monitoring & Maintenance

### Railway Monitoring
- Check application logs in Railway dashboard
- Monitor memory and CPU usage
- Set up alerts for downtime

### Vercel Analytics
- Enable Vercel Analytics for frontend metrics
- Monitor Core Web Vitals
- Track user engagement

### Database Monitoring
- Use Supabase dashboard for query performance
- Monitor database size and usage
- Set up backup policies

## 🔐 Security Considerations

1. **API Keys**
   - Never commit API keys to Git
   - Use environment variables for all secrets
   - Rotate keys regularly

2. **Database Security**
   - Review RLS policies
   - Enable audit logging in Supabase
   - Monitor for unusual access patterns

3. **Rate Limiting**
   - Implement rate limiting in FastAPI
   - Monitor scraping activities
   - Respect robots.txt and terms of service

## 🚀 Performance Optimization

1. **Backend Optimization**
   - Enable response caching
   - Optimize database queries
   - Use connection pooling

2. **Frontend Optimization**
   - Implement lazy loading
   - Optimize images and assets
   - Use React.memo for expensive components

3. **Database Optimization**
   - Add indexes for frequently queried fields
   - Implement pagination for large datasets
   - Use Supabase edge functions for heavy operations

## 📝 Maintenance Tasks

### Weekly
- Check application health and performance
- Review error logs and fix issues
- Monitor API usage and costs

### Monthly
- Update dependencies (with testing)
- Review security advisories
- Backup database (automated via Supabase)

### Quarterly
- Performance audit and optimization
- Security review and penetration testing
- Feature usage analysis and cleanup

## 🎉 Success!

Your Job Dashboard should now be live! 

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

Share your deployment and start finding amazing job opportunities! 🎯