"""
Question Generator Module
Generates tailored interview questions based on job description and resume
"""
from dotenv import load_dotenv
load_dotenv()
import os
from typing import List, Dict
import json


class QuestionGenerator:
    """Generate interview questions using AI based on JD and resume"""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        """
        Initialize question generator
        
        Args:
            api_key: API key for AI service
            provider: 'openai' or 'anthropic'
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.provider = provider
        
        # Check if it's actually a Groq key disguised as an OpenAI key
        is_groq = self.api_key and self.api_key.startswith("gsk_")

        if provider == "openai" or is_groq:
            try:
                import openai
                # If it's a Groq key, we change the base_url
                base_url = "https://api.groq.com/openai/v1" if is_groq else None
                self.client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
                
                # Use Groq's free model if using Groq, otherwise default OpenAI
                self.model_name = "llama3-8b-8192" if is_groq else "gpt-4o-mini"
                self.available = True
                print(f"Using {'Groq' if is_groq else 'OpenAI'} provider")
            except ImportError:
                print("OpenAI library not available. Install with: pip install openai")
                self.available = False
        elif provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.available = True
            except ImportError:
                print("Anthropic library not available. Install with: pip install anthropic")
                self.available = False
    
    def generate_questions(self, job_description: str, resume: str, 
                          num_questions: int = 5) -> List[Dict[str, str]]:
        """
        Generate interview questions tailored to JD and resume
        
        Args:
            job_description: Job description text
            resume: Resume text
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with question, category, and difficulty
        """
        if not self.available or not self.api_key:
            return self._generate_fallback_questions(job_description, num_questions)
        
        try:
            prompt = self._create_prompt(job_description, resume, num_questions)
            
            if self.provider == "openai" or self.api_key.startswith("gsk_"):
                response = self.client.chat.completions.create(
                    model=self.model_name, # Dynamically uses llama3 for Groq
                    messages=[
                        {"role": "system", "content": "You are an expert technical interviewer who creates insightful, role-specific interview questions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                questions_text = response.choices[0].message.content
                return self._parse_questions(questions_text)
            else:  # anthropic
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                questions_text = message.content[0].text
            
            return self._parse_questions(questions_text)
            
        except Exception as e:
            print(f"Error generating questions with AI: {e}")
            return self._generate_fallback_questions(job_description, num_questions)
    
    def _create_prompt(self, job_description: str, resume: str, num_questions: int) -> str:
        """Create prompt for AI question generation"""
        return f"""Based on the following job description and candidate resume, generate {num_questions} tailored interview questions.

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE RESUME:
{resume[:1500]}

Generate {num_questions} interview questions that:
1. Are specific to the role and the candidate's background
2. Test both technical skills and behavioral competencies
3. Vary in difficulty from basic to advanced
4. Cover different aspects of the role

Format each question as JSON with the following structure:
{{
    "question": "The interview question",
    "category": "technical/behavioral/situational",
    "difficulty": "basic/intermediate/advanced",
    "focus_area": "specific skill or competency being tested"
}}

Return ONLY a JSON array of {num_questions} questions, no additional text."""
    
    def _parse_questions(self, questions_text: str) -> List[Dict[str, str]]:
        """Parse AI-generated questions from text"""
        try:
            # Try to extract JSON from the response
            start_idx = questions_text.find('[')
            end_idx = questions_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = questions_text[start_idx:end_idx]
                questions = json.loads(json_str)
                return questions
            else:
                raise ValueError("No JSON array found in response")
                
        except Exception as e:
            print(f"Error parsing questions: {e}")
            # Fallback: create questions from text lines
            lines = [line.strip() for line in questions_text.split('\n') if line.strip()]
            questions = []
            for i, line in enumerate(lines[:5]):
                if '?' in line or any(line.startswith(q) for q in ['Tell me', 'Describe', 'Explain', 'How']):
                    questions.append({
                        'question': line.strip('0123456789.-) '),
                        'category': 'general',
                        'difficulty': 'intermediate',
                        'focus_area': 'general assessment'
                    })
            return questions if questions else self._generate_fallback_questions("", 5)
    
    def _generate_behavioral_questions(self, num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate standard behavioral questions"""
        behavioral_pool = [
            {
                'question': "Tell me about yourself and walk me through your background.",
                'category': 'behavioral',
                'difficulty': 'basic',
                'focus_area': 'self-introduction'
            },
            {
                'question': "Describe a challenging situation you faced and how you handled it.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'problem-solving'
            },
            {
                'question': "Tell me about a time when you had to work under pressure or meet a tight deadline.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'time management'
            },
            {
                'question': "Describe a situation where you had to collaborate with a difficult team member.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'teamwork'
            },
            {
                'question': "Tell me about a time when you failed at something. How did you handle it?",
                'category': 'behavioral',
                'difficulty': 'advanced',
                'focus_area': 'resilience'
            },
            {
                'question': "Describe a situation where you had to learn something new quickly.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'adaptability'
            },
            {
                'question': "Tell me about a time when you took initiative on a project.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'leadership'
            },
            {
                'question': "Describe a situation where you had to make a difficult decision.",
                'category': 'behavioral',
                'difficulty': 'advanced',
                'focus_area': 'decision-making'
            }
        ]
        return behavioral_pool[:num_questions]
    
    def _generate_technical_questions(self, job_description: str, num_questions: int = 5) -> List[Dict[str, str]]:
        """Generate technical questions based on job description"""
        jd_lower = job_description.lower()
        
        technical_questions = []
        
        # Python-related
        if 'python' in jd_lower:
            technical_questions.append({
                'question': "Explain the difference between lists and tuples in Python. When would you use each?",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'Python fundamentals'
            })
            technical_questions.append({
                'question': "How do you handle exceptions in Python? Give an example of try-except usage.",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'Python error handling'
            })
        
        # Machine Learning
        if 'machine learning' in jd_lower or 'ml' in jd_lower:
            technical_questions.append({
                'question': "What is the difference between supervised and unsupervised learning? Provide examples of each.",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'ML concepts'
            })
            technical_questions.append({
                'question': "Explain overfitting in machine learning. How would you prevent it?",
                'category': 'technical',
                'difficulty': 'advanced',
                'focus_area': 'ML model optimization'
            })
        
        # Data Science
        if 'data' in jd_lower:
            technical_questions.append({
                'question': "How would you handle missing data in a dataset?",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'data preprocessing'
            })
        
        # Deep Learning
        if 'deep learning' in jd_lower or 'neural network' in jd_lower:
            technical_questions.append({
                'question': "Explain how backpropagation works in neural networks.",
                'category': 'technical',
                'difficulty': 'advanced',
                'focus_area': 'deep learning'
            })
        
        # Web Development
        if 'web' in jd_lower or 'api' in jd_lower:
            technical_questions.append({
                'question': "What is the difference between GET and POST requests in HTTP?",
                'category': 'technical',
                'difficulty': 'basic',
                'focus_area': 'web development'
            })
        
        # Database
        if 'sql' in jd_lower or 'database' in jd_lower:
            technical_questions.append({
                'question': "Explain the difference between SQL and NoSQL databases. When would you use each?",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'database'
            })
        
        # Default technical questions if no matches
        if len(technical_questions) < num_questions:
            default_technical = [
                {
                    'question': "Describe your approach to debugging a complex technical issue.",
                    'category': 'technical',
                    'difficulty': 'intermediate',
                    'focus_area': 'problem-solving'
                },
                {
                    'question': "How do you ensure code quality in your projects?",
                    'category': 'technical',
                    'difficulty': 'intermediate',
                    'focus_area': 'best practices'
                },
                {
                    'question': "Explain a technical concept you recently learned and how you applied it.",
                    'category': 'technical',
                    'difficulty': 'intermediate',
                    'focus_area': 'continuous learning'
                }
            ]
            technical_questions.extend(default_technical)
        
        return technical_questions[:num_questions]
    
    def generate_resume_specific_questions(self, resume: str, job_description: str, 
                                          num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Generate highly specific questions based on resume content
        These are the most likely to be asked in real interviews
        """
        if not self.available or not self.api_key:
            print("⚠️ AI not available. Using fallback resume questions...")
            return self._generate_fallback_resume_questions(resume, job_description, num_questions)
        
        try:
            prompt = f"""You are an expert technical interviewer. Based on the candidate's resume and the job description, generate {num_questions} HIGHLY SPECIFIC interview questions that:

1. Are directly related to projects, technologies, or experiences mentioned in the resume
2. Test depth of knowledge about skills they claim to have
3. Ask about specific accomplishments or roles mentioned
4. Would naturally be asked by a hiring manager reviewing this resume
5. Connect resume experience to job requirements

RESUME:
{resume[:2000]}

JOB DESCRIPTION:
{job_description[:1500]}

Generate questions that dig deep into:
- Specific projects mentioned (ask about implementation details, challenges, results)
- Technologies and tools listed (ask about usage, experience level, best practices)
- Roles and responsibilities (ask about specific scenarios and decisions)
- Achievements mentioned (ask for details, metrics, process)

Format as JSON array with this structure:
[
    {{
        "question": "Specific question about resume content",
        "category": "resume_based",
        "difficulty": "intermediate/advanced",
        "focus_area": "specific skill/project from resume"
    }}
]

Return ONLY the JSON array of {num_questions} questions."""

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert interviewer who asks precise, resume-specific questions that would realistically be asked in interviews."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                questions_text = response.choices[0].message.content
            else:  # anthropic
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=3000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                questions_text = message.content[0].text
            
            questions = self._parse_questions(questions_text)
            
            # Ensure all questions are marked as resume_based
            for q in questions:
                q['category'] = 'resume_based'
            
            return questions
            
        except Exception as e:
            print(f"Error generating resume-specific questions: {e}")
            return self._generate_fallback_resume_questions(resume, job_description, num_questions)
    
    def _generate_fallback_resume_questions(self, resume: str, job_description: str, 
                                           num_questions: int) -> List[Dict[str, str]]:
        """Generate resume-specific questions when AI is unavailable"""
        resume_lower = resume.lower()
        questions = []
        
        # Extract likely technologies/skills from resume
        technologies = {
            'python': 'Python',
            'java': 'Java',
            'javascript': 'JavaScript',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'react': 'React',
            'django': 'Django',
            'flask': 'Flask',
            'sql': 'SQL',
            'aws': 'AWS',
            'docker': 'Docker'
        }
        
        found_tech = [tech_name for tech_key, tech_name in technologies.items() if tech_key in resume_lower]
        
        # Generate questions based on found technologies
        for tech in found_tech[:5]:
            questions.append({
                'question': f"I see you have experience with {tech}. Can you walk me through a specific project where you used {tech} and the challenges you faced?",
                'category': 'resume_based',
                'difficulty': 'intermediate',
                'focus_area': f'{tech} experience'
            })
        
        # Generic resume-based questions
        generic_resume_questions = [
            {
                'question': "Looking at your resume, which project are you most proud of and why?",
                'category': 'resume_based',
                'difficulty': 'intermediate',
                'focus_area': 'project discussion'
            },
            {
                'question': "Can you elaborate on your most recent role and what your day-to-day responsibilities were?",
                'category': 'resume_based',
                'difficulty': 'basic',
                'focus_area': 'work experience'
            },
            {
                'question': "You mentioned [skill] in your resume. How long have you been working with it and at what scale?",
                'category': 'resume_based',
                'difficulty': 'intermediate',
                'focus_area': 'skill verification'
            },
            {
                'question': "Tell me about the technical architecture of one of the projects listed on your resume.",
                'category': 'resume_based',
                'difficulty': 'advanced',
                'focus_area': 'technical depth'
            },
            {
                'question': "What was the biggest technical challenge you faced in your previous role and how did you solve it?",
                'category': 'resume_based',
                'difficulty': 'advanced',
                'focus_area': 'problem-solving'
            }
        ]
        
        questions.extend(generic_resume_questions)
        
        return questions[:num_questions]

    def _generate_fallback_questions(self, job_description: str, 
                                    num_questions: int) -> List[Dict[str, str]]:
        """Generate fallback questions when AI is not available"""
        
        # Analyze JD for technical terms
        jd_lower = job_description.lower()
        
        fallback_questions = [
            {
                'question': "Tell me about yourself and why you're interested in this position.",
                'category': 'behavioral',
                'difficulty': 'basic',
                'focus_area': 'introduction and motivation'
            },
            {
                'question': "Describe a challenging project you've worked on and how you overcame obstacles.",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'problem-solving and resilience'
            },
            {
                'question': "What are your strongest technical skills and how have you applied them in your previous roles?",
                'category': 'technical',
                'difficulty': 'intermediate',
                'focus_area': 'technical competency'
            },
            {
                'question': "How do you stay updated with the latest trends and technologies in your field?",
                'category': 'behavioral',
                'difficulty': 'basic',
                'focus_area': 'continuous learning'
            },
            {
                'question': "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'teamwork and conflict resolution'
            },
            {
                'question': "Walk me through your approach to debugging a complex technical issue.",
                'category': 'technical',
                'difficulty': 'advanced',
                'focus_area': 'analytical thinking'
            },
            {
                'question': "What do you consider your greatest professional achievement and why?",
                'category': 'behavioral',
                'difficulty': 'intermediate',
                'focus_area': 'self-awareness and impact'
            }
        ]
        
        # Add role-specific questions based on keywords
        if 'python' in jd_lower or 'machine learning' in jd_lower:
            fallback_questions.append({
                'question': "Explain how you would approach building a machine learning model for a classification problem.",
                'category': 'technical',
                'difficulty': 'advanced',
                'focus_area': 'machine learning expertise'
            })
        
        if 'leadership' in jd_lower or 'manage' in jd_lower:
            fallback_questions.append({
                'question': "Describe your experience leading a team and how you ensure team productivity and morale.",
                'category': 'behavioral',
                'difficulty': 'advanced',
                'focus_area': 'leadership and management'
            })
        
        return fallback_questions[:num_questions]


if __name__ == "__main__":
    # Test the question generator
    generator = QuestionGenerator()
    
    sample_jd = """
    Senior Software Engineer - AI/ML
    
    We are looking for an experienced software engineer with expertise in 
    Python, machine learning, and cloud technologies. The ideal candidate 
    will have 5+ years of experience building scalable ML systems.
    """
    
    sample_resume = """
    John Doe
    Software Engineer with 6 years of experience in Python development,
    machine learning, and cloud architecture. Expert in TensorFlow and AWS.
    """
    
    print("Generating interview questions...")
    questions = generator.generate_questions(sample_jd, sample_resume, num_questions=5)
    
    print(f"\nGenerated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Category: {q['category']} | Difficulty: {q['difficulty']}")
        print(f"   Focus: {q['focus_area']}")