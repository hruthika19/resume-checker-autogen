from dotenv import load_dotenv
import os
import autogen
import re

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


config_list_gemini = [
    {
        "model": "gemini-2.0-flash-001",
        "api_key": GOOGLE_API_KEY,
        "api_type": "google",
        "base_url": "https://generativelanguage.googleapis.com/v1/models",
    }
]
llm_config = {
    "config_list": config_list_gemini,
    "cache_seed": 42, # Consider removing cache_seed or making it dynamic for multiple runs
    "temperature": 0.2,
}


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
    (e.g., If "Strongly Recommended" or "Recommended", use "Hirable". If "Not Recommended", use "Not Hirable". If "Consider with Reservations", use that string.)

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
# Global agent and groupchat setup (to be initialized once)
user_proxy = None
admin_agent = None
experience_agent = None
skills_agent = None
communication_agent = None
groupchat = None
manager = None

def initialize_agents():
    global user_proxy, admin_agent, experience_agent, skills_agent, communication_agent, groupchat, manager

    if admin_agent is not None: # Already initialized
        return

    print("Initializing AutoGen agents...") # For backend log

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

    groupchat_agents_list = [admin_agent, experience_agent, skills_agent, communication_agent]
    groupchat = autogen.GroupChat(
        agents=groupchat_agents_list,
        messages=[],
        max_round=10, # Adjust as needed
        speaker_selection_method="round_robin"
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: (
            isinstance(msg.get("content"), str) and
            "## Resume Evaluation Summary ##" in msg.get("content") and
            msg.get("name") == admin_agent.name
        )
    )
    print("AutoGen agents initialized.")


def analyze_resume_with_autogen(resume_text_content, job_requirements_text):
    initialize_agents() # Ensure agents are ready

    if not all([user_proxy, admin_agent, groupchat, manager]):
        return "Error: Agents not initialized.", "Error"

    print(f"\n--- Analyzing Resume (Backend Log) ---")
    print(f"Job Requirements:\n{job_requirements_text[:200]}...") # Log snippet
    print(f"Resume Content:\n{resume_text_content[:200]}...") # Log snippet

    initial_message = f"""
Please screen the following resume against the provided job requirements.

## Job Requirements ##
{job_requirements_text}

## Resume ##
{resume_text_content}

JobRequirementsAgent, please begin the process by delegating tasks.
"""
    # CRITICAL: Clear messages for each new analysis
    if hasattr(groupchat, 'messages') and groupchat.messages is not None:
        groupchat.messages.clear()
    else:
        groupchat.messages = []


    user_proxy.initiate_chat(
        recipient=manager,
        message=initial_message,
    )

    print("--- AutoGen Chat Complete (Backend Log) ---")

    final_report_text = None
    hiring_decision = "Undetermined" # Default

    if hasattr(groupchat, 'messages'):
        for msg in reversed(groupchat.messages):
            # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\nmsg=", msg)
            # print("\nDEBUG: Message details:")
            # print(f"Name: {msg.get('name')}")
            # print(f"Role: {msg.get('role')}")
            # print(f"Content type: {type(msg.get('content'))}")
            # print(f"Content preview: {str(msg.get('content'))[:100]}...","\n\n\n\n\n\n\n\n\n\n\n\n\n\n") # For debugging
            content = msg.get('content')
            if (msg.get('name') == admin_agent.name and
                msg.get('role') == 'user' and # Check role is 'assistant' for LLM responses
                isinstance(content, str) and
                "## Resume Evaluation Summary ##" in content):
                final_report_text = content
                # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\nfinal_report_text=", final_report_text, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                # Extract "Hiring Decision:"
                decision_match = re.search(r"Hiring Decision:\s*(.*)", content, re.IGNORECASE)
                # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\ndecision_match=", decision_match, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                if decision_match:
                    hiring_decision = decision_match.group(1).strip()
                else:
                    # Fallback: Infer from "Overall Hireability Rating"
                    rating_match = re.search(r"\*\*Overall Hireability Rating:\*\*\s*(.*)", content, re.IGNORECASE)
                    # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\trating_match=", rating_match, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    if rating_match:
                        rating = rating_match.group(1).strip().lower()
                        if "strongly recommended" in rating or "recommended" in rating:
                            hiring_decision = "Hirable"
                        elif "not recommended" in rating:
                            hiring_decision = "Not Hirable"
                        elif "consider with reservations" in rating or "borderline" in rating:
                            hiring_decision = "Consider with Reservations"
                        # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\thiring_decision=", hiring_decision, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                break
    
    # For backend log: Print the extracted full report and decision
    if final_report_text:
        print("\n--- Full Evaluation Report (Backend Log) ---")
        print(final_report_text)
        print("-----------------------------------------")
    print(f"FINAL HIRING DECISION (Backend Log): {hiring_decision}")
    print("-----------------------------------------\n")
    
    return hiring_decision, final_report_text # Return decision for UI and full report for optional display