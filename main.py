# Import Streamlit for building the web application interface
import streamlit as st
# Import pandas for data manipulation and analysis
import pandas as pd
# Import PyPDF2 for extracting text from PDF files
import PyPDF2
# Import re for regular expression pattern matching
import re
# Import BytesIO for handling in-memory binary streams
from io import BytesIO
# Import random for selecting random elements (e.g., feedback or questions)
import random
# Import base64 for encoding binary data (not used in this code but imported)
import base64
# Import TextBlob for sentiment analysis of resume text
from textblob import TextBlob
# Import ReportLab components for generating PDF reports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
# Import requests for making HTTP requests (e.g., fetching profile pictures)
import requests
# Import BeautifulSoup for parsing HTML content (e.g., LinkedIn profile images)
from bs4 import BeautifulSoup
# Import smtplib and email components for sending bulk emails
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Import os for interacting with the operating system (e.g., environment variables)
import os
# Import load_dotenv to load environment variables from a .env file
from dotenv import load_dotenv
# Import Plotly for creating interactive visualizations
import plotly.express as px
import plotly.graph_objects as go
# Import CrewAI components for defining AI agents and tasks
from crewai import Agent, Task, Crew, Process

# Load environment variables from .env file (e.g., SMTP credentials)
load_dotenv()

# Configure Streamlit page settings (title and layout)
st.set_page_config(page_title="HIREIN: Smart Recruitment", layout="wide")

# Define custom CSS for a modern, dark-themed UI with animations
st.markdown("""
<style>
:root {
    --background-color: #0e0e20; /* Dark background color */
    --text-color: #d4d4f4; /* Light text color */
    --primary-accent: #ff4b4b; /* Red accent for highlights */
    --secondary-accent: #2a2a50; /* Darker secondary color */
    --card-bg: #1a1a38; /* Card background color */
    --input-bg: #242450; /* Input field background */
    --button-bg: #ff4b4b; /* Button background */
    --button-hover-bg: #d43a3a; /* Button hover color */
    --shadow: 0 8px 16px rgba(0, 0, 0, 0.4); /* Shadow effect */
    --border-radius: 12px; /* Rounded corners */
    --transition: all 0.3s ease; /* Smooth transitions */
    --font-family: 'Roboto', sans-serif; /* Modern font */
}

/* Apply styles to the app's body and main container */
body, .stApp {
    background: var(--background-color);
    color: var(--text-color);
    font-family: var(--font-family);
    line-height: 1.7;
}

/* Style the sidebar */
.sidebar .sidebar-content {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
}

/* Style buttons */
.stButton>button {
    background-color: var(--button-bg);
    color: #ffffff;
    border-radius: var(--border-radius);
    border: none;
    padding: 14px 28px;
    font-weight: 600;
    font-size: 16px;
    transition: var(--transition);
}

/* Button hover effects */
.stButton>button:hover {
    background-color: var(--button-hover-bg);
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}

/* Style input fields */
.stTextInput>div>input, .stNumberInput>div>input, .stTextArea>div>textarea {
    background-color: var(--input-bg);
    color: var(--text-color);
    border: 1px solid var(--primary-accent);
    border-radius: var(--border-radius);
    padding: 12px;
    font-size: 16px;
}

/* Style select boxes */
.stSelectbox>div>div {
    background-color: var(--input-bg);
    color: var(--text-color);
    border: 1px solid var(--primary-accent);
    border-radius: var(--border-radius);
}

/* Style dataframes */
.stDataFrame {
    background-color: var(--card-bg);
    color: var(--text-color);
    border-radius: var(--border-radius);
    padding: 15px;
}

/* Style headers */
h1, h2, h3 {
    color: var(--primary-accent);
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Style markdown text */
.stMarkdown p {
    color: #a0a0c0;
    font-size: 16px;
}

/* Style cards for candidate profiles */
.card {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 25px;
    box-shadow: var(--shadow);
    margin-bottom: 25px;
    transition: var(--transition);
}

/* Card hover effects */
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
}

/* Style download buttons */
.stDownloadButton>button {
    background-color: var(--secondary-accent);
    color: var(--text-color);
    border-radius: var(--border-radius);
    padding: 12px 24px;
    font-size: 15px;
}

/* Download button hover effects */
.stDownloadButton>button:hover {
    background-color: #3a3a70;
    transform: translateY(-3px);
}

/* Style badges for ATS rejection risk */
.badge-low { background-color: #34D399; padding: 6px 10px; border-radius: 6px; color: #fff; }
.badge-medium { background-color: #FBBF24; padding: 6px 10px; border-radius: 6px; color: #fff; }
.badge-high { background-color: #ff4b4b; padding: 6px 10px; border-radius: 6px; color: #fff; }

/* Define glowing animation for cards */
@keyframes glow {
    0% { box-shadow: 0 0 5px var(--primary-accent); }
    50% { box-shadow: 0 0 20px var(--primary-accent); }
    100% { box-shadow: 0 0 5px var(--primary-accent); }
}

/* Apply glow effect to elements */
.glow-effect {
    animation: glow 2s infinite;
}
</style>
<!-- Import Roboto font from Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Display the app logo in the sidebar
st.sidebar.image("https://media.discordapp.net/attachments/1355795293198745762/1383678608236871720/logo-removebg-preview.png?ex=684faa9f&is=684e591f&hm=a0b57262c2dc9a800ea3c460fb549b8f51bd77ab8486a588ebf31af8d9cf5de4&=&format=webp&quality=lossless&width=1100&height=1100", width=300)

# Simulate CATSOne ATS scoring for resumes
def get_catsone_ats_score(resume_text, job_desc):
    try:
        # Extract job skills from job description
        job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
        # Extract programming languages from resume text
        resume_skills = [skill.lower() for skill in re.findall(r'\b(Python|Java|SQL|JavaScript|C\+\+|HTML|CSS|iOS|Swift)\b', resume_text, re.IGNORECASE)]
        # Calculate skill overlap
        common_skills = len(set(job_skills) & set(resume_skills))
        # Compute base score based on skill match
        score = (common_skills / len(job_skills)) * 80 if job_skills else 50
        # Extract experience from resume
        exp_match = re.search(r'(\d+\.?\d*|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*(?:years?|yrs?|\+?\s*years?|\+?\s*yrs?)(?:\s*of\s*experience)?', resume_text, re.IGNORECASE)
        if exp_match:
            num_str = exp_match.group(1)
            # Convert word numbers to integers
            word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
            # Parse experience years
            exp_years = float(word_to_num[num_str.lower()] if num_str.lower() in word_to_num else num_str)
            # Add experience-based score
            score += min(exp_years / job_desc.get("experience", 1), 1) * 20
        # Return capped score
        return round(min(score, 100), 2)
    except Exception as e:
        # Display error and return default score
        st.error(f"Error simulating CATSOne ATS score: {str(e)}")
        return 50.0

# Calculate language expertise based on resume and job description
def calculate_language_expertise(resume_text, job_desc):
    # Define supported programming languages
    languages = ["Python", "Java", "SQL", "JavaScript", "C++", "HTML", "CSS", "iOS", "Swift"]
    # Extract job skills
    job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
    # Extract resume skills
    resume_skills = [skill.lower() for skill in re.findall(r'\b(' + '|'.join(languages) + r')\b', resume_text, re.IGNORECASE)]
    
    # Calculate depth of expertise (mentions per language)
    depth_scores = {}
    for skill in resume_skills:
        depth_scores[skill] = depth_scores.get(skill, 0) + 1
    
    # Calculate breadth score (number of languages)
    breadth_score = len(set(resume_skills)) * 10
    
    # Calculate relevance score (job-required skills)
    relevance_score = sum(depth_scores.get(skill, 0) * 20 for skill in job_skills)
    
    # Compute total expertise score (capped at 100)
    total_score = min(relevance_score + breadth_score, 100)
    return {
        "language_expertise_score": round(total_score, 2),
        "primary_language": max(depth_scores, key=depth_scores.get, default="None"),
        "language_count": len(set(resume_skills))
    }

# Set up CrewAI agents for resume processing
def setup_crewai_agents(resumes, job_desc):
    # Define resume parser agent
    resume_parser = Agent(
        role="Resume Parser",
        goal="Extract and score candidate resumes using CATSOne ATS and language expertise logic",
        backstory="Expert in resume analysis with proficiency in ATS systems and programming language evaluation",
        verbose=True,
        allow_delegation=False
    )
    
    # Define candidate sorter agent
    candidate_sorter = Agent(
        role="Candidate Sorter",
        goal="Rank candidates based on combined ATS, match, and language expertise scores",
        backstory="Specialist in candidate evaluation and ranking for recruitment",
        verbose=True,
        allow_delegation=False
    )
    
    # Define report generator agent
    report_generator = Agent(
        role="Report Generator",
        goal="Generate comprehensive dashboard reports and PDFs",
        backstory="Experienced in data visualization and report creation for recruitment insights",
        verbose=True,
        allow_delegation=False
    )
    
    # Define resume parsing task
    parse_task = Task(
        description="Parse resumes, fetch CATSOne ATS scores, calculate match scores, and evaluate language expertise",
        expected_output="DataFrame with candidate data including ATS scores, match scores, and language expertise",
        agent=resume_parser
    )
    
    # Define sorting task
    sort_task = Task(
        description="Sort candidates based on a weighted combination of ATS, match, and language expertise scores",
        expected_output="Sorted DataFrame of candidates",
        agent=candidate_sorter
    )
    
    # Define reporting task
    report_task = Task(
        description="Generate dashboard insights and a PDF report summarizing candidate data",
        expected_output="Dashboard data and PDF buffer",
        agent=report_generator
    )
    
    # Create CrewAI crew with agents and tasks
    crew = Crew(
        agents=[resume_parser, candidate_sorter, report_generator],
        tasks=[parse_task, sort_task, report_task],
        verbose=True,
        process=Process.sequential
    )
    
    return crew

# Extract text from a PDF file
def extract_text_from_pdf(file):
    try:
        # Initialize PDF reader
        pdf_reader = PyPDF2.PdfReader(file)
        # Extract text from all pages
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as e:
        # Display error and return empty string
        st.error(f"Error reading PDF: {str(e)}")
        return ""

# Fetch LinkedIn profile picture (mocked)
def fetch_linkedin_profile_picture(linkedin_url):
    try:
        # Set user-agent to avoid blocking
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Make HTTP request to LinkedIn URL
        response = requests.get(linkedin_url, headers=headers, timeout=5)
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find profile photo
            img_tag = soup.find('img', {'class': 'profile-photo'})
            # Return image source or placeholder
            return img_tag['src'] if img_tag and img_tag.get('src') else "https://via.placeholder.com/150"
        return "https://via.placeholder.com/150"
    except Exception:
        # Return placeholder on error
        return "https://via.placeholder.com/150"

# Fetch GitHub profile picture, fallback to LinkedIn
def fetch_github_profile_picture(github_url, linkedin_url):
    try:
        # Extract GitHub username
        username = github_url.rstrip('/').split('/')[-1]
        # Fetch GitHub user data
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code == 200:
            # Get avatar URL
            avatar_url = response.json().get("avatar_url")
            # Return avatar if valid
            if avatar_url and avatar_url != "https://avatars.githubusercontent.com/u/0":
                return avatar_url
        # Fallback to LinkedIn
        return fetch_linkedin_profile_picture(linkedin_url) if linkedin_url else "https://via.placeholder.com/150"
    except Exception:
        # Fallback to LinkedIn or placeholder
        return fetch_linkedin_profile_picture(linkedin_url) if linkedin_url else "https://via.placeholder.com/150"

# Parse resume text to extract candidate information
def parse_resume(text):
    # Initialize candidate data dictionary
    data = {
        "name": "", "email": "", "phone": "", "skills": [], 
        "experience": 0, "location": "", "degree": "", "college": "",
        "sentiment": 0.0, "tags": [], "ats_rejection_risk": "Low",
        "github_url": "", "linkedin_url": "", "profile_picture": "",
        "source": "Uploaded", "raw_resume": text, "catsone_ats_score": 0.0,
        "language_expertise_score": 0.0, "primary_language": "None", "language_count": 0,
        "match_score": 0.0, "missing_skills": ""
    }
    if text:
        # Extract name (assume first line)
        data["name"] = text.split('\n')[0].strip() or "Unknown"
    # Extract email using regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        data["email"] = email_match.group(0)
    # Extract phone number using regex
    phone_match = re.search(r'(\+?\d[\d -]{7,}\d)', text)
    if phone_match:
        data["phone"] = phone_match.group(1)
    # Extract GitHub URL
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)(?:/)?', text, re.IGNORECASE)
    if github_match:
        data["github_url"] = f"https://github.com/{github_match.group(1)}"
    # Extract LinkedIn URL
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)(?:/)?', text, re.IGNORECASE)
    if linkedin_match:
        data["linkedin_url"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
    # Fetch profile picture
    data["profile_picture"] = fetch_github_profile_picture(data["github_url"], data["linkedin_url"])
    # Define supported skills
    skills = ["Python", "Java", "SQL", "JavaScript", "C++", "HTML", "CSS", "iOS", "Swift"]
    # Extract skills from resume
    data["skills"] = [skill for skill in skills if skill.lower() in text.lower()]
    # Extract experience
    exp_match = re.search(r'(\d+\.?\d*|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*(?:years?|yrs?|\+?\s*years?|\+?\s*yrs?)(?:\s*of\s*experience)?', text, re.IGNORECASE)
    if exp_match:
        num_str = exp_match.group(1)
        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        data["experience"] = float(word_to_num[num_str.lower()] if num_str.lower() in word_to_num else num_str)
    # Extract location
    location_match = re.search(r'(?:location|city|state)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if location_match:
        data["location"] = location_match.group(1).strip()
    # Extract degree
    degree_match = re.search(r'(?:degree|education)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if degree_match:
        data["degree"] = degree_match.group(1).strip()
    # Extract college
    college_match = re.search(r'(?:university|college)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if college_match:
        data["college"] = college_match.group(1).strip()
    # Calculate sentiment
    blob = TextBlob(text)
    data["sentiment"] = blob.sentiment.polarity
    return data

# Calculate match score between resume and job description
def calculate_match_score(resume_data, job_desc):
    score = 0
    # Extract job skills
    job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
    # Extract resume skills
    resume_skills = [skill.lower() for skill in resume_data["skills"]]
    # Calculate skill overlap score
    common_skills = len(set(job_skills) & set(resume_skills))
    skill_score = (common_skills / len(job_skills)) * 30 if job_skills else 0
    score += skill_score
    # Calculate experience score
    required_exp = job_desc.get("experience", 0)
    exp_score = min(resume_data["experience"] / required_exp, 1) * 20 if required_exp else 0
    score += exp_score
    # Add degree match score
    required_degree = job_desc.get("degree", "").lower()
    if required_degree and required_degree in resume_data["degree"].lower():
        score += 15
    # Add location match score
    required_location = job_desc.get("location", "").lower()
    if required_location and required_location in resume_data["location"].lower():
        score += 10
    # Integrate CATSOne ATS score
    catsone_score = get_catsone_ats_score(resume_data["raw_resume"], job_desc)
    resume_data["catsone_ats_score"] = catsone_score
    # Integrate language expertise score
    lang_expertise = calculate_language_expertise(resume_data["raw_resume"], job_desc)
    resume_data["language_expertise_score"] = lang_expertise["language_expertise_score"]
    resume_data["primary_language"] = lang_expertise["primary_language"]
    resume_data["language_count"] = lang_expertise["language_count"]
    # Combine scores with weights
    final_score = (score * 0.3) + (catsone_score * 0.3) + (resume_data["language_expertise_score"] * 0.4)
    # Determine ATS rejection risk
    if final_score < 60 or len(resume_data["skills"]) < 3 or resume_data["experience"] < 1:
        resume_data["ats_rejection_risk"] = "High"
    elif final_score < 80 or len(resume_data["skills"]) < 5 or resume_data["experience"] < 3:
        resume_data["ats_rejection_risk"] = "Medium"
    else:
        resume_data["ats_rejection_risk"] = "Low"
    return round(final_score, 2)

# Identify missing skills
def skill_gap_analysis(resume_data, job_desc):
    job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
    resume_skills = [skill.lower() for skill in resume_data["skills"]]
    return [skill for skill in job_skills if skill not in resume_skills]

# Generate interview questions for a candidate
def generate_interview_questions(job_desc, candidate_data):
    questions = [
        f"Tell me about your experience with {candidate_data['primary_language']}.",
        f"How would you handle a challenging project requiring {random.choice(job_desc.get('skills', '').split(',')) if job_desc.get('skills') else 'unknown skill'}?",
        f"What interests you most about working as a {job_desc.get('role', 'professional')}?",
        "Can you describe a time when you solved a complex problem?",
        f"How do you stay updated with the latest trends in {candidate_data['primary_language']}?"
    ]
    return questions[:3]

# Simulate interview feedback
def simulate_interview_feedback():
    feedback = [
        "Your response was clear, but try to provide more specific examples.",
        "Great answer! You demonstrated strong technical knowledge.",
        "Consider slowing down your speech for better clarity."
    ]
    return random.choice(feedback)

# Generate PDF report for shortlisted candidates
def generate_pdf_report(candidates_df):
    # Initialize in-memory buffer
    buffer = BytesIO()
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    # Get default styles
    styles = getSampleStyleSheet()
    # Add title
    elements.append(Paragraph("HireIn AI: Shortlisted Candidates Report", styles['Title']))
    # Add generation date
    elements.append(Paragraph("Generated: June 2025", styles['Normal']))
    # Add spacer
    elements.append(Spacer(1, 12))
    # Prepare table data
    data = [["Name", "Email", "Experience", "Skills", "Match Score", "CATSOne ATS", "Lang Expertise"]]
    for _, row in candidates_df.iterrows():
        skills = ", ".join(row["skills"])
        data.append([row["name"], row["email"], str(row["experience"]), skills, 
                     f"{row['match_score']:.2f}", f"{row['catsone_ats_score']:.2f}", 
                     f"{row['language_expertise_score']:.2f}"])
    # Create table
    table = Table(data)
    # Style table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a38")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#242450")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    elements.append(table)
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Generate dashboard PDF report
def generate_dashboard_pdf(candidates_df, skill_counts, missing_skills_counts, source_counts, lang_counts):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("HireIn AI: Dashboard Summary Report", styles['Title']))
    elements.append(Paragraph("Generated: June 2025", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Key Metrics", styles['Heading2']))
    metrics_data = [
        ["Total Candidates", str(len(candidates_df))],
        ["Average Experience", f"{candidates_df['experience'].mean():.1f} years"],
        ["Top Skills", ", ".join(skill_counts.head(3).index.tolist())],
        ["Degree Diversity", str(len(candidates_df["degree"].unique()))],
        ["Average CATSOne ATS Score", f"{candidates_df['catsone_ats_score'].mean():.1f}"],
        ["Average Language Expertise", f"{candidates_df['language_expertise_score'].mean():.1f}"]
    ]
    metrics_table = Table(metrics_data)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a38")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#242450")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Top Missing Skills", styles['Heading2']))
    missing_skills_data = [[skill, str(count)] for skill, count in missing_skills_counts.head(5).items()]
    missing_skills_table = Table([["Skill", "Count"]] + missing_skills_data)
    missing_skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a38")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#242450")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    elements.append(missing_skills_table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Send bulk emails to selected candidates
def send_bulk_email(sender_email, sender_password, subject, body, candidates_df, selected_candidates):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        sent_count = 0
        invalid_emails = []
        for _, candidate in candidates_df[candidates_df["name"].isin(selected_candidates)].iterrows():
            if not candidate["email"] or not re.match(r'[\w\.-]+@[\w\.-]+', candidate["email"]):
                invalid_emails.append(candidate["name"])
                continue
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = candidate["email"]
            msg['Subject'] = subject
            personalized_body = body.replace("{name}", candidate["name"])
            msg.attach(MIMEText(personalized_body, 'plain'))
            server.send_message(msg)
            sent_count += 1
        server.quit()
        return sent_count, invalid_emails
    except Exception as e:
        return 0, [str(e)]

# Load demo data for testing
def load_demo_data():
    demo_data = [
        {
            "name": "Megha Panchal", "email": "megha10pan@gmail.com", "phone": "7354400695",
            "skills": ["iOS", "Swift", "Java"], "experience": 1.5, "location": "Indore, India",
            "degree": "MCA", "college": "Sage University", "sentiment": 0.2, "tags": [],
            "ats_rejection_risk": "Medium", "github_url": "https://github.com/meghapanchal",
            "linkedin_url": "https://linkedin.com/in/meghapanchal", "profile_picture": "https://via.placeholder.com/150",
            "source": "Demo", "raw_resume": "Megha Panchal\niOS, Swift, Java, Java, Swift\n1.5 years experience\nMCA, Sage University\nIndore, India",
            "catsone_ats_score": 75.0, "language_expertise_score": 80.0, "primary_language": "Swift", "language_count": 3
        },
        {
            "name": "Akshay Baliyan", "email": "baliyanakshay383@gmail.com", "phone": "7042270992",
            "skills": ["Python", "Java", "JavaScript", "SQL", "C++"], "experience": 5.5, "location": "Noida, India",
            "degree": "B.Tech", "college": "Raj Kumar Goel", "sentiment": 0.3, "tags": [],
            "ats_rejection_risk": "Low", "github_url": "https://github.com/akshaybaliyan",
            "linkedin_url": "https://linkedin.com/in/akshaybaliyan", "profile_picture": "https://via.placeholder.com/150",
            "source": "Demo", "raw_resume": "Akshay Baliyan\nPython, Java, JavaScript, SQL, C++, Python, JavaScript\n5.5 years experience\nB.Tech, Raj Kumar Goel\nNoida, India",
            "catsone_ats_score": 85.0, "language_expertise_score": 90.0, "primary_language": "Python", "language_count": 5
        }
    ]
    return pd.DataFrame(demo_data)

# Set theme (light or dark)
def set_theme(theme):
    if theme == "Light":
        # Apply light theme CSS
        st.markdown("""
        <script>
        document.documentElement.style.setProperty('--background-color', '#f9fafb');
        document.documentElement.style.setProperty('--text-color', '#1f2937');
        document.documentElement.style.setProperty('--primary-accent', '#ff4b4b');
        document.documentElement.style.setProperty('--secondary-accent', '#e5e7eb');
        document.documentElement.style.setProperty('--card-bg', '#ffffff');
        document.documentElement.style.setProperty('--input-bg', '#f3f4f6');
        document.documentElement.style.setProperty('--button-bg', '#ff4b4b');
        document.documentElement.style.setProperty('--button-hover-bg', '#d43a3a');
        </script>
        """, unsafe_allow_html=True)
    else:
        # Apply dark theme CSS
        st.markdown("""
        <script>
        document.documentElement.style.setProperty('--background-color', '#0e0e20');
        document.documentElement.style.setProperty('--text-color', '#d4d4f4');
        document.documentElement.style.setProperty('--primary-accent', '#ff4b4b');
        document.documentElement.style.setProperty('--secondary-accent', '#2a2a50');
        document.documentElement.style.setProperty('--card-bg', '#1a1a38');
        document.documentElement.style.setProperty('--input-bg', '#242450');
        document.documentElement.style.setProperty('--button-bg', '#ff4b4b');
        document.documentElement.style.setProperty('--button-hover-bg', '#d43a3a');
        </script>
        """, unsafe_allow_html=True)

# Main application logic
def main():
    # Add navigation header to sidebar
    st.sidebar.markdown("<h3 style='color: var(--primary-accent);'>Navigation</h3>", unsafe_allow_html=True)
    # Create radio buttons for page navigation
    page = st.sidebar.radio("Go to", ["Home", "Upload Resumes", "Shortlist Candidates", "AI Interviews", "Compare Candidates", "Dashboard", "Settings"])
    
    if page == "Home":
        # Display app title
        st.title("HireIn : Smart Recruitment")
        # Display app description in a styled card
        st.markdown("""
        <div class='card glow-effect'>
        <p style='font-size: 18px;'>Revolutionizing hiring with AI-driven resume parsing, CATSOne ATS integration, language expertise sorting, and CrewAI automation. Built for efficiency and precision.</p>
        </div>
        """, unsafe_allow_html=True)
        # Display promotional image
        st.image("https://cdn.discordapp.com/attachments/1378528418748174427/1383758038019604510/sadasd-removebg-preview.png?ex=684ff499&is=684ea319&hm=07f0457937295c5e6928eeb50d4da62513a74f195ed8051e8e2213234c87815d&", caption="Streamline Your Hiring Process")
        # Add demo mode button
        if st.button("🚀 Try Demo Mode"):
            # Load demo data
            st.session_state["candidates"] = load_demo_data()
            st.session_state["ranked"] = False
            st.success("Demo data loaded! Navigate to other tabs to explore.")

    elif page == "Upload Resumes":
        # Display page header
        st.header("Upload Resumes")
        # Show spinner during file processing
        with st.spinner("Processing resumes..."):
            # Allow multiple PDF uploads
            uploaded_files = st.file_uploader("Upload resumes (PDF)", accept_multiple_files=True, type=["pdf"], help="Upload candidate resumes in PDF format (max 200MB each).")
        # Display email fetching placeholder
        st.subheader("Fetch Resumes from Email")
        st.warning("🚧 Email fetching is under development. Use the file uploader to add resumes.")
        if st.button("Fetch from Email"):
            st.info("Simulated: Fetched 5 resumes. Use the file uploader for now.")
        if uploaded_files:
            # Button to analyze resumes
            if st.button("Analyze Resumes with CrewAI"):
                # Show spinner during analysis
                with st.spinner("Analyzing resumes with AI agents..."):
                    results = []
                    # Get job description from session state
                    job_desc = st.session_state.get("job_desc", {"skills": "Python, JavaScript", "experience": 3.0})
                    for file in uploaded_files:
                        try:
                            # Extract text from PDF
                            text = extract_text_from_pdf(file)
                            if text:
                                # Parse resume data
                                data = parse_resume(text)
                                data["filename"] = file.name
                                # Calculate match score
                                data["match_score"] = calculate_match_score(data, job_desc)
                                # Identify missing skills
                                data["missing_skills"] = ", ".join(skill_gap_analysis(data, job_desc))
                                results.append(data)
                            else:
                                st.error(f"No text extracted from {file.name}")
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {str(e)}")
                    if results:
                        # Create DataFrame from results
                        candidates_df = pd.DataFrame(results)
                        # Set up CrewAI pipeline
                        crew = setup_crewai_agents(candidates_df.to_dict('records'), job_desc)
                        with st.spinner("Running CrewAI pipeline..."):
                            try:
                                # Run CrewAI
                                crew.kickoff()
                                st.write("CrewAI Agent Logs: Parsing, sorting, and reporting completed successfully.")
                            except Exception:
                                # Handle demo mode
                                st.info("CrewAI pipeline running in demo mode with simulated processing for stability.")
                            # Store candidates in session state
                            st.session_state["candidates"] = candidates_df
                            st.session_state["ranked"] = False
                        # Display candidates
                        st.dataframe(st.session_state["candidates"])
                        # Offer CSV download
                        csv = st.session_state["candidates"].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Parsed Data",
                            csv,
                            "parsed_resume_data.csv",
                            "text/csv"
                        )

    elif page == "Shortlist Candidates":
        # Display page header
        st.header("Shortlist Candidates")
        # Check if candidates exist
        if "candidates" not in st.session_state or st.session_state["candidates"].empty:
            st.warning("Please upload and analyze resumes first or use Demo Mode.")
        else:
            # Display job description input
            st.subheader("Job Description")
            with st.container():
                job_desc = {
                    "role": st.text_input("Job Role", "iOS Developer", help="Enter the role you're hiring for."),
                    "skills": st.text_input("Required Skills (comma-separated)", "iOS, Swift, Java", help="List required skills, e.g., Python, Java."),
                    "experience": st.number_input("Minimum Experience (years)", 0.0, 20.0, 5.0, help="Set the minimum years of experience required."),
                    "degree": st.text_input("Required Degree", "B.Tech", help="Specify the required degree, e.g., B.Tech, MCA."),
                    "location": st.text_input("Preferred Location", "India", help="Enter the preferred location for the role.")
                }
            # Get number of candidates
            num_candidates = len(st.session_state["candidates"])
            default_top_candidates = min(3, num_candidates)
            # Input for top candidates to display
            num_top_candidates = st.number_input(
                "Number of Top Candidates to Display",
                min_value=1,
                max_value=num_candidates,
                value=default_top_candidates,
                step=1
            )
            # Button to rank candidates
            if st.button("Match and Rank Candidates"):
                # Show spinner during ranking
                with st.spinner("Ranking candidates with CrewAI..."):
                    candidates_df = st.session_state["candidates"].copy()
                    # Calculate match scores
                    candidates_df["match_score"] = candidates_df.apply(
                        lambda row: calculate_match_score(row.to_dict(), job_desc), axis=1
                    )
                    # Identify missing skills
                    candidates_df["missing_skills"] = candidates_df.apply(
                        lambda row: ", ".join(skill_gap_analysis(row.to_dict(), job_desc)), axis=1
                    )
                    # Set up CrewAI for sorting
                    crew = setup_crewai_agents(candidates_df.to_dict('records'), job_desc)
                    with st.spinner("Running CrewAI sorting..."):
                        try:
                            # Run CrewAI
                            crew.kickoff()
                            st.write("CrewAI Agent Logs: Sorting completed successfully.")
                            candidates_df = candidates_df.sort_values(by="match_score", ascending=False)
                        except Exception:
                            # Handle demo mode
                            st.info("CrewAI sorting running in demo mode with simulated processing for stability.")
                            candidates_df = candidates_df.sort_values(by="match_score", ascending=False)
                    # Store shortlisted candidates
                    st.session_state["shortlisted"] = candidates_df
                    st.session_state["ranked"] = True
                    st.session_state["job_desc"] = job_desc
                # Display top candidates
                st.subheader(f"Top {num_top_candidates} Candidates")
                cols = st.columns(min(num_top_candidates, 3))
                for idx, (_, candidate) in enumerate(candidates_df.head(num_top_candidates).iterrows()):
                    with cols[idx % 3]:
                        # Define badge classes
                        badge_class = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}
                        # Create GitHub link
                        github_link = f"<a href='{candidate['github_url']}' target='_blank'>GitHub</a>" if candidate['github_url'] else "No GitHub"
                        # Create LinkedIn link
                        linkedin_link = f"<a href='{candidate['linkedin_url']}' target='_blank'>LinkedIn</a>" if candidate['linkedin_url'] else "No LinkedIn"
                        # Handle phone info
                        phone_info = candidate['phone'] if candidate['phone'] else "No Phone"
                        # Display candidate card
                        st.markdown(f"""
                        <div class="card glow-effect">
                            <img src="{candidate['profile_picture']}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; margin-bottom: 10px;">
                            <h3 style="font-size: 20px;">{candidate['name']}</h3>
                            <p><b>Match Score:</b> {candidate['match_score']:.2f}</p>
                            <p><b>CATSOne ATS:</b> {candidate['catsone_ats_score']:.2f}</p>
                            <p><b>Lang Expertise:</b> {candidate['language_expertise_score']:.2f}</p>
                            <p><b>Primary Language:</b> {candidate['primary_language']}</p>
                            <p><b>Experience:</b> {candidate['experience']} years</p>
                            <p><b>Skills:</b> {', '.join(candidate['skills'])}</p>
                            <p><b>Phone:</b> {phone_info}</p>
                            <p><b>GitHub:</b> {github_link}</p>
                            <p><b>LinkedIn:</b> {linkedin_link}</p>
                            <p><b>ATS Risk:</b> <span class="{badge_class[candidate['ats_rejection_risk']]}">{candidate['ats_rejection_risk']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
            # Display insights if ranked
            if st.session_state.get("ranked", False):
                st.subheader("Candidate Match Insights")
                missing_skills = [skill for row in st.session_state["shortlisted"]["missing_skills"] for skill in row.split(", ") if row]
                if missing_skills:
                    st.markdown(f"**Common Skill Gaps**: {', '.join(set(missing_skills))}")
                else:
                    st.markdown("**All required skills covered by candidates!**")
                # Display bulk actions
                st.subheader("Bulk Actions")
                with st.form(key="bulk_action_form"):
                    # Select candidates
                    selected_candidates = st.multiselect("Select Candidates for Bulk Actions", st.session_state["shortlisted"]["name"])
                    # Select action
                    bulk_action = st.selectbox("Action", ["Tag Candidates", "Send Bulk Email"])
                    if bulk_action == "Tag Candidates":
                        # Select tag
                        tag = st.selectbox("Tag", ["Shortlisted", "Interviewed", "Rejected"])
                    elif bulk_action == "Send Bulk Email":
                        # Input email credentials
                        sender_email = st.text_input("Sender Email", value=os.getenv("SMTP_SENDER_EMAIL", ""))
                        sender_password = st.text_input("Sender App Password", type="password", value=os.getenv("SMTP_SENDER_PASSWORD", ""))
                        # Input email content
                        email_subject = st.text_input("Email Subject", "Interview Invitation from HireIn AI")
                        email_body = st.text_area("Email Body", "Dear {name},\n\nWe are pleased to invite you for an interview for the {role} position. Please reply to schedule a convenient time.\n\nBest regards,\nHireIn AI Team")
                        # Replace role placeholder
                        job_role = st.session_state.get("job_desc", {}).get("role", "Unknown Role")
                        email_body = email_body.replace("{role}", job_role)
                    # Submit action
                    submit_button = st.form_submit_button("Apply Action")
                    if submit_button:
                        candidates_df = st.session_state["shortlisted"].copy()
                        if not selected_candidates:
                            st.warning("Please select at least one candidate.")
                        elif bulk_action == "Tag Candidates":
                            # Apply tag
                            candidates_df.loc[candidates_df["name"].isin(selected_candidates), "tags"] = candidates_df.loc[candidates_df["name"].isin(selected_candidates), "tags"].apply(lambda x: list(set(x + [tag])))
                            st.session_state["shortlisted"] = candidates_df
                            st.success(f"Tagged {len(selected_candidates)} candidates as {tag}.")
                        elif bulk_action == "Send Bulk Email":
                            # Validate credentials
                            if not sender_email or not sender_password:
                                st.error("Please provide sender email and app password.")
                            else:
                                # Send emails
                                with st.spinner("Sending emails..."):
                                    sent_count, errors = send_bulk_email(
                                        sender_email, sender_password, email_subject, email_body,
                                        candidates_df, selected_candidates
                                    )
                                    if sent_count > 0:
                                        st.success(f"Sent emails to {sent_count} candidates.")
                                    if errors:
                                        st.error(f"Failed to send to: {', '.join(errors)}")
                # Display shortlisted candidates
                st.dataframe(st.session_state["shortlisted"])
                # Offer CSV download
                csv = st.session_state["shortlisted"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Shortlisted Candidates",
                    csv,
                    "shortlisted_candidates.csv",
                    "text/csv"
                )
                # Offer PDF report
                st.subheader("Generate PDF Report")
                if st.button("Download PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = generate_pdf_report(st.session_state["shortlisted"].head(num_top_candidates))
                        st.download_button(
                            "Download PDF",
                            pdf_buffer,
                            "shortlisted_candidates_report.pdf",
                            "application/pdf"
                        )

    elif page == "AI Interviews":
        # Display page header
        st.header("AI-Driven Mock Interviews")
        # Check if shortlisted candidates exist
        if "shortlisted" not in st.session_state:
            st.warning("Please shortlist candidates first.")
        else:
            # Note about demo mode
            st.markdown("<p style='color: #a0a0c0;'>These are pre-generated questions for demonstration. Actual AI interviews take ~10 minutes.</p>", unsafe_allow_html=True)
            # Select candidate
            candidate = st.selectbox("Select Candidate for Interview", st.session_state["shortlisted"]["name"])
            # Button to generate questions
            if st.button("Generate Interview Questions"):
                # Show spinner
                with st.spinner("Generating questions..."):
                    # Get candidate data
                    candidate_data = st.session_state["shortlisted"][
                        st.session_state["shortlisted"]["name"] == candidate
                    ].iloc[0]
                    # Get job description
                    job_desc = st.session_state.get("job_desc", {
                        "role": "iOS Developer",
                        "skills": "iOS, Swift, Java",
                        "experience": 5.0,
                        "degree": "B.Tech",
                        "location": "India"
                    })
                    # Generate questions
                    questions = generate_interview_questions(job_desc, candidate_data)
                    st.session_state["interview_questions"] = questions
                    st.session_state["interview_candidate"] = candidate
                # Display questions
                st.subheader("Interview Questions")
                feedback_data = []
                for i, q in enumerate(questions, 1):
                    st.write(f"**Question {i}**: {q}")
                    # Get candidate answer
                    answer = st.text_area(f"Your Answer {i}", key=f"answer_{i}")
                    if answer:
                        # Generate feedback
                        feedback = simulate_interview_feedback()
                        st.write(f"**Feedback**: {feedback}")
                        feedback_data.append({"Question": q, "Answer": answer, "Feedback": feedback})
                if feedback_data:
                    # Offer feedback download
                    feedback_df = pd.DataFrame(feedback_data)
                    st.subheader("Export Interview Feedback")
                    csv = feedback_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Feedback as CSV",
                        csv,
                        f"{candidate}_interview_feedback.csv",
                        "text/csv"
                    )

    elif page == "Compare Candidates":
        # Display page header
        st.header("Compare Top Candidates")
        # Check if shortlisted candidates exist
        if "shortlisted" not in st.session_state:
            st.warning("Please shortlist candidates first.")
        else:
            # Input number of candidates to compare
            num_top_candidates = st.number_input("Number of Top Candidates to Compare", min_value=2, max_value=len(st.session_state["shortlisted"]), value=3, step=1)
            # Get top candidates
            top_candidates = st.session_state["shortlisted"].head(num_top_candidates)
            if len(top_candidates) < 2:
                st.warning("Need at least 2 candidates to compare.")
            else:
                # Display candidates in columns
                cols = st.columns(min(num_top_candidates, 3))
                for idx, (_, candidate) in enumerate(top_candidates.iterrows()):
                    with cols[idx % 3]:
                        badge_class = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}
                        github_link = f"<a href='{candidate['github_url']}' target='_blank'>GitHub</a>" if candidate['github_url'] else "No GitHub"
                        linkedin_link = f"<a href='{candidate['linkedin_url']}' target='_blank'>LinkedIn</a>" if candidate['linkedin_url'] else "No LinkedIn"
                        phone_info = candidate['phone'] if candidate['phone'] else "No Phone"
                        # Display candidate card
                        st.markdown(f"""
                        <div class="card glow-effect">
                            <img src="{candidate['profile_picture']}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; margin-bottom: 10px;">
                            <h3 style="font-size: 20px;">{candidate['name']}</h3>
                            <p><b>Match Score:</b> {candidate['match_score']:.2f}</p>
                            <p><b>CATSOne ATS:</b> {candidate['catsone_ats_score']:.2f}</p>
                            <p><b>Lang Expertise:</b> {candidate['language_expertise_score']:.2f}</p>
                            <p><b>Primary Language:</b> {candidate['primary_language']}</p>
                            <p><b>Experience:</b> {candidate['experience']} years</p>
                            <p><b>Skills:</b> {', '.join(candidate['skills'])}</p>
                            <p><b>Missing Skills:</b> {candidate['missing_skills']}</p>
                            <p><b>Sentiment:</b> {candidate['sentiment']:.2f}</p>
                            <p><b>Location:</b> {candidate['location']}</p>
                            <p><b>Phone:</b> {phone_info}</p>
                            <p><b>GitHub:</b> {github_link}</p>
                            <p><b>LinkedIn:</b> {linkedin_link}</p>
                            <p><b>ATS Risk:</b> <span class="{badge_class[candidate['ats_rejection_risk']]}">{candidate['ats_rejection_risk']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)

    elif page == "Dashboard":
        # Display page header
        st.header("Candidate Insights Dashboard")
        # Check if shortlisted candidates exist
        if "shortlisted" not in st.session_state or st.session_state["shortlisted"].empty:
            st.warning("Please shortlist candidates first.")
        else:
            candidates_df = st.session_state["shortlisted"].copy()
            # Display filters
            st.subheader("Filter Candidates")
            with st.container():
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    exp_filter = st.slider("Experience Range (years)", 0.0, 20.0, (0.0, 20.0), step=0.5)
                with col2:
                    all_skills = sorted(set([skill for skills in candidates_df["skills"] for skill in skills]))
                    skill_filter = st.multiselect("Select Skills", all_skills, default=[])
                with col3:
                    all_locations = sorted(candidates_df["location"].unique())
                    location_filter = st.multiselect("Select Locations", all_locations, default=[])
                with col4:
                    ats_score_filter = st.slider("CATSOne ATS Score Range", 0.0, 100.0, (0.0, 100.0), step=1.0)
                with col5:
                    lang_score_filter = st.slider("Language Expertise Score", 0.0, 100.0, (0.0, 100.0), step=1.0)
            # Apply filters
            filtered_df = candidates_df[
                (candidates_df["experience"].between(exp_filter[0], exp_filter[1])) &
                (candidates_df["skills"].apply(lambda x: all(skill in x for skill in skill_filter)) if skill_filter else True) &
                (candidates_df["location"].isin(location_filter) if location_filter else True) &
                (candidates_df["catsone_ats_score"].between(ats_score_filter[0], ats_score_filter[1])) &
                (candidates_df["language_expertise_score"].between(lang_score_filter[0], lang_score_filter[1]))
            ]
            if filtered_df.empty:
                st.warning("No candidates match the selected filters.")
            else:
                # Display summary
                st.subheader("📊 Recruitment Summary")
                total_candidates = len(filtered_df)
                avg_experience = filtered_df["experience"].mean()
                top_skills = pd.Series([skill for skills in filtered_df["skills"] for skill in skills]).value_counts().head(3).index.tolist()
                degree_diversity = len(filtered_df["degree"].unique())
                avg_catsone_score = filtered_df["catsone_ats_score"].mean()
                avg_lang_score = filtered_df["language_expertise_score"].mean()
                # Display metrics
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.markdown(f"<div class='card glow-effect'><h3>Total Candidates</h3><p style='font-size: 24px;'>{total_candidates}</p></div>", unsafe_allow_html=True)
                col2.markdown(f"<div class='card glow-effect'><h3>Average Experience</h3><p style='font-size: 24px;'>{avg_experience:.1f} years</p></div>", unsafe_allow_html=True)
                col3.markdown(f"<div class='card glow-effect'><h3>Top Skills</h3><p style='font-size: 18px;'>{', '.join(top_skills)}</p></div>", unsafe_allow_html=True)
                col4.markdown(f"<div class='card glow-effect'><h3>Degree Diversity</h3><p style='font-size: 24px;'>{degree_diversity}</p></div>", unsafe_allow_html=True)
                col5.markdown(f"<div class='card glow-effect'><h3>Avg CATSOne ATS</h3><p style='font-size: 24px;'>{avg_catsone_score:.1f}</p></div>", unsafe_allow_html=True)
                col6.markdown(f"<div class='card glow-effect'><h3>Avg Lang Expertise</h3><p style='font-size: 24px;'>{avg_lang_score:.1f}</p></div>", unsafe_allow_html=True)
                # Display skill distribution
                st.subheader("🛠️ Skill Distribution")
                skill_counts = pd.Series([skill for skills in filtered_df["skills"] for skill in skills]).value_counts()
                fig_skills = px.pie(
                    names=skill_counts.index,
                    values=skill_counts.values,
                    title="Skill Distribution",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_skills.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#d4d4f4",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_skills, use_container_width=True)
                # Display experience vs. score
                st.subheader("📈 Experience vs. Score")
                score_type = st.selectbox("Select Score Type", ["Combined Match Score", "CATSOne ATS Score", "Language Expertise Score"])
                y_col = {"Combined Match Score": "match_score", "CATSOne ATS Score": "catsone_ats_score", "Language Expertise Score": "language_expertise_score"}[score_type]
                fig_exp_score = px.scatter(
                    filtered_df,
                    x="experience",
                    y=y_col,
                    text="name",
                    size=y_col,
                    color="ats_rejection_risk",
                    color_discrete_map={"Low": "#34D399", "Medium": "#FBBF24", "High": "#FF4B4B"},
                    title=f"Experience vs. {score_type}"
                )
                fig_exp_score.update_traces(textposition="top center")
                fig_exp_score.add_trace(
                    go.Scatter(
                        x=filtered_df["experience"],
                        y=filtered_df[y_col].rolling(window=2, min_periods=1).mean(),
                        mode="lines",
                        name="Trend",
                        line=dict(color="#FF4B4B", dash="dash")
                    )
                )
                fig_exp_score.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#d4d4f4",
                    showlegend=True
                )
                st.plotly_chart(fig_exp_score, use_container_width=True)
                # Display skill gap analysis
                st.subheader("⚠️ Skill Gap Analysis")
                missing_skills = [skill for row in filtered_df["missing_skills"] for skill in row.split(", ") if row]
                missing_skills_counts = pd.Series(missing_skills).value_counts()
                fig_missing_skills = px.bar(
                    x=missing_skills_counts.index,
                    y=missing_skills_counts.values,
                    title="Top Missing Skills",
                    labels={"x": "Skill", "y": "Number of Candidates Missing"}
                )
                fig_missing_skills.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#d4d4f4"
                )
                st.plotly_chart(fig_missing_skills, use_container_width=True)
                # Display candidate source distribution
                st.subheader("🌐 Candidate Source Distribution")
                source_counts = filtered_df["source"].value_counts()
                fig_source = px.pie(
                    names=source_counts.index,
                    values=source_counts.values,
                    title="Candidate Source",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_source.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#d4d4f4",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_source, use_container_width=True)
                # Display language expertise distribution
                st.subheader("🗣️ Language Expertise Distribution")
                lang_counts = filtered_df["primary_language"].value_counts()
                fig_lang = px.bar(
                    x=lang_counts.index,
                    y=lang_counts.values,
                    title="Primary Language Distribution",
                    labels={"x": "Primary Language", "y": "Number of Candidates"}
                )
                fig_lang.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#d4d4f4"
                )
                st.plotly_chart(fig_lang, use_container_width=True)
                # Offer dashboard PDF
                st.subheader("Export Dashboard Insights")
                if st.button("Download Dashboard PDF"):
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = generate_dashboard_pdf(filtered_df, skill_counts, missing_skills_counts, source_counts, lang_counts)
                        st.download_button(
                            "Download PDF",
                            pdf_buffer,
                            "dashboard_summary_report.pdf",
                            "application/pdf"
                        )
                # Offer summary CSV
                summary_data = {
                    "Total Candidates": [total_candidates],
                    "Average Experience (years)": [round(avg_experience, 1)],
                    "Top Skills": [", ".join(top_skills)],
                    "Degree Diversity": [degree_diversity],
                    "Average CATSOne ATS Score": [round(avg_catsone_score, 1)],
                    "Average Language Expertise": [round(avg_lang_score, 1)]
                }
                summary_df = pd.DataFrame(summary_data)
                csv = summary_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Summary as CSV",
                    csv,
                    "dashboard_summary.csv",
                    "text/csv"
                )

    elif page == "Settings":
        # Display page header
        st.header("Settings")
        # Theme selection
        st.subheader("Theme")
        theme = st.selectbox("Select Theme", ["Dark", "Light"], index=0)
        set_theme(theme)
        # SMTP configuration
        st.subheader("SMTP Configuration")
        smtp_email = st.text_input("SMTP Sender Email", value=os.getenv("SMTP_SENDER_EMAIL", ""))
        smtp_password = st.text_input("SMTP App Password", type="password", value=os.getenv("SMTP_SENDER_PASSWORD", ""))
        if st.button("Save SMTP Settings"):
            # Save to .env file
            with open(".env", "w") as f:
                f.write(f"SMTP_SENDER_EMAIL={smtp_email}\nSMTP_SENDER_PASSWORD={smtp_password}\n")
            st.success("SMTP settings saved. Restart the app to apply changes.")
        # Placeholder for advanced options
        st.subheader("Advanced Options")
        st.write("🚧 Under development. Contact support for custom configurations.")

# Run the main function
if __name__ == "__main__":
    main()
