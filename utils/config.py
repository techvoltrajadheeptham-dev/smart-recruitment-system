# Configuration settings for the recruitment system

class Config:
    # Matching weights
    SKILLS_WEIGHT = 0.4
    EXPERIENCE_WEIGHT = 0.3
    SEMANTIC_WEIGHT = 0.2
    KEYWORDS_WEIGHT = 0.1
    
    # Score thresholds
    EXCELLENT_MATCH = 80
    GOOD_MATCH = 60
    POOR_MATCH = 0
    
    # File settings
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Display settings
    TOP_CANDIDATES_DISPLAY = 10
    SCORE_DECIMAL_PLACES = 1