from typing import Dict, List

# Base message templates for all agents
SYSTEM_BASE = """You are the {agent_name}. {role_description}"""

# Admin Agent Messages
ADMIN_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="Job Requirements Agent",
        role_description="You are an expert HR hiring manager orchestrating the resume screening process."
    ),
    "human": """Please review this resume{job_req_section} for evaluation:
{resume_section}""",
    "ai": """I acknowledge receipt of{job_req_acknowledgment} the Resume.

{requirements_section}
Delegating to specialist agents...

Delegation complete. I will synthesize the reports in my next turn after the specialist agents have provided their input.""",
    "ai_follow_up": """All specialist reports have been received. Proceeding with final evaluation.

{evaluation_summary}"""
}

# Add default formatters for admin messages
ADMIN_DEFAULT_FORMATTERS = {
    "job_req_section": lambda jr: f" and job requirements:\n\nJob Requirements:\n{jr}" if jr else "",
    "resume_section": lambda r: f"Resume:\n{r}" if r else "",
    "job_req_acknowledgment": lambda jr: " the Job Requirements and" if jr else "",
    "requirements_section": lambda ra: f"Requirements Analysis:\n{ra}\n\n" if ra else ""
}

# Experience Agent Messages
EXPERIENCE_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="ExperienceCheckAgent",
        role_description="You specialize in analyzing the experience section of resumes."
    ),
    "human": """Please analyze this experience requirement against the resume:

Requirement:
{requirement}

Resume:
{resume}""",
    "ai": """**Experience Analysis:**
*   **Requirement:** {requirement}
*   **Candidate's Relevant Experience:** {experience_duration}
*   **Assessment:** {assessment}
*   **Supporting Evidence:**
{evidence}
*   **Comments:** {comments}"""
}

# Skills Agent Messages
SKILLS_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="SkillsCheckAgent",
        role_description="You specialize in identifying and assessing technical skills in resumes."
    ),
    "human": """Please analyze these required skills against the resume:

Required Skills:
{required_skills}

Resume:
{resume}""",
    "ai": """**Skills Analysis:**
{skills_analysis}
**Bonus Skills:**
{bonus_skills}
**Overall Skills Summary:** {summary}"""
}

# Project Agent Messages
PROJECT_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="ProjectCheckAgent",
        role_description="You specialize in analyzing projects to identify skills and assess complexity."
    ),
    "human": """Please analyze the projects section in this resume:

Resume:
{resume}""",
    "ai": """**Projects Analysis:**
{projects_analysis}
**Overall Project Assessment:** {assessment}"""
}

# Education Agent Messages
EDUCATION_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="EducationCheckAgent",
        role_description="You specialize in analyzing educational qualifications and identifying gaps."
    ),
    "human": """Please analyze the education section in this resume:

Resume:
{resume}""",
    "ai": """**Education Analysis:**
{education_analysis}
**Overall Assessment:** {assessment}"""
}

# Certifications Agent Messages
CERTIFICATIONS_MESSAGES = {
    "system": SYSTEM_BASE.format(
        agent_name="CertificationsCheckAgent",
        role_description="You specialize in analyzing certifications and their relevance."
    ),
    "human": """Please analyze the certifications in this resume:

Resume:
{resume}""",
    "ai": """**Certifications Analysis:**
{certifications_analysis}
**Overall Value Add:** {assessment}"""
}

MESSAGES = {
    "admin": ADMIN_MESSAGES,
    "experience": EXPERIENCE_MESSAGES,
    "skills": SKILLS_MESSAGES,
    "project": PROJECT_MESSAGES,
    "education": EDUCATION_MESSAGES,
    "certifications": CERTIFICATIONS_MESSAGES
}

# Default formatters for all agents
DEFAULT_FORMATTERS = {
    "admin": {
        "job_req_section": lambda jr: f" and job requirements:\n\nJob Requirements:\n{jr}" if jr else "",
        "resume_section": lambda r: f"Resume:\n{r}" if r else "",
        "job_req_acknowledgment": lambda jr: " the Job Requirements and" if jr else "",
        "requirements_section": lambda ra: f"Requirements Analysis:\n{ra}\n\n" if ra else "",
        "evaluation_summary": lambda es: es if es else "No evaluation summary available."
    },
    "experience": {
        "requirement": lambda r: r if r else "No specific requirement provided",
        "resume": lambda r: r if r else "",
        "experience_duration": lambda d: d if d else "Not specified",
        "assessment": lambda a: a if a else "Not evaluated",
        "evidence": lambda e: e if e else "No evidence provided",
        "comments": lambda c: c if c else "No additional comments"
    },
    "skills": {
        "required_skills": lambda s: s if s else "No skills requirements provided",
        "resume": lambda r: r if r else "",
        "skills_analysis": lambda a: a if a else "No analysis available",
        "bonus_skills": lambda b: b if b else "None found",
        "summary": lambda s: s if s else "No summary available"
    },
    "project": {
        "resume": lambda r: r if r else "",
        "projects_analysis": lambda a: a if a else "No projects analyzed",
        "assessment": lambda a: a if a else "No assessment available"
    },
    "education": {
        "resume": lambda r: r if r else "",
        "education_analysis": lambda a: a if a else "No education details analyzed",
        "assessment": lambda a: a if a else "No assessment available"
    },
    "certifications": {
        "resume": lambda r: r if r else "",
        "certifications_analysis": lambda a: a if a else "No certifications found",
        "assessment": lambda a: a if a else "No assessment available"
    }
}
