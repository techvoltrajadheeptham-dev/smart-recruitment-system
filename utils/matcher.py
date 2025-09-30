import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List

class CandidateMatcher:
    def __init__(self):
        self.skills_db = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'mongodb', 'postgresql',
            'mysql', 'redis', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum',
            'tableau', 'power bi', 'excel', 'tensorflow', 'pytorch', 'sklearn',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly'
        ]
    
    def calculate_match(self, candidate_data: Dict, job_description: str) -> Dict:
        """Calculate match score between candidate and job description"""
        
        # Calculate different match components
        skills_match = self._calculate_skills_match(candidate_data['skills'], job_description)
        experience_match = self._calculate_experience_match(candidate_data['experience'], job_description)
        semantic_match = self._calculate_semantic_match(candidate_data['raw_text'], job_description)
        
        # Weighted final score
        final_score = (
            skills_match * 0.5 +
            experience_match * 0.3 +
            semantic_match * 0.2
        ) * 100
        
        return {
            **candidate_data,
            'match_score': final_score,
            'skills_match': skills_match * 100,
            'experience_match': experience_match * 100,
            'semantic_match': semantic_match * 100
        }
    
    def _calculate_skills_match(self, candidate_skills: List[str], job_description: str) -> float:
        """Calculate skills match percentage"""
        job_skills = self._extract_skills_from_jd(job_description)
        
        if not job_skills:
            return 0.0
        
        matched_skills = set(candidate_skills) & set(job_skills)
        return len(matched_skills) / len(job_skills) if job_skills else 0.0
    
    def _extract_skills_from_jd(self, job_description: str) -> List[str]:
        """Extract skills from job description"""
        found_skills = []
        jd_lower = job_description.lower()
        
        for skill in self.skills_db:
            if skill in jd_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_experience_match(self, candidate_experience: float, job_description: str) -> float:
        """Calculate experience match"""
        required_exp = self._extract_required_experience(job_description)
        
        if required_exp == 0:
            return 1.0  # No experience requirement specified
        
        if candidate_experience >= required_exp:
            return 1.0
        else:
            return candidate_experience / required_exp
    
    def _extract_required_experience(self, job_description: str) -> float:
        """Extract required years of experience from job description"""
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yr',
            r'experience.*?(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, job_description.lower())
            if matches:
                return float(matches[0])
        
        return 0.0
    
    def _calculate_semantic_match(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        # Combine texts
        documents = [resume_text, job_description]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        try:
            # Transform documents to TF-IDF features
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words and focus on meaningful terms
        stop_words = {'this', 'that', 'with', 'have', 'from', 'they', 'what'}
        keywords = [word for word in words if word not in stop_words and word not in self.skills_db]
        
        return list(set(keywords))[:20]
