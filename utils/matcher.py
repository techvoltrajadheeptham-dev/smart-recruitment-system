import re
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List

class CandidateMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
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
        keywords_match = self._calculate_keywords_match(candidate_data['raw_text'], job_description)
        
        # Weighted final score
        weights = {
            'skills': 0.4,
            'experience': 0.3,
            'semantic': 0.2,
            'keywords': 0.1
        }
        
        final_score = (
            skills_match * weights['skills'] +
            experience_match * weights['experience'] +
            semantic_match * weights['semantic'] +
            keywords_match * weights['keywords']
        ) * 100
        
        return {
            **candidate_data,
            'match_score': final_score,
            'skills_match': skills_match * 100,
            'experience_match': experience_match * 100,
            'semantic_match': semantic_match * 100,
            'keywords_match': keywords_match * 100
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
        # Extract required experience from JD
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
        """Calculate semantic similarity using sentence transformers"""
        # Encode both texts
        resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = self.model.encode(job_description, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.pytorch_cos_sim(resume_embedding, jd_embedding)
        return similarity.item()
    
    def _calculate_keywords_match(self, resume_text: str, job_description: str) -> float:
        """Calculate keyword match percentage"""
        # Extract important keywords from JD (non-skill keywords)
        jd_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)
        
        if not jd_keywords:
            return 0.0
        
        matched_keywords = set(resume_keywords) & set(jd_keywords)
        return len(matched_keywords) / len(jd_keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction - you can enhance this
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words and focus on meaningful terms
        stop_words = {'this', 'that', 'with', 'have', 'from', 'they', 'what'}
        keywords = [word for word in words if word not in stop_words and word not in self.skills_db]
        
        return list(set(keywords))[:20]  # Return top 20 unique keywords