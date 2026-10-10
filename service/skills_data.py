# The rules the analyzer uses. Every list here is a plain dictionary of words.
# To teach the analyzer something new, just add a word to a list.

# Flat list of every skill the engine can detect (used for tag detection
# and for job-description keyword matching).
ALL_SKILLS = [
    # Programming languages
    "python", "java", "c++", "c#", "javascript", "typescript", "php", "ruby",
    "go", "golang", "swift", "kotlin", "r", "matlab", "scala", "perl", "c",
    "dart", "rust", "sql", "html", "css",
    # Web technologies
    "react", "angular", "vue", "node.js", "nodejs", "express", "django",
    "flask", "spring", "spring boot", "asp.net", ".net", "jquery",
    "bootstrap", "tailwind", "next.js", "graphql", "rest api", "restful",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
    "cassandra", "firebase", "dynamodb", "mariadb", "sql server",
    # Data science / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "opencv", "data analysis", "data visualization", "computer vision",
    "artificial intelligence", "neural network", "matplotlib", "seaborn",
    "statistics", "tableau", "power bi",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "jenkins", "ci/cd", "terraform", "ansible", "linux", "git", "github",
    "gitlab", "devops", "microservices",
    # Tools / other
    "excel", "jira", "figma", "photoshop", "postman", "vs code",
    "eclipse", "android studio", "unity",
    # Mobile
    "flutter",
    # Soft skills
    "communication", "leadership", "teamwork", "problem solving",
    "time management", "adaptability", "creativity", "collaboration",
    "critical thinking", "project management",
]

# Skills grouped by professional field, used only to PREDICT the field —
# a skill may legitimately appear in more than one field's list.
FIELD_SKILL_MAP = {
    "Data Science": [
        "python", "r", "matlab", "pandas", "numpy", "scikit-learn",
        "tensorflow", "pytorch", "keras", "matplotlib", "seaborn",
        "data visualization", "data analysis", "machine learning",
        "deep learning", "nlp", "natural language processing",
        "computer vision", "artificial intelligence", "neural network",
        "statistics", "tableau", "power bi", "opencv",
    ],
    "Web Development": [
        "html", "css", "javascript", "typescript", "react", "angular",
        "vue", "node.js", "nodejs", "express", "django", "flask", "php",
        "asp.net", ".net", "jquery", "bootstrap", "tailwind", "next.js",
        "graphql", "rest api", "restful", "ruby", "spring boot", "spring",
    ],
    "Software Engineering": [
        "java", "c++", "c#", "c", "go", "golang", "rust", "scala", "perl",
        "git", "github", "gitlab", "python",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "jenkins", "ci/cd", "terraform", "ansible", "linux", "devops",
        "microservices",
    ],
    "Database & Data Engineering": [
        "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
        "cassandra", "firebase", "dynamodb", "mariadb", "sql server", "sql",
    ],
    "Mobile Development": [
        "android studio", "swift", "kotlin", "dart", "flutter", "unity",
    ],
    "Design": [
        "figma", "photoshop",
    ],
}

# Extra, more-advanced skills suggested per field when recommending
# "skills to add" (on top of each field's own skill list above).
FIELD_SKILL_EXTRAS = {
    "Data Science": ["r programming", "deep learning", "data analysis", "tensorflow", "keras", "pytorch", "seaborn", "nlp"],
    "Web Development": ["typescript", "next.js", "graphql", "docker", "rest api", "tailwind", "jest", "ci/cd"],
    "Software Engineering": ["data structures", "algorithms", "system design", "unit testing", "git", "docker", "ci/cd", "design patterns"],
    "Cloud & DevOps": ["kubernetes", "terraform", "ansible", "ci/cd", "monitoring", "aws", "azure", "linux"],
    "Database & Data Engineering": ["data modeling", "etl pipelines", "sql optimization", "mongodb", "redis", "data warehousing"],
    "Mobile Development": ["flutter", "kotlin", "swift", "firebase", "rest api", "ui testing"],
    "Design": ["figma", "user research", "wireframing", "prototyping", "accessibility", "design systems"],
    "General": ["communication", "project management", "problem solving", "time management"],
}

# Recommended courses per predicted field.
FIELD_COURSES = {
    "Data Science": ["Python for Data Science", "Machine Learning Specialization", "Data Analysis with Pandas"],
    "Web Development": ["The Complete Web Developer Course", "React – The Complete Guide", "Node.js, Express & MongoDB"],
    "Software Engineering": ["Data Structures & Algorithms", "Clean Code & Software Design", "Git & GitHub Essentials"],
    "Cloud & DevOps": ["AWS Certified Cloud Practitioner", "Docker & Kubernetes Essentials", "CI/CD with Jenkins"],
    "Database & Data Engineering": ["SQL for Data Analysis", "Database Design Fundamentals", "MongoDB Basics"],
    "Mobile Development": ["Android App Development", "iOS Development with Swift", "Flutter & Dart Bootcamp"],
    "Design": ["UI/UX Design Fundamentals", "Figma for Beginners", "Adobe Photoshop Essentials"],
    "General": ["Effective Resume Writing", "Professional Communication Skills", "Introduction to Programming"],
}

# Section-header rule base: canonical section -> phrases that introduce it.
SECTION_HEADERS = {
    "summary": ["summary", "objective", "profile", "about me", "career objective"],
    "education": ["education", "academic background", "academic qualification", "qualifications"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "internship", "internships"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "awards", "accomplishments", "honors"],
    "publications": ["publications", "research papers"],
}

# Degree keyword rule base.
DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "bachelor of technology", "bachelor of engineering",
    "bachelor of science", "b.sc", "bsc", "bachelor of arts", "b.a",
    "bachelor of commerce", "b.com", "bca", "bachelor of computer application",
    "m.tech", "mtech", "master of technology", "master of engineering", "m.e",
    "master of science", "m.sc", "msc", "mba", "master of business administration",
    "mca", "master of computer application", "phd", "ph.d", "doctorate",
    "hnd", "higher national diploma", "diploma", "high school", "hsc", "ssc",
]

