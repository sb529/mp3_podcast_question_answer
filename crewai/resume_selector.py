import os
from dotenv import load_dotenv
from crewai import Agent, Task, Process, Crew
from openai import OpenAI
import shutil

# Load environment variables
load_dotenv()

# Paths to inputs and outputs
JOB_DESCRIPTION_PATH = "inputs/job_description.txt"
RESUMES_FOLDER = "inputs/resumes/"
OUTPUT_FOLDER = "outputs/top_5_resumes/"
EMAIL_LOG_PATH = "outputs/email_log.txt"


# Load OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
hiring_manager_email = os.getenv("HIRING_MANAGER_EMAIL")

# Define Agent 1: Resume Analyzer
resume_analyzer = Agent(
    role="Resume Analyzer",
    goal="Read through the job description and find the most relevant resumes from the provided PDF files.",
    backstory="""You are an expert in analyzing job descriptions and matching them with resumes. Your expertise helps identify candidates whose skills and experience align with the requirements.""",
    verbose=True,
    allow_delegation=False,
    llm=openai_api_key,  # Use OpenAI API
)

# Define Agent 2: Resume Selector and Emailer
resume_selector_emailer = Agent(
    role="Resume Selector and Emailer",
    goal="Select the top 5 resumes and email them to the hiring manager.",
    backstory="""You are skilled in assessing the quality of resumes and ranking them based on relevance to the job description. You also handle professional email communication.""",
    verbose=True,
    allow_delegation=False,
    llm=openai_api_key,  # Use OpenAI API
)

# Task 1: Analyze Resumes
task1 = Task(
    name="Analyze Resumes",
    description="""Read the job description and evaluate the 20 provided resumes (in PDF format). Identify the most relevant resumes based on skills, experience, and alignment with the job description.""",
    agent=resume_analyzer,
    input_files=["inputs/resumes/resume1.pdf", "inputs/resumes/resume2.pdf"],  # Add all 20 resumes here
    output={
        "relevant_resumes": {
            "description": "The list of resumes identified as relevant to the job description.",
            "type": "list",  # Specify the type of output
        }
    },  # Output format for relevant resumes
)

# Task 2: Select and Email Resumes
task2 = Task(
    name="Select and Email Resumes",
    description="""From the relevant resumes, select the top 5 and email them to the hiring manager at shreya.bhargava123@gmail.com.""",
    agent=resume_selector_emailer,
    input="relevant_resumes",  # Use the output of Task 1 as input
    output={
        "email_confirmation": {
            "description": "Confirmation that emails have been sent successfully.",
            "type": "confirmation",  # Specify the type of output
        }
    },  # Output format for email confirmation
)

# Define the Crew
crew = Crew(
    agents=[resume_analyzer, resume_selector_emailer],
    tasks=[task1, task2],
    verbose=2,
    process=Process.sequential,  # Execute tasks sequentially
)

# Run the Crew
result = crew.kickoff()
print("######################")
print(result)


# Function to read job description
def load_job_description():
    with open(JOB_DESCRIPTION_PATH, "r") as file:
        return file.read()

# Function to load all resumes
def load_resumes():
    resume_files = [os.path.join(RESUMES_FOLDER, f) for f in os.listdir(RESUMES_FOLDER) if f.endswith(".pdf")]
    return [{"path": path, "filename": os.path.basename(path)} for path in resume_files]

# Example usage
job_description = load_job_description()
resumes = load_resumes()
print(f"Job Description: {job_description}")
print(f"Loaded {len(resumes)} resumes.")

# Email-Sending Function
def send_emails(resumes):
    """
    Send the top 5 resumes to the hiring manager via email.
    """
    import smtplib
    from email.message import EmailMessage

    # Create the email
    msg = EmailMessage()
    msg["Subject"] = "Top 5 Candidates for the Role"
    msg["From"] = email_address
    msg["To"] = hiring_manager_email
    msg.set_content("Attached are the top 5 resumes based on the job description.")

    # Attach resumes
    for resume in resumes[:5]:  # Only the top 5 resumes
        with open(resume["path"], "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=resume["filename"])

    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)

    return "Email sent successfully."
    
# Save top 5 resumes
def save_top_resumes(resumes):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    for resume in resumes[:5]:
        shutil.copy(resume["path"], os.path.join(OUTPUT_FOLDER, resume["filename"]))

# Log email confirmations
def log_email_confirmation(message):
    with open(EMAIL_LOG_PATH, "a") as log_file:
        log_file.write(message + "\n")

# Note:
# - Replace "your_email@gmail.com" and "your_password" with valid credentials.
# - Ensure the resumes are accessible as files in the working directory.
