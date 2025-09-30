from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Candidate:
    name: str
    email: str
    phone: str
    skills: List[str]
    experience: float
    education: str
    resume_text: str
    match_score: float = 0.0
    skills_match: float = 0.0
    experience_match: float = 0.0
    semantic_match: float = 0.0
    status: str = "New"
    applied_date: str = None
    
    def __post_init__(self):
        if self.applied_date is None:
            self.applied_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class JobDescription:
    title: str
    description: str
    required_skills: List[str]
    required_experience: float
    company: str
    location: str

class CandidatePool:
    def __init__(self):
        self.candidates = []
    
    def add_candidate(self, candidate: Candidate):
        self.candidates.append(candidate)
    
    def get_top_candidates(self, top_n: int = 10) -> List[Candidate]:
        return sorted(self.candidates, key=lambda x: x.match_score, reverse=True)[:top_n]
    
    def filter_by_score(self, min_score: float) -> List[Candidate]:
        return [candidate for candidate in self.candidates if candidate.match_score >= min_score]