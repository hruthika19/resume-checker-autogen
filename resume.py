from dotenv import load_dotenv
import os
import autogen
import re
from prompts import (
    admin_prompt_template, 
    experience_prompt_template,
    skills_prompt_template,
    project_prompt_template,
    education_prompt_template,
    certifications_prompt_template
)

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


ADMIN_SYSTEM_PROMPT = admin_prompt_template.format_messages(candidate_name="")[0].content
EXPERIENCE_SYSTEM_PROMPT = experience_prompt_template.format_messages(requirement="")[0].content
SKILLS_SYSTEM_PROMPT = skills_prompt_template.format_messages(example_skill="Python")[0].content
PROJECT_SYSTEM_PROMPT = project_prompt_template.format_messages()[0].content
EDUCATION_SYSTEM_PROMPT = education_prompt_template.format_messages(qualification_type="")[0].content
CERTIFICATIONS_SYSTEM_PROMPT = certifications_prompt_template.format_messages()[0].content

# Global agent and groupchat setup (to be initialized once)
user_proxy = None
admin_agent = None
experience_agent = None
skills_agent = None
project_agent = None
education_agent = None
certifications_agent = None
groupchat = None
manager = None

def initialize_agents():
    global user_proxy, admin_agent, experience_agent, skills_agent, project_agent, education_agent, certifications_agent, groupchat, manager

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

    project_agent = autogen.AssistantAgent(
        name="ProjectCheckAgent",
        system_message=PROJECT_SYSTEM_PROMPT,
        llm_config=llm_config,
    )

    education_agent = autogen.AssistantAgent(
        name="EducationCheckAgent",
        system_message=EDUCATION_SYSTEM_PROMPT,
        llm_config=llm_config,
    )

    certifications_agent = autogen.AssistantAgent(
        name="CertificationsCheckAgent",
        system_message=CERTIFICATIONS_SYSTEM_PROMPT,
        llm_config=llm_config,
    )

    groupchat_agents_list = [
        admin_agent, 
        experience_agent, 
        skills_agent, 
        project_agent, 
        education_agent, 
        certifications_agent
    ]
    
    groupchat = autogen.GroupChat(
        agents=groupchat_agents_list,
        messages=[],
        max_round=10,
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
                            hiring_decision = "Hireable"
                        elif "not recommended" in rating:
                            hiring_decision = "Not Hireable"
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