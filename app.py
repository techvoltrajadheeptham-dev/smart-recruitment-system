import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.resume_parser import ResumeParser
from utils.matcher import CandidateMatcher
import base64
import time
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Smart Recruitment System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .match-high { background-color: #d4edda; }
    .match-medium { background-color: #fff3cd; }
    .match-low { background-color: #f8d7da; }
    </style>
    """, unsafe_allow_html=True)

class RecruitmentApp:
    def __init__(self):
        self.parser = ResumeParser()
        self.matcher = CandidateMatcher()
        load_css()
        
    def run(self):
        # Sidebar
        st.sidebar.title("💼 Smart Recruitment")
        st.sidebar.markdown("---")
        
        menu = st.sidebar.selectbox("Navigation", 
            ["🏠 Dashboard", "📊 Candidate Matching", "👥 Candidate Pool", "⚙️ Settings"])
        
        # Main content
        if menu == "🏠 Dashboard":
            self.show_dashboard()
        elif menu == "📊 Candidate Matching":
            self.show_matching()
        elif menu == "👥 Candidate Pool":
            self.show_candidate_pool()
        elif menu == "⚙️ Settings":
            self.show_settings()
    
    def show_dashboard(self):
        st.markdown('<h1 class="main-header">Smart Recruitment Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", "156", "12%")
        with col2:
            st.metric("Shortlisted", "23", "8%")
        with col3:
            st.metric("Avg. Match Score", "76%", "5%")
        with col4:
            st.metric("Time Saved", "42 hrs", "15%")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Skills distribution
            skills_data = {
                'Skill': ['Python', 'Java', 'SQL', 'AWS', 'React', 'ML'],
                'Count': [45, 32, 38, 28, 25, 20]
            }
            fig = px.bar(skills_data, x='Skill', y='Count', 
                        title="Top Skills Distribution", color='Count')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Match score distribution
            scores = [85, 92, 78, 65, 88, 72, 95, 81, 69, 87]
            fig = px.histogram(x=scores, nbins=10, 
                             title="Candidate Match Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def show_matching(self):
        st.title("🎯 Candidate Matching")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Job Description")
            job_description = st.text_area(
                "Paste job description here:",
                height=300,
                placeholder="Enter the job description including required skills, experience, and qualifications..."
            )
            
            st.subheader("Upload Resumes")
            uploaded_files = st.file_uploader(
                "Choose resume files",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True,
                help="Upload multiple resumes in PDF, DOCX, or TXT format"
            )
            
            if st.button("🚀 Match Candidates", type="primary"):
                if job_description and uploaded_files:
                    self.process_matching(job_description, uploaded_files)
                else:
                    st.error("Please provide both job description and resumes.")
        
        with col2:
            st.subheader("Matching Results")
            if 'matching_results' in st.session_state:
                self.display_results(st.session_state.matching_results)
    
    def process_matching(self, job_description, uploaded_files):
        with st.spinner("Analyzing resumes and matching candidates..."):
            progress_bar = st.progress(0)
            candidates_data = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Save uploaded file temporarily
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse resume
                resume_data = self.parser.parse_resume(file_path)
                resume_data['filename'] = uploaded_file.name
                
                # Calculate match score
                match_result = self.matcher.calculate_match(resume_data, job_description)
                candidates_data.append(match_result)
                
                # Update progress
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                
                # Clean up
                os.remove(file_path)
            
            st.session_state.matching_results = candidates_data
            st.success(f"Successfully processed {len(uploaded_files)} resumes!")
    
    def display_results(self, results):
        # Create DataFrame for display
        df_data = []
        for result in results:
            df_data.append({
                'Candidate': result['name'],
                'Email': result['email'],
                'Match Score': f"{result['match_score']:.1f}%",
                'Skills Match': f"{result['skills_match']:.1f}%",
                'Experience': result['experience'],
                'Status': self.get_status(result['match_score'])
            })
        
        df = pd.DataFrame(df_data)
        
        # Display metrics
        avg_score = sum(r['match_score'] for r in results) / len(results)
        top_score = max(r['match_score'] for r in results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col2:
            st.metric("Top Score", f"{top_score:.1f}%")
        with col3:
            st.metric("Candidates Processed", len(results))
        
        # Display results table
        st.dataframe(df, use_container_width=True)
        
        # Detailed view
        st.subheader("Candidate Details")
        for result in sorted(results, key=lambda x: x['match_score'], reverse=True):
            with st.expander(f"{result['name']} - {result['match_score']:.1f}% Match"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {result['email']}")
                    st.write(f"**Phone:** {result['phone']}")
                    st.write(f"**Experience:** {result['experience']} years")
                
                with col2:
                    st.write(f"**Skills Match:** {result['skills_match']:.1f}%")
                    st.write(f"**Education:** {result['education']}")
                
                # Skills
                st.write("**Key Skills:**")
                for skill in result['skills'][:10]:
                    st.write(f"• {skill}")
    
    def get_status(self, score):
        if score >= 80:
            return "🟢 Excellent"
        elif score >= 60:
            return "🟡 Good"
        else:
            return "🔴 Needs Review"
    
    def show_candidate_pool(self):
        st.title("👥 Candidate Pool")
        st.info("This feature will show all processed candidates across multiple job matches.")
    
    def show_settings(self):
        st.title("⚙️ System Settings")
        st.write("Configure matching parameters and system preferences.")
        
        st.subheader("Matching Weights")
        skills_weight = st.slider("Skills Weight", 0.0, 1.0, 0.4)
        experience_weight = st.slider("Experience Weight", 0.0, 1.0, 0.3)
        education_weight = st.slider("Education Weight", 0.0, 1.0, 0.2)
        keywords_weight = st.slider("Keywords Weight", 0.0, 1.0, 0.1)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

if __name__ == "__main__":
    app = RecruitmentApp()
    app.run()