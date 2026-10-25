import os
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import (
    User,
    Resume,
    Course,
    Lesson,
    Progress,
    Placement,
    Interview
)


# Default Curated Placement Opportunities to seed if table is empty
DEFAULT_PLACEMENTS_SEED = [
    {
        "company_name": "CloudSphere Systems",
        "job_title": "Senior Full-Stack Engineer",
        "location": "San Francisco, CA • Remote",
        "job_type": "Full-time",
        "salary": "$130,000 - $160,000 / yr",
        "skills_required": "Python, FastAPI, React, PostgreSQL, Docker",
        "description": "Architect scalable microservices and build user-centric dashboards. Work closely with product teams to design scalable APIs and modern frontends.",
        "application_url": "https://careers.example.com/fullstack-engineer"
    },
    {
        "company_name": "DataPulse AI",
        "job_title": "Backend FastAPI Developer",
        "location": "New York, NY • Hybrid",
        "job_type": "Full-time",
        "salary": "$120,000 - $145,000 / yr",
        "skills_required": "Python, FastAPI, Redis, SQLAlchemy, AWS",
        "description": "Build high-throughput data processing endpoints. Responsible for API performance optimization, security, and cloud deployment pipelines.",
        "application_url": "https://careers.example.com/backend-developer"
    },
    {
        "company_name": "NextGen Digital",
        "job_title": "Frontend React Specialist",
        "location": "Austin, TX • Remote",
        "job_type": "Remote",
        "salary": "$110,000 - $135,000 / yr",
        "skills_required": "React, JavaScript, TypeScript, Tailwind CSS, Vite",
        "description": "Craft sleek, responsive web applications with state-of-the-art UI/UX standards and high-speed client interactions.",
        "application_url": "https://careers.example.com/frontend-specialist"
    },
    {
        "company_name": "NeuralLabs AI",
        "job_title": "AI Infrastructure Engineer",
        "location": "Seattle, WA • On-site",
        "job_type": "Full-time",
        "salary": "$140,000 - $180,000 / yr",
        "skills_required": "Python, PyTorch, Docker, Kubernetes, MLOps",
        "description": "Build model inference pipelines and scalable GPU cluster workloads for generative AI enterprise solutions.",
        "application_url": "https://careers.example.com/ai-engineer"
    },
    {
        "company_name": "Innovate Software",
        "job_title": "Software Engineering Intern",
        "location": "Remote",
        "job_type": "Internship",
        "salary": "$45 / hr",
        "skills_required": "JavaScript, Python, Git, HTML, CSS",
        "description": "Hands-on experience building production features alongside senior mentors across web and backend systems.",
        "application_url": "https://careers.example.com/internship"
    },
    {
        "company_name": "Google",
        "job_title": "Associate Software Engineer",
        "location": "Mountain View, CA • Hybrid",
        "job_type": "Full-time",
        "salary": "$145,000 - $185,000 / yr",
        "skills_required": "Python, Java, C++, Algorithms, System Design",
        "description": "Develop next-generation technologies that change how billions of users connect, explore, and interact with information and apps.",
        "application_url": "https://careers.google.com/jobs"
    },
    {
        "company_name": "Microsoft",
        "job_title": "Cloud Applications Developer",
        "location": "Redmond, WA • Hybrid",
        "job_type": "Full-time",
        "salary": "$135,000 - $170,000 / yr",
        "skills_required": "Python, React, TypeScript, Azure, Docker",
        "description": "Deliver cloud-native software powering Azure and Microsoft 365 solutions with strong emphasis on reliability and clean design.",
        "application_url": "https://careers.microsoft.com"
    }
]


def ensure_placements_seeded(db: Session) -> List[Placement]:
    """Ensure the placements table has records; auto-seed standard records if empty."""
    existing = db.query(Placement).all()
    if existing:
        return existing

    seeded = []
    for item in DEFAULT_PLACEMENTS_SEED:
        p = Placement(
            company_name=item["company_name"],
            job_title=item["job_title"],
            location=item.get("location"),
            job_type=item.get("job_type"),
            salary=item.get("salary"),
            skills_required=item.get("skills_required"),
            description=item.get("description"),
            application_url=item.get("application_url")
        )
        db.add(p)
        seeded.append(p)
    db.commit()
    for p in seeded:
        db.refresh(p)
    return seeded


def parse_string_or_json_list(raw_value: Optional[str]) -> List[Any]:
    """Safely parse a field that might be JSON array or delimited text."""
    if not raw_value or not raw_value.strip():
        return []

    val = raw_value.strip()
    if (val.startswith("[") and val.endswith("]")) or (val.startswith("{") and val.endswith("}")):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
        except Exception:
            pass

    # Fallback to comma/semicolon/newline separation
    parts = re.split(r"[,;\n\r]+", val)
    return [p.strip() for p in parts if p.strip()]


def extract_skills_from_text(text: str) -> List[str]:
    """Extract standard clean skill names from a string."""
    raw_list = parse_string_or_json_list(text)
    clean_skills = []
    for item in raw_list:
        if isinstance(item, str):
            s = item.strip()
            if s and s not in clean_skills:
                clean_skills.append(s)
        elif isinstance(item, dict) and "name" in item:
            s = str(item["name"]).strip()
            if s and s not in clean_skills:
                clean_skills.append(s)
    return clean_skills


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison (e.g. 'React.js' -> 'react', 'fastapi' -> 'fastapi')."""
    s = skill.lower().strip()
    s = re.sub(r"\.js$", "", s)
    s = re.sub(r"[\s\-_]+", "", s)
    return s


TECH_ALIASES = {
    "sql": {"postgresql", "postgres", "mysql", "sqlite", "sql"},
    "postgres": {"postgresql", "postgres", "sql"},
    "postgresql": {"postgresql", "postgres", "sql"},
    "js": {"javascript", "js", "ecmascript"},
    "javascript": {"javascript", "js"},
    "ts": {"typescript", "ts"},
    "typescript": {"typescript", "ts"},
    "py": {"python", "python3", "py"},
    "python": {"python", "python3", "py"},
    "react": {"react", "reactjs", "react.js"},
    "node": {"node", "nodejs", "node.js"},
    "nodejs": {"node", "nodejs", "node.js"},
}


def skills_match(skill_a: str, skill_b: str) -> bool:
    """Determine if two skill strings refer to the same skill."""
    norm_a = normalize_skill(skill_a)
    norm_b = normalize_skill(skill_b)
    if norm_a == norm_b:
        return True

    # Check aliases
    for key, group in TECH_ALIASES.items():
        if norm_a in group and norm_b in group:
            return True

    if norm_a in norm_b or norm_b in norm_a:
        if len(norm_a) >= 4 and len(norm_b) >= 4:
            return True
    return False


def build_student_profile(user_id: int, db: Session) -> Dict[str, Any]:
    """Build a comprehensive, normalized profile from CodeSphere PostgreSQL database."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    resume = db.query(Resume).filter(Resume.user_id == user_id).first()

    # Learning Progress & LMS Courses
    all_courses = db.query(Course).all()
    all_lessons = db.query(Lesson).all()
    user_progress = db.query(Progress).filter(Progress.user_id == user_id).all()

    progress_by_lesson = {p.lesson_id: p.completion_percentage for p in user_progress}

    completed_courses = []
    courses_in_progress = []
    course_progress_map = {}

    for course in all_courses:
        course_lessons = [l for l in all_lessons if l.course_id == course.id]
        if not course_lessons:
            continue
        total_lessons = len(course_lessons)
        completed_lessons = sum(1 for l in course_lessons if progress_by_lesson.get(l.id, 0) >= 100)
        avg_course_pct = sum(progress_by_lesson.get(l.id, 0) for l in course_lessons) / total_lessons

        course_progress_map[course.id] = {
            "id": course.id,
            "title": course.title,
            "category": course.category,
            "completion": round(avg_course_pct, 1),
            "completed": avg_course_pct >= 99.9 or completed_lessons == total_lessons
        }

        if avg_course_pct >= 99.9 or completed_lessons == total_lessons:
            completed_courses.append(course.title)
        elif avg_course_pct > 0:
            courses_in_progress.append(course.title)

    overall_progress_val = (
        sum(p.completion_percentage for p in user_progress) / len(user_progress)
        if user_progress else 0.0
    )

    # Resume parsing
    resume_skills = []
    resume_projects = []
    resume_experiences = []
    resume_education = []
    resume_certifications = []
    career_goal = ""
    resume_location = ""
    resume_full_name = user.username

    resume_exists = resume is not None

    if resume:
        resume_full_name = resume.full_name or user.username
        career_goal = resume.career_objective or ""
        resume_location = resume.location or ""

        # Skills
        resume_skills = extract_skills_from_text(resume.skills or "")

        # Projects
        raw_projects = parse_string_or_json_list(resume.projects)
        for proj in raw_projects:
            if isinstance(proj, dict):
                resume_projects.append({
                    "title": proj.get("title", "Project"),
                    "tech_stack": proj.get("tech_stack", ""),
                    "description": proj.get("description", "")
                })
            elif isinstance(proj, str):
                resume_projects.append({
                    "title": "Project",
                    "tech_stack": "",
                    "description": proj
                })

        # Experience
        raw_exp = parse_string_or_json_list(resume.experience)
        for exp in raw_exp:
            if isinstance(exp, dict):
                resume_experiences.append({
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "duration": exp.get("duration", ""),
                    "description": exp.get("description", "")
                })
            elif isinstance(exp, str):
                resume_experiences.append({"title": exp, "company": "", "description": ""})

        # Education
        raw_edu = parse_string_or_json_list(resume.education)
        for edu in raw_edu:
            if isinstance(edu, dict):
                resume_education.append({
                    "degree": edu.get("degree", ""),
                    "institution": edu.get("institution", ""),
                    "year": edu.get("year", ""),
                    "score": edu.get("score", "")
                })
            elif isinstance(edu, str):
                resume_education.append({"degree": edu, "institution": ""})

        # Certifications
        if resume.certifications:
            resume_certifications = [
                c.strip() for c in re.split(r"[,;\n]+", resume.certifications) if c.strip()
            ]

    # Interview practice data
    interview_count = db.query(Interview).count()

    # Consolidate overall skills from resume + projects + completed courses
    all_known_skills = list(resume_skills)
    for p in resume_projects:
        ts = p.get("tech_stack", "")
        if ts:
            for s in re.split(r"[,;/\s]+", ts):
                s = s.strip()
                if s and len(s) > 1 and s not in all_known_skills:
                    all_known_skills.append(s)

    for c in completed_courses:
        # Extract keywords like React, Python, FastAPI from course titles
        for token in ["React", "Python", "FastAPI", "JavaScript", "Docker", "Node.js", "SQL", "PostgreSQL", "Java"]:
            if token.lower() in c.lower() and token not in all_known_skills:
                all_known_skills.append(token)

    return {
        "student": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": resume_full_name,
            "career_goal": career_goal,
            "location": resume_location,
            "education": resume_education
        },
        "skills": all_known_skills,
        "resume": {
            "exists": resume_exists,
            "skills": resume_skills,
            "projects": resume_projects,
            "experience": resume_experiences,
            "education": resume_education,
            "certifications": resume_certifications,
            "career_objective": career_goal,
            "location": resume_location,
            "full_name": resume_full_name
        },
        "learning": {
            "total_courses": len(all_courses),
            "completed_courses": completed_courses,
            "courses_in_progress": courses_in_progress,
            "average_progress": round(overall_progress_val, 1),
            "lessons_started": len(user_progress)
        },
        "interview": {
            "questions_available": interview_count
        }
    }


def call_jev_ai_decision_engine(
    state_payload: Dict[str, Any],
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Call the Jev AI (TypeSafe AI) decision engine if API key is configured.
    Returns structured decisions or None if offline / no key provided.
    """
    key = api_key or os.getenv("JEV_AI_API_KEY") or os.getenv("TYPESAFE_API_KEY")
    if not key:
        return None

    api_url = os.getenv("JEV_AI_API_URL", "https://api.typesafe.ai/v1/system_one")

    request_body = {
        "model": "jev-latest",
        "state": json.dumps(state_payload),
        "questions": {
            "evaluation_confidence": {
                "type": "Noul",
                "instructions": "Is the candidate profile sufficiently matched to recommend tech placements?"
            },
            "overall_tier": {
                "type": "Choice",
                "instructions": "Classify candidate overall readiness",
                "options": ["High Readiness", "Moderate Readiness", "Developing"]
            }
        }
    }

    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(request_body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
                "User-Agent": "CodeSphere-PlacementEngine/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                result = json.loads(response.read().decode("utf-8"))
                return result
    except Exception:
        # Fallback to local evaluation gracefully
        return None

    return None


def calculate_placement_recommendations(
    user_id: int,
    db: Session,
    career_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Full pipeline combining CodeSphere PostgreSQL data, Resume data, LMS progress,
    and database Placement records through Jev AI evaluation.
    """
    profile = build_student_profile(user_id, db)
    placements = ensure_placements_seeded(db)
    all_courses = db.query(Course).all()

    student_skills = profile["skills"]
    resume_data = profile["resume"]
    learning_data = profile["learning"]

    # Calculate Resume Strength (0 to 100)
    resume_strength = 0
    if resume_data["exists"]:
        if resume_data["full_name"]: resume_strength += 10
        if resume_data["career_objective"]: resume_strength += 15
        if len(resume_data["skills"]) >= 3: resume_strength += 25
        elif len(resume_data["skills"]) > 0: resume_strength += 15
        if len(resume_data["projects"]) >= 2: resume_strength += 25
        elif len(resume_data["projects"]) == 1: resume_strength += 15
        if len(resume_data["education"]) > 0: resume_strength += 15
        if len(resume_data["certifications"]) > 0: resume_strength += 10
    resume_strength = min(100, resume_strength)

    # Technical Skills Score
    tech_skills_score = min(95, max(30, len(student_skills) * 12 + (15 if len(student_skills) >= 4 else 0)))

    # Learning Progress Score
    learning_score = int(learning_data["average_progress"])
    if len(learning_data["completed_courses"]) > 0:
        learning_score = max(learning_score, 80 + len(learning_data["completed_courses"]) * 5)
    learning_score = min(98, max(25, learning_score))

    # Projects Score
    proj_count = len(resume_data["projects"])
    projects_score = min(95, max(20, proj_count * 35 + (15 if proj_count >= 1 else 0)))

    # Communication / Career Goal Score
    comm_score = 75 if resume_data["career_objective"] else 40

    # Interview Readiness Score
    interview_score = 70 if profile["interview"]["questions_available"] > 0 else 50

    # Overall Placement Readiness
    if resume_data["exists"]:
        overall_readiness = int(
            tech_skills_score * 0.30 +
            resume_strength * 0.25 +
            learning_score * 0.20 +
            projects_score * 0.15 +
            comm_score * 0.05 +
            interview_score * 0.05
        )
    else:
        # Without resume, learning & technical skills carry weight, but capped
        overall_readiness = int(
            tech_skills_score * 0.40 +
            learning_score * 0.35 +
            comm_score * 0.15 +
            interview_score * 0.10
        )
        overall_readiness = min(68, overall_readiness)

    # Evaluate Each Company in PostgreSQL Database
    company_recommendations = []
    missing_skills_agg: Dict[str, List[str]] = {}

    for place in placements:
        req_skills_raw = extract_skills_from_text(place.skills_required or "")
        matched_skills = []
        missing_skills = []

        for req in req_skills_raw:
            matched = any(skills_match(req, st) for st in student_skills)
            if matched:
                matched_skills.append(req)
            else:
                missing_skills.append(req)
                if req not in missing_skills_agg:
                    missing_skills_agg[req] = []
                missing_skills_agg[req].append(place.company_name)

        total_req = len(req_skills_raw)
        if total_req > 0:
            match_pct = int((len(matched_skills) / total_req) * 100)
        else:
            match_pct = 60

        # Adjust match score with resume and project relevance
        # Bonus if project tech stack mentions company requirements
        bonus = 0
        for proj in resume_data["projects"]:
            if any(skills_match(m, proj.get("tech_stack", "")) for m in req_skills_raw):
                bonus += 5
                break

        # Bonus if completed course teaches any required skill
        for comp_c in learning_data["completed_courses"]:
            if any(m.lower() in comp_c.lower() for m in req_skills_raw):
                bonus += 5
                break

        final_match_pct = min(98, max(25, match_pct + bonus))

        # Readiness percentage specifically for this company
        company_readiness = int(
            (final_match_pct * 0.5) + (overall_readiness * 0.5)
        )
        company_readiness = min(96, max(30, company_readiness))

        # Match Tier
        if final_match_pct >= 80:
            match_level = "Strong Match"
        elif final_match_pct >= 65:
            match_level = "Good Match"
        elif final_match_pct >= 45:
            match_level = "Partial Match"
        else:
            match_level = "Low Match"

        # Generate Data-Driven "Why Recommended" Explanation
        reasons = []
        if matched_skills:
            matched_str = ", ".join(matched_skills[:3])
            reasons.append(f"Your profile demonstrates proficiency in {matched_str}")

        if resume_data["exists"] and resume_data["projects"]:
            reasons.append("your portfolio contains relevant project implementations")

        if learning_data["completed_courses"]:
            reasons.append("you completed courses aligned with their engineering requirements")

        if not reasons:
            reasons.append(f"matches your focus in {place.job_title}")

        why_recommended = (
            "Recommended because " + "; and ".join(reasons) + "."
        )

        # Application Readiness Checklist
        app_readiness = {
            "resume": {
                "status": "Ready" if resume_strength >= 70 else ("Needs Improvement" if resume_data["exists"] else "Missing"),
                "detail": f"Resume score: {resume_strength}% ({len(resume_data['skills'])} skills, {len(resume_data['projects'])} projects detected)" if resume_data["exists"] else "Resume not created in Resume Builder"
            },
            "skills": {
                "status": "Ready" if len(matched_skills) >= len(missing_skills) and len(matched_skills) > 0 else "Needs Improvement",
                "detail": f"{len(matched_skills)} of {total_req} required skills verified ({', '.join(matched_skills[:3]) if matched_skills else 'None yet'})"
            },
            "projects": {
                "status": "Ready" if len(resume_data["projects"]) >= 1 else "Needs Improvement",
                "detail": f"{len(resume_data['projects'])} project(s) showcased in portfolio" if resume_data["projects"] else "Add full-stack projects to strengthen application"
            },
            "education": {
                "status": "Ready" if len(resume_data["education"]) > 0 else "Needs Improvement",
                "detail": resume_data["education"][0].get("degree", "Degree added") if resume_data["education"] else "Education details in resume"
            },
            "certifications": {
                "status": "Ready" if len(resume_data["certifications"]) > 0 else "Needs Improvement",
                "detail": f"{len(resume_data['certifications'])} verified certification(s)" if resume_data["certifications"] else "Certifications or course credentials recommended"
            },
            "interview": {
                "status": "Ready" if profile["interview"]["questions_available"] > 0 else "Needs Improvement",
                "detail": f"{profile['interview']['questions_available']} interview prep modules active"
            }
        }

        # Preparation suggestions for this company
        prep_suggestions = []
        if missing_skills:
            prep_suggestions.append(f"Focus on mastering missing technologies: {', '.join(missing_skills)}")
        if not learning_data["completed_courses"]:
            prep_suggestions.append("Complete ongoing CodeSphere LMS courses to earn course completion credentials")
        if not resume_data["exists"] or resume_strength < 75:
            prep_suggestions.append("Tailor your CodeSphere ATS Resume highlighting the matched technical stack")
        prep_suggestions.append(f"Practice technical interview questions in category: {place.job_title}")

        company_recommendations.append({
            "id": place.id,
            "company_name": place.company_name,
            "job_title": place.job_title,
            "location": place.location or "Remote",
            "job_type": place.job_type or "Full-time",
            "salary": place.salary or "Competitive",
            "description": place.description or "",
            "application_url": place.application_url or "#",
            "skills_required": place.skills_required or "",
            "match_percentage": final_match_pct,
            "readiness_percentage": company_readiness,
            "match_level": match_level,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "why_recommended": why_recommended,
            "application_readiness": app_readiness,
            "preparation_suggestions": prep_suggestions
        })

    # Sort ranked companies by match percentage descending
    company_recommendations.sort(key=lambda x: (x["match_percentage"], x["readiness_percentage"]), reverse=True)

    # Optional Jev AI evaluation payload to refine decision tier
    jev_evaluation = call_jev_ai_decision_engine({
        "student": profile["student"],
        "skills": student_skills,
        "resume_strength": resume_strength,
        "learning": learning_data,
        "top_company": company_recommendations[0] if company_recommendations else None
    })

    # Skill Gap Analysis
    skill_gaps = []
    for skill, companies in missing_skills_agg.items():
        # Match against real CodeSphere LMS courses in database
        related_course = None
        for c in all_courses:
            title_lower = (c.title or "").lower()
            desc_lower = (c.description or "").lower()
            skill_lower = skill.lower()
            if skill_lower in title_lower or skill_lower in desc_lower:
                related_course = {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description
                }
                break

        # Priority calculation
        priority = "High Priority" if len(companies) >= 2 else "Medium Priority"

        skill_gaps.append({
            "skill": skill,
            "priority": priority,
            "companies_count": len(companies),
            "companies_requiring": companies,
            "recommended_course": related_course
        })

    # Sort skill gaps by priority
    skill_gaps.sort(key=lambda x: (x["priority"] == "High Priority", x["companies_count"]), reverse=True)

    # Preparation recommendations list
    prep_steps = []
    step_num = 1
    if skill_gaps:
        top_gap = skill_gaps[0]
        rec_course_text = f" via course '{top_gap['recommended_course']['title']}'" if top_gap['recommended_course'] else ""
        prep_steps.append({
            "priority": step_num,
            "title": f"Master {top_gap['skill']}",
            "description": f"High impact skill required by {', '.join(top_gap['companies_requiring'][:2])}{rec_course_text}.",
            "category": "Skill Enhancement"
        })
        step_num += 1

    if not learning_data["completed_courses"]:
        prep_steps.append({
            "priority": step_num,
            "title": "Complete Active LMS Course",
            "description": "Finish your in-progress courses to demonstrate mastery and boost readiness.",
            "category": "Course Progress"
        })
        step_num += 1

    if not resume_data["exists"]:
        prep_steps.append({
            "priority": step_num,
            "title": "Generate CodeSphere ATS Resume",
            "description": "Create your resume with verified projects and skills to unlock higher matching precision.",
            "category": "Resume Builder"
        })
        step_num += 1
    elif resume_strength < 80:
        prep_steps.append({
            "priority": step_num,
            "title": "Enhance Resume Project Descriptions",
            "description": "Quantify project impact and list tools to maximize ATS ranking for top tier employers.",
            "category": "Resume Builder"
        })
        step_num += 1

    prep_steps.append({
        "priority": step_num,
        "title": "Practice Mock Technical Questions",
        "description": "Solve interview questions in system design, async backend, and modern frontend frameworks.",
        "category": "Interview Preparation"
    })

    return {
        "status": "success",
        "student_profile": {
            "name": profile["student"]["name"],
            "email": profile["student"]["email"],
            "career_goal": profile["student"]["career_goal"] or "Full Stack Software Engineer",
            "location": profile["student"]["location"] or "Available for Remote / Hybrid",
            "detected_skills": student_skills,
            "skills_count": len(student_skills)
        },
        "readiness": {
            "overall": overall_readiness,
            "breakdown": {
                "technical_skills": {
                    "score": tech_skills_score,
                    "status": "Strong" if tech_skills_score >= 75 else ("Good" if tech_skills_score >= 50 else "Developing")
                },
                "communication": {
                    "score": comm_score,
                    "status": "Strong" if comm_score >= 70 else "Developing"
                },
                "learning_progress": {
                    "score": learning_score,
                    "status": "Strong" if learning_score >= 75 else ("Good" if learning_score >= 50 else "Developing")
                },
                "projects": {
                    "score": projects_score,
                    "status": "Strong" if projects_score >= 70 else ("Good" if projects_score >= 35 else "Developing")
                },
                "resume_strength": {
                    "score": resume_strength,
                    "status": "Strong" if resume_strength >= 75 else ("Good" if resume_strength >= 50 else "Not Created" if not resume_data["exists"] else "Developing")
                },
                "interview_readiness": {
                    "score": interview_score,
                    "status": "Good" if interview_score >= 60 else "Developing"
                }
            }
        },
        "resume_status": {
            "exists": resume_data["exists"],
            "strength": resume_strength,
            "skills_detected": len(resume_data["skills"]),
            "projects_detected": len(resume_data["projects"]),
            "certifications_detected": len(resume_data["certifications"]),
            "has_objective": bool(resume_data["career_objective"])
        },
        "recommendations": company_recommendations,
        "skill_gap_analysis": skill_gaps,
        "preparation_recommendations": prep_steps,
        "jev_decision": jev_evaluation
    }
