import streamlit as st
from docx import Document
import PyPDF2
import io # To handle byte streams for file processing
import base64  # Add this import at the top of the file

# Import the core AutoGen logic
from resume import initialize_agents, analyze_resume_with_autogen

# --- Helper functions to read file content ---
def read_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return None

def read_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# --- Initialize AutoGen Agents (globally for the app session if desired, or on demand) ---
# Calling it here means it initializes when the Streamlit app starts.
# This is good if the LLM config is static.
# If LLM config could change per user session, might need a more complex setup.
initialize_agents()


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("📝 Resume Analyzer with AutoGen")

# --- Initialize session state variables ---
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = [] # Stores {'name': str, 'text': str, 'status': str, 'id': int}
if 'job_requirements' not in st.session_state:
    st.session_state.job_requirements = """Job Title: Python Developer
Experience: 3+ years of professional Python development experience.
Skills:
  - Python: Proficient
  - SQL: Proficient (e.g., PostgreSQL, MySQL)
  - APIs: Experience with RESTful APIs
  - Version Control: Git
Communication: Good written and verbal communication skills.
Bonus: Experience with Django or Flask, cloud platforms (AWS, Azure, GCP).
""" # Default example

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("📄 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload DOCX or PDF resume files",
        type=["docx", "pdf"],
        accept_multiple_files=True
    )

    st.header("🎯 Job Requirements")
    st.session_state.job_requirements = st.text_area(
        "Enter the job requirements:",
        value=st.session_state.job_requirements,
        height=300
    )

    if st.button("🔄 Process Uploaded Files"):
        if uploaded_files:
            st.session_state.uploaded_files_data = [] # Clear previous
            for i, uploaded_file in enumerate(uploaded_files):
                file_bytes = uploaded_file.getvalue()
                text_content = None
                if uploaded_file.type == "application/pdf":
                    text_content = read_pdf(file_bytes)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text_content = read_docx(file_bytes)
                
                if text_content:
                    st.session_state.uploaded_files_data.append({
                        "id": i,
                        "name": uploaded_file.name,
                        "text": text_content,
                        "status": "Pending Analysis",
                        "full_report": None,
                        "file_type": uploaded_file.type,
                        "file_bytes": file_bytes  # Store the raw file bytes
                    })
            st.success(f"{len(st.session_state.uploaded_files_data)} resumes processed and ready for analysis.")
        else:
            st.warning("Please upload resume files first.")


if not st.session_state.uploaded_files_data:
    st.info("Upload resumes and click 'Process Uploaded Files' in the sidebar to begin.")
else:
    if not st.session_state.job_requirements.strip():
        st.warning("Please enter job requirements in the sidebar before checking resumes.")
    else:
        for i, resume_data in enumerate(st.session_state.uploaded_files_data):
            st.subheader(f"📄 Resume: {resume_data['name']}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                with st.expander("View Resume Content"):
                    if resume_data['file_type'] == "application/pdf":
                        # Display PDF using base64 encoding
                        base64_pdf = base64.b64encode(resume_data['file_bytes']).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    else:
                        # For DOCX files, show text content
                        st.text(resume_data['text'][:500] + "...")
                
                # Display status and full report if available
                status_color = "blue"
                if "Hireable" in resume_data['status']:
                    status_color = "green"
                elif "Not Hireable" in resume_data['status']:
                    status_color = "red"
                elif "Consider" in resume_data['status']:
                    status_color = "orange"
                
                st.markdown(f"**Status:** <font color='{status_color}'>{resume_data['status']}</font>", unsafe_allow_html=True)

                if resume_data.get("full_report"):
                     with st.expander("View Full Evaluation Report"):
                        st.text_area("", value=resume_data["full_report"], height=300, disabled=True)


            with col2:
                # Use a unique key for each button based on the resume's ID or name
                button_key = f"check_button_{resume_data['id']}"
                if st.button("🔍 Analyze this Resume", key=button_key, type="primary"):
                    if st.session_state.job_requirements.strip():
                        st.info(f"Analyzing {resume_data['name']}... (Check terminal for detailed logs)")
                        with st.spinner(f"AutoGen is thinking about {resume_data['name']}..."):
                            decision, full_report_text = analyze_resume_with_autogen(
                                resume_data['text'],
                                st.session_state.job_requirements
                            )
                        # Update the specific resume's data in session_state
                        st.session_state.uploaded_files_data[i]['status'] = decision
                        st.session_state.uploaded_files_data[i]['full_report'] = full_report_text
                        st.rerun() # Rerun to update the UI with the new status
                    else:
                        st.error("Job requirements are missing. Please enter them in the sidebar.")
            st.markdown("---") # Separator