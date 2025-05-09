from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY= os.getenv("ANTHROPIC_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# --- ANSI Color Codes ---
class TermColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    ORANGE = '\033[93m'
    BLUE = '\033[94m' # For "Recommended" if you want a different shade from "Strongly Recommended"
    RESET = '\033[0m'

# --- Configuration and Sample Data ---

JOB_REQUIREMENTS = """
Job Title: Python Developer
Experience: 3+ years of professional Python development experience.
Skills:
  - Python: Proficient
  - SQL: Proficient (e.g., PostgreSQL, MySQL)
  - APIs: Experience with RESTful APIs
  - Version Control: Git
Communication: Good written and verbal communication skills.
Bonus: Experience with Django or Flask, cloud platforms (AWS, Azure, GCP).
"""

SAMPLE_RESUME_1_GOOD_FIT = """
Dr. Alex Chen
alex.chen@email.com | (555) 123-4567 | linkedin.com/in/alexchen | github.com/alexchen

Summary
Highly motivated and results-oriented Python Developer with 4 years of experience in designing, developing, and deploying scalable web applications. Proven ability to work with SQL databases, build robust APIs, and collaborate effectively in agile teams. Passionate about clean code and continuous learning.

Experience
Senior Python Developer | TechSolutions Inc. | Jan 2021 – Present
- Led the development of a new client-facing analytics dashboard using Python, Flask, and PostgreSQL, resulting in a 20% increase in user engagement.
- Designed and implemented RESTful APIs for data integration with third-party services.
- Mentored junior developers on Python best practices and Git workflows.
- Utilized AWS (EC2, S3, RDS) for application deployment and management.

Python Developer | Innovatech Ltd. | June 2019 – Dec 2020
- Developed and maintained backend services for e-commerce platform using Python and Django.
- Wrote complex SQL queries for data retrieval and reporting using MySQL.
- Contributed to CI/CD pipeline setup using Jenkins and Git.

Education
M.S. in Computer Science | University of Advanced Technology | 2019
B.S. in Software Engineering | State University | 2017

Skills
Programming Languages: Python (Expert), SQL (Proficient), JavaScript (Intermediate)
Frameworks/Libraries: Flask, Django, Pandas, NumPy
Databases: PostgreSQL, MySQL, SQLite
Tools: Git, Docker, Jenkins, AWS
Communication: Excellent written and verbal communication, demonstrated through technical documentation and team presentations.
"""

SAMPLE_RESUME_3_BORDERLINE = """
Charlie Davis
charlie.d@email.com | 123-456-7890

Objective: Seeking a challenging role as a Python Developer to utilize my skills in software development.

Experience:
Software Engineer | WebStartup Co. | July 2021 – Present (2 years 6 months)
- Developed backend features for a web application primarily using Node.js.
- Occasionally contributed to Python scripts for data processing tasks (approx 20% of time).
- Gained exposure to SQL databases (primarily querying).
- Used Git for version control in a team environment.

Intern | DataAnalytics Corp. | Jan 2021 – June 2021 (6 months)
- Assisted senior developers with Python-based data cleaning and analysis projects.
- Learned basics of SQL and API interaction.

Education:
B.Sc. Computer Engineering | Tech Institute | 2020

Skills:
- Programming: Python (Intermediate), JavaScript (Proficient), Node.js (Proficient)
- Databases: Basic SQL
- Tools: Git
- Communication: Clear written communication in project documentation.
"""

config_list_gemini = [
    {
        "model": "gemini-1.5-flash",
        "api_key": GOOGLE_API_KEY,
        "api_type": "google",
    }
]
llm_config = {
    "config_list": config_list_gemini,
    "cache_seed": 42,
    "temperature": 0.2,
}

# --- Agent System Prompts ---
ADMIN_SYSTEM_PROMPT = """You are the Job Requirements Agent, an expert HR hiring manager.
Your role is to orchestrate the resume screening process. The conversation will proceed in a round-robin fashion among the agents in the group chat (ExperienceCheckAgent, SkillsCheckAgent, CommunicationCheckAgent, and yourself).

**Your First Turn (after receiving the initial request):**
1.  You will receive an initial message from an external UserProxy containing a resume and job requirements.
2.  Acknowledge receipt of the Job Requirements and Resume (e.g., "Received job requirements and resume for [Candidate Name].").
3.  Extract the specific criteria for Experience, Skills (including proficiency and bonus), and Communication from the Job Requirements.
4.  **Delegate to ExperienceCheckAgent:**
    -   Address the agent clearly: "ExperienceCheckAgent, please analyze the following resume based on this experience requirement..."
    -   Provide the *entire resume*.
    -   Provide the *specific experience requirement* you extracted.
5.  **Delegate to SkillsCheckAgent:**
    -   Address the agent clearly: "SkillsCheckAgent, please analyze the following resume based on these skills requirements..."
    -   Provide the *entire resume*.
    -   Provide the *specific skills requirements* you extracted.
6.  **Delegate to CommunicationCheckAgent:**
    -   Address the agent clearly: "CommunicationCheckAgent, please analyze the following resume for communication indicators..."
    -   Provide the *entire resume*.
    -   State the general requirement for "good communication skills."
7.  **Conclude your first message with EXACTLY**: "Delegation complete. I will synthesize the reports in my next turn after the specialist agents (ExperienceCheckAgent, SkillsCheckAgent, CommunicationCheckAgent) have provided their input."
    **Your first response MUST end here. Do not add any further statements or attempt to summarize.**

**Your Second Turn (after specialist agents have spoken their reports):**
1.  By this turn, ExperienceCheckAgent, SkillsCheckAgent, and CommunicationCheckAgent will have provided their reports in the messages immediately preceding your turn in the round-robin sequence.
2.  Begin your response with: "All specialist reports have been received. Proceeding with final evaluation."
3.  Carefully review the *actual messages* from ExperienceCheckAgent, SkillsCheckAgent, and CommunicationCheckAgent in the preceding chat history.
4.  Synthesize their findings into the "Output Format for Final Evaluation" below.
5.  Your message containing the final evaluation MUST start with "## Resume Evaluation Summary ##".
6.  **After the "Justification for Rating:", add a new line with a final, clear hiring decision based on your "Overall Hireability Rating". Format it as:**
    `Hiring Decision: [Hirable / Not Hirable / Consider with Reservations]`
    (e.g., If "Strongly Recommended" or "Recommended", use "Hirable". If "Not Recommended", use "Not Hirable". If "Consider with Reservations", use that.)

Output Format for Final Evaluation (ONLY to be used in your second turn):
## Resume Evaluation Summary ##
**Candidate:** [Extract Name from resume, e.g., Charlie Davis or Dr. Alex Chen]
**Overall Hireability Rating:** [Your Rating, e.g., "Strongly Recommended", "Recommended", "Consider with Reservations", "Not Recommended"]

**Detailed Breakdown:**
*   **Experience Match:** [Summarize ExperienceCheckAgent's actual report from chat history, and your assessment of it]
*   **Skills Match:** [Summarize SkillsCheckAgent's actual report from chat history, and your assessment of it]
*   **Communication Indicators:** [Summarize CommunicationCheckAgent's actual report from chat history, and your assessment of it]
*   **Bonus Skills:** [Mention if any bonus skills from JD are present, based on SkillsCheckAgent's actual report from chat history]

**Justification for Rating:**
[Your concise explanation tying everything together, based on the actual reports from the chat history]

Hiring Decision: [Your final decision: Hirable / Not Hirable / Consider with Reservations]

After providing the "## Resume Evaluation Summary ##" and the "Hiring Decision:", your task for this resume is complete. This message will terminate the chat.
"""

EXPERIENCE_SYSTEM_PROMPT = """You are the ExperienceCheckAgent.
You specialize in analyzing the "Experience" section of a resume to determine if a candidate meets specific years of experience requirements for a given role.
You will be given the full resume and a specific experience requirement by the JobRequirementsAgent.
Respond only with your analysis in the specified format. Do not add conversational filler. Your response is your report.

Output Format:
**Experience Analysis:**
*   **Requirement:** [State the experience requirement you were given]
*   **Candidate's Relevant Experience:** [e.g., Approx. X years Y months]
*   **Assessment:** [Meets Requirement / Exceeds Requirement / Falls Short / Borderline]
*   **Supporting Evidence:**
    - [Role 1] at [Company A]: [Duration] - [Briefly state relevance]
    - [Role 2] at [Company B]: [Duration] - [Briefly state relevance]
*   **Comments:** [Any additional notes]
"""

SKILLS_SYSTEM_PROMPT = """You are the SkillsCheckAgent.
You specialize in identifying technical skills in a resume and assessing them against a list of required skills.
You will be given the full resume and a list of required skills by the JobRequirementsAgent.
Respond only with your analysis in the specified format. Do not add conversational filler. Your response is your report.

Output Format:
**Skills Analysis:**
**Required Skills:**
*   **[Skill 1 Name (e.g., Python)]:**
    *   **Requirement:** [e.g., Proficient]
    *   **Found in Resume:** [Yes/No]
    *   **Evidence/Context:** [Quote or describe where it was found]
    *   **Assessed Proficiency:** [e.g., Appears Proficient / Intermediate / Basic / Not Evident]
(Repeat for all required skills)
**Bonus Skills (if mentioned in requirements and found):**
*   **[Bonus Skill 1 Name]:** [Present/Not Present] - [Evidence/Context if present]
**Overall Skills Summary:** [Briefly summarize adequacy of core technical skills.]
"""

COMMUNICATION_SYSTEM_PROMPT = """You are the CommunicationCheckAgent.
Your task is to infer potential communication skills based on the quality of the resume itself.
You will be given the full resume by the JobRequirementsAgent. The general requirement is "good communication skills."
Respond only with your analysis in the specified format. Do not add conversational filler. Your response is your report.

Output Format:
**Communication Indicators Analysis:**
*   **Clarity & Conciseness:** [e.g., Good, Average, Needs Improvement - with brief justification]
*   **Grammar & Spelling:** [e.g., Excellent, Minor issues, Several errors]
*   **Professionalism (Tone & Format):** [e.g., Highly professional, Acceptable, Lacks professionalism]
*   **Structure & Organization:** [e.g., Well-structured, Acceptable, Disorganized]
*   **Explicit Mentions:** [List any relevant mentions]
*   **Overall Impression:** [e.g., Resume suggests good written communication skills]
"""

import autogen
import re # Import re for more flexible searching

# --- Create Agents ---
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    code_execution_config=False,
)

admin_agent = autogen.AssistantAgent(
    name="JobRequirementsAgent",
    system_message=ADMIN_SYSTEM_PROMPT,
    llm_config=llm_config,
)

experience_agent = autogen.AssistantAgent(
    name="ExperienceCheckAgent",
    system_message=EXPERIENCE_SYSTEM_PROMPT,
    llm_config=llm_config,
)

skills_agent = autogen.AssistantAgent(
    name="SkillsCheckAgent",
    system_message=SKILLS_SYSTEM_PROMPT,
    llm_config=llm_config,
)

communication_agent = autogen.AssistantAgent(
    name="CommunicationCheckAgent",
    system_message=COMMUNICATION_SYSTEM_PROMPT,
    llm_config=llm_config,
)

groupchat_agents = [admin_agent, experience_agent, skills_agent, communication_agent]
groupchat = autogen.GroupChat(
    agents=groupchat_agents,
    messages=[],
    max_round=10,
    speaker_selection_method="round_robin"
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
    is_termination_msg=lambda msg: (
        isinstance(msg.get("content"), str) and
        "## Resume Evaluation Summary ##" in msg.get("content") and # This marker is still key
        # "Hiring Decision:" in msg.get("content") and # Optionally add this if needed
        msg.get("name") == admin_agent.name
    )
)

def screen_resume(resume_text, job_requirements_text):
    print(f"\n--- Screening Resume for Job ---\n")
    initial_message = f"""
Please screen the following resume against the provided job requirements.

## Job Requirements ##
{job_requirements_text}

## Resume ##
{resume_text}

JobRequirementsAgent, please begin the process by delegating tasks.
"""
    if hasattr(groupchat, 'messages') and groupchat.messages is not None:
        groupchat.messages.clear()
    else:
        groupchat.messages = []

    user_proxy.initiate_chat(
        recipient=manager,
        message=initial_message,
    )

    print("\n--- Screening Complete ---")
    final_report_text = None
    if hasattr(groupchat, 'messages'):
        for msg in reversed(groupchat.messages):
            content = msg.get('content')
            if (msg.get('name') == admin_agent.name and
                msg.get('role') == 'assistant' and
                isinstance(content, str) and
                "## Resume Evaluation Summary ##" in content):
                final_report_text = content
                break
    
    if final_report_text:
        print("\nFinal Evaluation Report:")
        
        colored_report = final_report_text
        try:
            # Use regex to find the rating line more robustly
            # This looks for "**Overall Hireability Rating:**" followed by any characters up to the end of the line.
            match = re.search(r"(\*\*Overall Hireability Rating:\*\*\s*)(.*)", final_report_text, re.IGNORECASE)
            if match:
                prefix = match.group(1) # The part before the rating, e.g., "**Overall Hireability Rating:** "
                rating_value = match.group(2).strip() # The actual rating, e.g., "Strongly Recommended"
                
                color_code = TermColors.RESET # Default
                rating_value_lower = rating_value.lower()

                if "strongly recommended" in rating_value_lower:
                    color_code = TermColors.GREEN
                elif "not recommended" in rating_value_lower:
                    color_code = TermColors.RED
                elif "recommended" in rating_value_lower: # Could be blue or green
                    color_code = TermColors.BLUE # Or TermColors.GREEN
                elif "consider with reservations" in rating_value_lower or "borderline" in rating_value_lower or "okay" in rating_value_lower:
                    color_code = TermColors.ORANGE
                
                colored_rating_line = f"{prefix}{color_code}{rating_value}{TermColors.RESET}"
                
                # Replace the original line with the colored one
                # This is safer than splitting by lines if the rating value itself contains newlines (unlikely here)
                colored_report = final_report_text.replace(match.group(0), colored_rating_line)
        except Exception as e:
            print(f"[Colorization Error] Could not colorize report: {e}")
            # Fallback to printing the uncolored report
        
        print(colored_report)

    else:
        print("\nCould not automatically extract the final report. Please review the chat history.")
        print("\nFull Chat History (for debugging):")
        if hasattr(groupchat, 'messages'):
            for i, msg_item in enumerate(groupchat.messages):
                print(f"--- Message {i+1} ---")
                print(f"Name: {msg_item.get('name', 'N/A')}")
                print(f"Role: {msg_item.get('role', 'N/A')}")
                m_content = msg_item.get('content', '')
                print(f"Content:\n{m_content}")
                print("-" * 30)
        else:
            print("No messages found in groupchat history.")

# --- Run the process for different resumes ---
screen_resume(SAMPLE_RESUME_1_GOOD_FIT, JOB_REQUIREMENTS) # Test with a "Strongly Recommended"
# screen_resume(SAMPLE_RESUME_3_BORDERLINE, JOB_REQUIREMENTS) # Test with "Not Recommended" or "Consider with Reservations"