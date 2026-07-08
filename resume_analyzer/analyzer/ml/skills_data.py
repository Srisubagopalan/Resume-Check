"""
Static knowledge base used by the NLP engine.

Contains categorized technical/soft skills, section header synonyms,
and degree/education keywords. Kept as plain Python data structures so
the whole project runs with zero external model downloads.
"""

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "dart",
    ],
    "Web Development": [
        "html", "css", "sass", "scss", "react", "reactjs", "angular", "vue", "vuejs",
        "django", "flask", "fastapi", "node.js", "nodejs", "express", "next.js", "nextjs",
        "bootstrap", "tailwind", "jquery", "rest api", "restful api", "graphql", "webpack",
    ],
    "Data Science & ML": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "data science", "data analysis", "data visualization",
        "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch", "pandas", "numpy",
        "matplotlib", "seaborn", "opencv", "neural network", "cnn", "rnn", "lstm",
        "transformer", "regression", "classification", "clustering", "feature engineering",
        "statistics", "statistical analysis", "a/b testing", "predictive modeling",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle",
        "redis", "elasticsearch", "firebase", "cassandra", "dynamodb", "nosql",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins",
        "ci/cd", "terraform", "ansible", "linux", "git", "github", "gitlab",
        "microservices", "devops", "nginx", "apache",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving", "problem-solving",
        "critical thinking", "time management", "adaptability", "collaboration",
        "project management", "creativity", "attention to detail", "analytical skills",
        "presentation", "mentoring", "negotiation",
    ],
    "Tools & Platforms": [
        "jira", "confluence", "slack", "figma", "postman", "vs code", "visual studio",
        "excel", "power bi", "tableau", "jupyter", "google colab", "android studio",
    ],
}

# Flat set for quick membership checks
ALL_SKILLS = sorted({s for group in SKILL_CATEGORIES.values() for s in group})

SECTION_SYNONYMS = {
    "contact": ["contact", "contact information", "personal details"],
    "summary": ["summary", "objective", "profile", "about me", "career objective"],
    "education": ["education", "academic background", "academic qualifications", "qualification"],
    "experience": ["experience", "work experience", "employment history", "professional experience",
                   "internship", "internships", "work history"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "expertise"],
    "projects": ["projects", "academic projects", "personal projects", "key projects"],
    "certifications": ["certifications", "certificates", "courses", "licenses"],
    "achievements": ["achievements", "awards", "accomplishments", "honors"],
}

DEGREE_KEYWORDS = [
    "b.tech", "b.e", "bachelor", "b.sc", "bsc", "bca", "b.com",
    "m.tech", "mtech", "m.e", "master", "m.sc", "msc", "mca", "m.com", "mba",
    "phd", "ph.d", "diploma", "12th", "10th", "high school", "hsc", "ssc",
]

ACTION_VERBS = [
    "developed", "designed", "implemented", "led", "built", "created", "managed",
    "analyzed", "optimized", "improved", "automated", "collaborated", "deployed",
    "engineered", "architected", "launched", "streamlined", "reduced", "increased",
    "spearheaded", "coordinated", "mentored", "delivered", "researched",
]

WEAK_PHRASES = [
    "responsible for", "hard working", "hard-working", "team player",
    "detail oriented", "self motivated", "good communication skill",
]
