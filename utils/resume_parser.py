import re
from PyPDF2 import PdfReader
from docx import Document
from typing import Dict, List

class ResumeParser:
    def __init__(self):
        self.skills_db = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'mongodb', 'postgresql',
            'mysql', 'redis', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum',
            'tableau', 'power bi', 'excel', 'tensorflow', 'pytorch', 'sklearn',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly'
        ]
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract structured information"""
        try:
            text = self._extract_text(file_path)
            
            return {
                'name': self._extract_name_simple(text),
                'email': self._extract_email(text),
                'phone': self._extract_phone(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education_simple(text),
                'raw_text': text
            }
        except Exception as e:
            return {
                'name': 'Candidate',
                'email': 'N/A',
                'phone': 'N/A',
                'skills': [],
                'experience': 0.0,
                'education': 'N/A',
                'raw_text': f'Error: {str(e)}'
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
        except:
            return "Could not read file"
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except:
            return "PDF read error"
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])
        except:
            return "DOCX read error"
    
    def _extract_name_simple(self, text: str) -> str:
        """Simple name extraction without spaCy"""
        # Look for patterns like "Name: John Doe" or email prefixes
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['name:', 'full name:', 'candidate:']):
                # Extract name after the keyword
                name_part = line.split(':', 1)[-1].strip()
                if name_part and len(name_part) > 2:
                    return name_part
            
            # If line looks like a name (2-3 words, no special chars)
            if re.match(r'^[A-Za-z]{2,}(?:\s+[A-Za-z]{2,}){1,2}$', line):
                return line
        
        # Fallback: use email username
        email = self._extract_email(text)
        if email != "No email found":
            username = email.split('@')[0]
            return username.replace('.', ' ').title()
        
        return "Candidate"
    
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
        
        max_exp = 0.0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                exp = float(match)
                if exp > max_exp:
                    max_exp = exp
        
        return max_exp
    
    def _extract_education_simple(self, text: str) -> str:
        """Simple education extraction without spaCy"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'mba', 'bs', 'ms', 'ba', 'ma',
            'university', 'college', 'degree', 'graduated'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                return line.strip()[:80]  # Limit length
        
        return "Education not specified"
