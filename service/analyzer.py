# The resume analyzer. It reads the file, finds the facts, scores the resume
# and saves the result. Everything is done with simple rules and word lists.
import json
import re
from datetime import datetime

from pypdf import PdfReader

from extension import db
from model.model import Submission
from service.skills_data import (
    ALL_SKILLS, FIELD_SKILL_MAP, FIELD_SKILL_EXTRAS, FIELD_COURSES,
    SECTION_HEADERS, DEGREE_KEYWORDS,
)


# ------------------------------------------------------------------
# 1. Reading the uploaded file
# ------------------------------------------------------------------

def read_resume_file(file):
    """Return (text, page_count). Raises ValueError with a friendly message."""
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        text = file.read().decode("utf-8", errors="ignore")
        page_count = None
    elif filename.endswith(".pdf"):
        try:
            reader = PdfReader(file.stream)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            page_count = len(reader.pages)
        except Exception:
            raise ValueError("That PDF could not be read. Please try another file.")
    else:
        raise ValueError("Only PDF and TXT files are supported.")

    if not text.strip():
        raise ValueError("No readable text was found in that file.")
    return text, page_count


# ------------------------------------------------------------------
# 2. Small helpers
# ------------------------------------------------------------------

def round_half_up(number):
    return int(number + 0.5)


def has_word(text, phrase):
    """True if the phrase appears in the text as a whole word."""
    pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    return re.search(pattern, text, re.IGNORECASE) is not None


def clean_text(raw):
    text = raw.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_lines(text):
    lines = [line.strip() for line in text.split("\n")]
    return [line for line in lines if line]


# ------------------------------------------------------------------
# 3. Finding the facts
# ------------------------------------------------------------------

EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?){2,4}\d{3,4}"
LINKEDIN_PATTERN = r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9\-_/%]+"
GITHUB_PATTERN = r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/%]+"


def find_contact(text):
    email = re.search(EMAIL_PATTERN, text)
    linkedin = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    github = re.search(GITHUB_PATTERN, text, re.IGNORECASE)

    phone = None
    for match in re.finditer(PHONE_PATTERN, text):
        digits = re.sub(r"\D", "", match.group(0))
        if 9 <= len(digits) <= 13:
            phone = match.group(0).strip()
            break

    return {
        "email": email.group(0) if email else None,
        "phone": phone,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
    }


def find_name(lines):
    all_headers = [h for group in SECTION_HEADERS.values() for h in group]

    for line in lines[:6]:
        if re.search(EMAIL_PATTERN, line) or "http" in line.lower():
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.fullmatch(r"[A-Za-z.\-]+", w) for w in words):
            lower = line.lower()
            if not any(lower.startswith(h) for h in all_headers):
                return re.sub(r"\w\S*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), line)
    return "Not detected"


def header_name(line):
    """If the line is a section title (like 'Education'), return the section name."""
    cleaned = re.sub(r"[^a-z\s]", "", line.lower()).strip()
    if not cleaned or len(cleaned.split()) > 5:
        return None
    for section, phrases in SECTION_HEADERS.items():
        for phrase in phrases:
            if cleaned == phrase or cleaned.startswith(phrase):
                return section
    return None


def split_into_sections(lines):
    sections = {"header_block": []}
    current = "header_block"
    for line in lines:
        found = header_name(line)
        if found:
            current = found
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def find_skills(text_lower):
    return sorted(skill for skill in ALL_SKILLS if has_word(text_lower, skill))


def find_education(sections, text_lower):
    degrees = [d for d in DEGREE_KEYWORDS if has_word(text_lower, d)]
    return {"degrees_found": degrees, "raw_lines": sections.get("education", [])}


MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december"
DATE_RANGE_PATTERN = (
    r"(?:(?:" + MONTHS + r")[a-z]*\.?\s+)?(\d{4})\s*(?:-|to|–|—)\s*"
    r"(?:(?:(?:" + MONTHS + r")[a-z]*\.?\s+)?(\d{4})|present|current|till date|now)"
)
YEARS_PATTERN = r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience"


def find_experience_years(text):
    # Case 1: the resume says "3 years of experience"
    said = re.search(YEARS_PATTERN, text, re.IGNORECASE)
    if said:
        return float(said.group(1))

    # Case 2: add up the date ranges like "2021 - 2023"
    this_year = datetime.now().year
    total_months = 0
    for match in re.finditer(DATE_RANGE_PATTERN, text, re.IGNORECASE):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else this_year
        if 1980 <= start <= this_year and start <= end <= this_year:
            total_months += max((end - start) * 12, 1)
    return round_half_up((total_months / 12) * 10) / 10


def level_from_years(years):
    if years >= 6:
        return "Senior"
    if years >= 3:
        return "Experienced"
    if years >= 1:
        return "Junior"
    return "Fresher"


def predict_field(skills):
    best_field = "General"
    best_count = 0
    for field, field_skills in FIELD_SKILL_MAP.items():
        count = len([s for s in field_skills if s in skills])
        if count > best_count:
            best_count = count
            best_field = field
    return best_field


# ------------------------------------------------------------------
# 4. Scoring, matching and advice
# ------------------------------------------------------------------

def score_resume(contact, skills, education, years, sections_found):
    contact_score = (5 if contact["email"] else 0) + (5 if contact["phone"] else 0)
    skills_score = min(len(skills) * 3, 30)
    has_education = education["degrees_found"] or education["raw_lines"]
    education_score = 20 if has_education else 0
    experience_score = min(years * 4, 20)
    structure_score = min((sections_found / 5) * 20, 20)
    total = round_half_up(contact_score + skills_score + education_score + experience_score + structure_score)
    return min(total, 100)


def match_job_description(skills, job_description):
    """Return the % of the job's skills that the resume has, or None."""
    if not job_description or not job_description.strip():
        return None
    job_text = job_description.lower()
    job_skills = [s for s in ALL_SKILLS if has_word(job_text, s)]
    if not job_skills:
        return None
    matched = [s for s in job_skills if s in skills]
    return round_half_up(len(matched) / len(job_skills) * 1000) / 10


def recommend_skills(field, skills):
    pool = list(FIELD_SKILL_MAP.get(field, [])) + list(FIELD_SKILL_EXTRAS.get(field, FIELD_SKILL_EXTRAS["General"]))
    wanted = []
    for skill in pool:
        if skill not in skills and skill not in wanted:
            wanted.append(skill)
    return wanted[:8]


def make_tips(contact, sections, total_words, skills):
    tips = []
    if not contact["phone"]:
        tips.append("Add a phone number so recruiters can reach you directly.")
    if not contact["linkedin"]:
        tips.append("Include a LinkedIn profile link to strengthen your professional presence.")
    if not sections.get("projects"):
        tips.append("Add a Projects section to showcase hands-on work.")
    if not sections.get("certifications"):
        tips.append("Consider adding relevant certifications to stand out.")
    if total_words < 200:
        tips.append("Your resume looks short — consider adding more detail about your achievements.")
    if len(skills) < 5:
        tips.append("List more of your technical skills to improve keyword matching with job descriptions.")
    tips.append('Use quantifiable achievements (e.g. "increased efficiency by 20%") wherever possible.')

    if len(tips) == 1:
        return ["Your resume looks strong! Keep it updated as you gain new skills."]
    return tips[:5]


def verdict_from_score(score):
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Needs work"


# ------------------------------------------------------------------
# 5. The main steps used by the routes
# ------------------------------------------------------------------

def analyse(raw_text, job_description, page_count):
    text = clean_text(raw_text)
    lines = get_lines(text)
    text_lower = text.lower()

    contact = find_contact(text)
    sections = split_into_sections(lines)
    skills = find_skills(text_lower)
    education = find_education(sections, text_lower)
    years = find_experience_years(text)
    field = predict_field(skills)

    core_sections = ["summary", "education", "experience", "skills", "projects"]
    sections_found = len([s for s in core_sections if sections.get(s)])

    score = score_resume(contact, skills, education, years, sections_found)
    total_words = len(text.split())

    return {
        "name": find_name(lines),
        "contact": contact,
        "skills": skills,
        "education": education,
        "level": level_from_years(years),
        "field": field,
        "score": score,
        "verdict": verdict_from_score(score),
        "jd_match": match_job_description(skills, job_description),
        "pages": page_count or max(1, -(-total_words // 500)),
        "recommended_skills": recommend_skills(field, skills),
        "recommended_courses": FIELD_COURSES.get(field, FIELD_COURSES["General"]),
        "tips": make_tips(contact, sections, total_words, skills),
    }


def save_submission(result):
    """Save the analysis in the database and return the new row's id."""
    row = Submission(
        name=result["name"][:200],
        email=(result["contact"]["email"] or "Not found")[:200],
        score=result["score"],
        field=result["field"],
        level=result["level"],
        result_json=json.dumps(result),
    )
    db.session.add(row)
    db.session.commit()
    return row.id


def dashboard_numbers():
    """Return (all rows newest first, count, average score, top field)."""
    rows = Submission.query.order_by(Submission.created_at.desc()).all()
    count = len(rows)
    average = round(sum(r.score for r in rows) / count, 1) if count else 0.0

    top_field = "-"
    top_count = 0
    for field in set(r.field for r in rows):
        field_count = len([r for r in rows if r.field == field])
        if field_count > top_count:
            top_field = field
            top_count = field_count
    return rows, count, average, top_field
