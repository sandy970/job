import os
from typing import Dict, Any, List
from openai import AsyncOpenAI
import asyncio
import re

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            self.enabled = True
            print("✅ OpenAI client initialized")
        else:
            self.client = None
            self.enabled = False
            print("⚠️  OpenAI API key not found. Using mock AI responses.")

    async def generate_job_summary(self, job_description: str) -> str:
        """Generate a concise AI summary of a job description"""
        if not self.enabled:
            return self._generate_mock_summary(job_description)
        
        try:
            prompt = f"""
            Please provide a concise, professional summary of this job posting in 1-2 sentences. 
            Focus on the key responsibilities, required skills, and what makes this role attractive:

            Job Description:
            {job_description[:1000]}...
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional recruiter who summarizes job postings clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return self._generate_mock_summary(job_description)

    async def analyze_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """Analyze job requirements and extract key information"""
        if not self.enabled:
            return self._mock_job_analysis(job_description)
        
        try:
            prompt = f"""
            Analyze this job posting and extract key information in JSON format:
            
            Job Description:
            {job_description}
            
            Please return a JSON object with:
            - "skills": array of technical skills mentioned
            - "experience_level": "entry", "mid", "senior", or "executive"
            - "remote_friendly": true/false
            - "salary_estimate": estimated salary range if not mentioned
            - "key_benefits": array of main benefits/perks
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert job market analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error analyzing job requirements: {e}")
            return self._mock_job_analysis(job_description)

    def calculate_match_score(self, job: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """Calculate how well a job matches user preferences"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # Skills matching (40% weight)
            skills_weight = 0.4
            if user_preferences.get("skills") and job.get("requirements"):
                user_skills = [skill.lower() for skill in user_preferences["skills"]]
                job_requirements = [req.lower() for req in job["requirements"]]
                
                matching_skills = 0
                for skill in user_skills:
                    for req in job_requirements:
                        if skill in req:
                            matching_skills += 1
                            break
                
                if user_skills:
                    skills_score = matching_skills / len(user_skills)
                    score += skills_score * skills_weight
                    total_weight += skills_weight
            
            # Location matching (20% weight)
            location_weight = 0.2
            if user_preferences.get("preferred_locations") and job.get("location"):
                user_locations = [loc.lower() for loc in user_preferences["preferred_locations"]]
                job_location = job["location"].lower()
                
                location_match = any(loc in job_location for loc in user_locations)
                if location_match or "remote" in job_location:
                    score += 1.0 * location_weight
                    total_weight += location_weight
            
            # Salary matching (25% weight)
            salary_weight = 0.25
            if user_preferences.get("salary_min") and job.get("salary_range"):
                min_salary = user_preferences["salary_min"]
                salary_range = job["salary_range"]
                
                # Extract salary numbers from range
                salary_numbers = re.findall(r'\$?([\d,]+)', salary_range)
                if salary_numbers:
                    job_min_salary = int(salary_numbers[0].replace(',', ''))
                    if job_min_salary >= min_salary:
                        score += 1.0 * salary_weight
                    else:
                        # Partial credit if close
                        ratio = job_min_salary / min_salary
                        score += max(0, ratio) * salary_weight
                    total_weight += salary_weight
            
            # Company/title matching (15% weight)
            title_weight = 0.15
            if user_preferences.get("job_types") and job.get("title"):
                user_types = [jtype.lower() for jtype in user_preferences["job_types"]]
                job_title = job["title"].lower()
                
                title_match = any(jtype in job_title for jtype in user_types)
                if title_match:
                    score += 1.0 * title_weight
                    total_weight += title_weight
            
            # Normalize score
            return min(1.0, score / total_weight if total_weight > 0 else 0.0)
            
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0

    async def generate_application_letter(
        self, 
        job: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Generate a personalized application letter"""
        if not self.enabled:
            return self._generate_mock_application_letter(job, user_profile)
        
        try:
            prompt = f"""
            Write a professional, personalized cover letter for this job application:
            
            Job Title: {job.get('title', 'N/A')}
            Company: {job.get('company', 'N/A')}
            Job Description: {job.get('description', 'N/A')[:500]}...
            
            Applicant Profile:
            Skills: {', '.join(user_profile.get('skills', []))}
            Experience: {user_profile.get('experience', 'Not specified')}
            
            Make it professional, concise (3-4 paragraphs), and highlight relevant skills.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional career advisor writing compelling cover letters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating application letter: {e}")
            return self._generate_mock_application_letter(job, user_profile)

    async def extract_salary_info(self, job_description: str) -> Dict[str, Any]:
        """Extract and normalize salary information"""
        try:
            # Use regex to find salary patterns
            salary_patterns = [
                r'\$(\d{2,3}),?(\d{3})\s*-\s*\$(\d{2,3}),?(\d{3})',  # $100,000 - $150,000
                r'\$(\d{2,3})k\s*-\s*\$(\d{2,3})k',  # $100k - $150k
                r'(\d{2,3}),?(\d{3})\s*-\s*(\d{2,3}),?(\d{3})',  # 100,000 - 150,000
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, job_description, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 4:
                        min_salary = int(f"{groups[0]}{groups[1]}")
                        max_salary = int(f"{groups[2]}{groups[3]}")
                        return {
                            "min_salary": min_salary,
                            "max_salary": max_salary,
                            "currency": "USD",
                            "found": True
                        }
            
            return {"found": False}
            
        except Exception as e:
            print(f"Error extracting salary info: {e}")
            return {"found": False}

    def _generate_mock_summary(self, job_description: str) -> str:
        """Generate a mock summary when AI is not available"""
        description_words = job_description.lower().split()
        
        if any(word in description_words for word in ["senior", "lead", "principal"]):
            level = "senior"
        elif any(word in description_words for word in ["junior", "entry", "associate"]):
            level = "entry-level"
        else:
            level = "mid-level"
        
        if "remote" in description_words:
            location_note = " with remote work options"
        else:
            location_note = ""
        
        return f"This is a {level} position focused on software development{location_note}. The role involves working with modern technologies and collaborating with cross-functional teams."

    def _mock_job_analysis(self, job_description: str) -> Dict[str, Any]:
        """Generate mock job analysis"""
        description_lower = job_description.lower()
        
        # Extract common skills
        common_skills = ["python", "javascript", "react", "sql", "aws", "docker", "git"]
        found_skills = [skill for skill in common_skills if skill in description_lower]
        
        # Determine experience level
        if any(word in description_lower for word in ["senior", "lead", "principal"]):
            exp_level = "senior"
        elif any(word in description_lower for word in ["junior", "entry"]):
            exp_level = "entry"
        else:
            exp_level = "mid"
        
        return {
            "skills": found_skills,
            "experience_level": exp_level,
            "remote_friendly": "remote" in description_lower,
            "salary_estimate": "$80,000 - $120,000",
            "key_benefits": ["Health insurance", "401k", "Flexible hours"]
        }

    def _generate_mock_application_letter(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate mock application letter"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.get('title', 'position')} role at {job.get('company', 'your company')}. With my background in {', '.join(user_profile.get('skills', ['software development'])[:3])}, I am excited about the opportunity to contribute to your team.

My experience aligns well with your requirements, particularly in areas such as {', '.join(user_profile.get('skills', ['programming'])[:2])}. I am passionate about building high-quality software solutions and collaborating with diverse teams to achieve common goals.

I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's success. Thank you for considering my application.

Best regards,
[Your Name]"""