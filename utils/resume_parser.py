import re
import spacy
from PyPDF2 import PdfReader
from docx import Document
from typing import Dict, List
import subprocess
import sys

class ResumeParser:
    def __init__(self):
        # Download spaCy model if not available
        self.nlp = self._load_spacy_model()
        self.skills_db = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'mongodb', 'postgresql',
            'mysql', 'redis', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum',
            'tableau', 'power bi', 'excel', 'tensorflow', 'pytorch', 'sklearn',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly'
        ]
    
    def _load_spacy_model(self):
        """Load spaCy model, download if not available"""
        try:
            # Try to load the model
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except OSError:
            # Model not found, download it
            print("Downloading spaCy model...")
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ])
            # Load the model after download
            nlp = spacy.load("en_core_web_sm")
            return nlp
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract structured information"""
        try:
            text = self._extract_text(file_path)
            
            return {
                'name': self._extract_name(text),
                'email': self._extract_email(text),
                'phone': self._extract_phone(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text),
                'raw_text': text
            }
        except Exception as e:
            # Return default data if parsing fails
            return {
                'name': 'Unknown Candidate',
                'email': 'N/A',
                'phone': 'N/A',
                'skills': [],
                'experience': 0.0,
                'education': 'N/A',
                'raw_text': f'Error parsing resume: {str(e)}'
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from different file formats"""
        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_from_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                return self._extract_from_docx(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name using spaCy NER"""
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text
            return "Unknown Candidate"
        except:
            return "Unknown Candidate"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else "No email found"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else "No phone found"
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_db:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience(self, text: str) -> float:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*yr',
            r'experience.*?(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                # Return the highest experience found
                return float(max(matches))
        
        return 0.0
    
    def _extract_education(self, text: str) -> str:
        """Extract education information"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'mba', 'bs', 'ms', 'ba', 'ma',
            'university', 'college', 'degree', 'graduated'
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in education_keywords):
                return sentence.strip()[:100]  # Limit length
        
        return "Education not specified"
