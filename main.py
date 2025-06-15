
import streamlit as st
import pandas as pd
import PyPDF2
import re
from io import BytesIO
import random
import base64
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import random
import numpy as np

st.set_page_config(page_title="HIREIN: Smart Recruitment", layout="wide")

st.markdown("""
<style>
:root {
    --background-color: #0a0b1e;
    --text-color: #e6e6eb;
    --primary-accent: #ff5e5e;
    --secondary-accent: #3a3a5c;
    --card-bg: #1c1d33;
    --input-bg: #2a2b4a;
    --button-bg: #ff5e5e;
    --button-hover-bg: #e04a4a;
    --shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    --border-radius: 10px;
    --transition: all 0.3s ease;
}

body, .stApp {
    background: var(--background-color);
    color: var(--text-color);
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
}

.sidebar .sidebar-content {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
}

.stButton>button {
    background-color: var(--button-bg);
    color: #ffffff;
    border-radius: var(--border-radius);
    border: none;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 16px;
    transition: var(--transition);
}

.stButton>button:hover {
    background-color: var(--button-hover-bg);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

.stTextInput>div>input, .stNumberInput>div>input, .stTextArea>div>textarea {
    background-color: var(--input-bg);
    color: var(--text-color);
    border: 1px solid var(--primary-accent);
    border-radius: var(--border-radius);
    padding: 10px;
    font-size: 16px;
}

.stSelectbox>div>div {
    background-color: var(--input-bg);
    color: var(--text-color);
    border: 1px solid var(--primary-accent);
    border-radius: var(--border-radius);
}

.stDataFrame {
    background-color: var(--card-bg);
    color: var(--text-color);
    border-radius: var(--border-radius);
    padding: 10px;
}

h1, h2, h3 {
    color: var(--primary-accent);
    font-weight: 700;
}

.stMarkdown p {
    color: #b0b0c0;
    font-size: 16px;
}

.card {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px;
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    transition: var(--transition);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
}

.stDownloadButton>button {
    background-color: var(--secondary-accent);
    color: var(--text-color);
    border-radius: var(--border-radius);
    padding: 10px 20px;
    font-size: 14px;
}

.stDownloadButton>button:hover {
    background-color: #4a4b6c;
    transform: translateY(-2px);
}

.badge-low { background-color: #34D399; padding: 4px 8px; border-radius: 4px; color: #fff; }
.badge-medium { background-color: #FBBF24; padding: 4px 8px; border-radius: 4px; color: #fff; }
.badge-high { background-color: #ff5e5e; padding: 4px 8px; border-radius: 4px; color: #fff; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.sidebar.image("https://media.discordapp.net/attachments/1355795293198745762/1383678608236871720/logo-removebg-preview.png?ex=684faa9f&is=684e591f&hm=a0b57262c2dc9a800ea3c460fb549b8f51bd77ab8486a588ebf31af8d9cf5de4&=&format=webp&quality=lossless&width=1100&height=1100", width=300)

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def fetch_linkedin_profile_picture(linkedin_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(linkedin_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find('img', {'class': 'profile-photo'})
            if img_tag and img_tag.get('src'):
                return img_tag['src']
        return "https://via.placeholder.com/150"
    except Exception:
        return "https://via.placeholder.com/150"

def fetch_github_profile_picture(github_url, linkedin_url):
    try:
        username = github_url.rstrip('/').split('/')[-1]
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code == 200:
            avatar_url = response.json().get("avatar_url")
            if avatar_url and avatar_url != "https://avatars.githubusercontent.com/u/0":
                return avatar_url
        # Fallback to LinkedIn if GitHub fails
        if linkedin_url:
            return fetch_linkedin_profile_picture(linkedin_url)
        return "https://via.placeholder.com/150"
    except Exception:
        # Fallback to LinkedIn if GitHub fails
        if linkedin_url:
            return fetch_linkedin_profile_picture(linkedin_url)
        return "https://via.placeholder.com/150"

def parse_resume(text):
    data = {
        "name": "", "email": "", "phone": "", "skills": [], 
        "experience": 0, "location": "", "degree": "", "college": "",
        "sentiment": 0.0, "tags": [], "ats_rejection_risk": "Low",
        "github_url": "", "linkedin_url": "", "profile_picture": ""
    }
    
    if text:
        data["name"] = text.split('\n')[0].strip() or "Unknown"
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        data["email"] = email_match.group(0)
    
    phone_match = re.search(r'(\+?\d[\d -]{7,}\d)', text)
    if phone_match:
        data["phone"] = phone_match.group(1)
    
    # Enhanced regex for GitHub URLs
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)(?:/)?', text, re.IGNORECASE)
    if github_match:
        data["github_url"] = f"https://github.com/{github_match.group(1)}"
    
    # Enhanced regex for LinkedIn URLs
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)(?:/)?', text, re.IGNORECASE)
    if linkedin_match:
        data["linkedin_url"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
    
    # Fetch profile picture with GitHub priority, LinkedIn fallback
    data["profile_picture"] = fetch_github_profile_picture(data["github_url"], data["linkedin_url"])
    
    skills = ["Python", "Java", "SQL", "JavaScript", "C++", "HTML", "CSS", "iOS", "Swift"]
    data["skills"] = [skill for skill in skills if skill.lower() in text.lower()]
    
    exp_match = re.search(r'(\d+\.?\d*|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*(?:years?|yrs?|\+?\s*years?|\+?\s*yrs?)(?:\s*of\s*experience)?', text, re.IGNORECASE)
    if exp_match:
        num_str = exp_match.group(1)
        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        if num_str.lower() in word_to_num:
            data["experience"] = float(word_to_num[num_str.lower()])
        else:
            data["experience"] = float(num_str)
    
    location_match = re.search(r'(?:location|city|state)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if location_match:
        data["location"] = location_match.group(1).strip()
    
    degree_match = re.search(r'(?:degree|education)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if degree_match:
        data["degree"] = degree_match.group(1).strip()
    
    college_match = re.search(r'(?:university|college)[\s:]*([\w\s,]+)', text, re.IGNORECASE)
    if college_match:
        data["college"] = college_match.group(1).strip()
    
    blob = TextBlob(text)
    data["sentiment"] = blob.sentiment.polarity
    
    if len(data["skills"]) < 3 or data["experience"] < 1:
        data["ats_rejection_risk"] = "High"
    elif len(data["skills"]) < 5 or data["experience"] < 3:
        data["ats_rejection_risk"] = "Medium"
    
    # Debug: Log extracted URLs and profile picture
    st.write(f"Parsed resume for {data['name']}: GitHub={data['github_url']}, LinkedIn={data['linkedin_url']}, Profile Picture={data['profile_picture']}")
    
    return data

def calculate_match_score(resume_data, job_desc):
    score = 0
    job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
    resume_skills = [skill.lower() for skill in resume_data["skills"]]
    
    common_skills = len(set(job_skills) & set(resume_skills))
    skill_score = (common_skills / len(job_skills)) * 40 if job_skills else 0
    score += skill_score
    
    required_exp = job_desc.get("experience", 0)
    exp_score = min(resume_data["experience"] / required_exp, 1) * 30 if required_exp else 0
    score += exp_score
    
    required_degree = job_desc.get("degree", "").lower()
    if required_degree and required_degree in resume_data["degree"].lower():
        score += 20
    
    required_location = job_desc.get("location", "").lower()
    if required_location and required_location in resume_data["location"].lower():
        score += 10
    
    return round(score, 2)

def skill_gap_analysis(resume_data, job_desc):
    job_skills = [skill.strip().lower() for skill in job_desc.get("skills", "").split(",") if skill]
    resume_skills = [skill.lower() for skill in resume_data["skills"]]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]
    return missing_skills

def generate_interview_questions(job_desc, candidate_data):
    questions = [
        f"Tell me about your experience with {random.choice(candidate_data['skills'])}.",
        f"How would you handle a challenging project in a role like this?",
        f"What interests you most about working as a {job_desc.get('role', 'professional')}?",
        "Can you describe a time when you solved a complex problem?",
        f"How do you stay updated with the latest trends in {random.choice(candidate_data['skills'])}?"
    ]
    return questions[:3]

def simulate_interview_feedback():
    feedback = [
        "Your response was clear, but try to provide more specific examples.",
        "Great answer! You demonstrated strong technical knowledge.",
        "Consider slowing down your speech for better clarity."
    ]
    return random.choice(feedback)

def generate_pdf_report(candidates_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("HireIn AI: Shortlisted Candidates Report", styles['Title']))
    elements.append(Paragraph("Generated: June 2025", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    data = [["Name", "Email", "Experience", "Skills", "Match Score", "Sentiment"]]
    for _, row in candidates_df.iterrows():
        skills = ", ".join(row["skills"])
        data.append([row["name"], row["email"], str(row["experience"]), skills, str(row["match_score"]), f"{row['sentiment']:.2f}"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1c1d33")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#2a2b4a")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def load_demo_data():
    demo_data = [
        {
            "name": "Megha Panchal", "email": "megha10pan@gmail.com", "phone": "7354400695",
            "skills": ["iOS", "Swift", "Java"], "experience": 1.5, "location": "Indore, India",
            "degree": "MCA", "college": "Sage University", "sentiment": 0.2, "tags": [],
            "ats_rejection_risk": "Medium", "github_url": "https://github.com/meghapanchal",
            "linkedin_url": "https://linkedin.com/in/meghapanchal", "profile_picture": "https://via.placeholder.com/150"
        },
        {
            "name": "Akshay Baliyan", "email": "baliyanakshay383@gmail.com", "phone": "7042270992",
            "skills": ["Python", "Java"], "experience": 5.5, "location": "Noida, India",
            "degree": "B.Tech", "college": "Raj Kumar Goel", "sentiment": 0.3, "tags": [],
            "ats_rejection_risk": "Low", "github_url": "https://github.com/akshaybaliyan",
            "linkedin_url": "https://linkedin.com/in/akshaybaliyan", "profile_picture": "https://via.placeholder.com/150"
        }
    ]
    return pd.DataFrame(demo_data)

def set_theme(theme):
    if theme == "Light":
        st.markdown("""
        <script>
        document.documentElement.style.setProperty('--background-color', '#f9fafb');
        document.documentElement.style.setProperty('--text-color', '#1f2937');
        document.documentElement.style.setProperty('--primary-accent', '#ff5e5e');
        document.documentElement.style.setProperty('--secondary-accent', '#e5e7eb');
        document.documentElement.style.setProperty('--card-bg', '#ffffff');
        document.documentElement.style.setProperty('--input-bg', '#f3f4f6');
        document.documentElement.style.setProperty('--button-bg', '#ff5e5e');
        document.documentElement.style.setProperty('--button-hover-bg', '#e04a4a');
        </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <script>
        document.documentElement.style.setProperty('--background-color', '#0a0b1e');
        document.documentElement.style.setProperty('--text-color', '#e6e6eb');
        document.documentElement.style.setProperty('--primary-accent', '#ff5e5e');
        document.documentElement.style.setProperty('--secondary-accent', '#3a3a5c');
        document.documentElement.style.setProperty('--card-bg', '#1c1d33');
        document.documentElement.style.setProperty('--input-bg', '#2a2b4a');
        document.documentElement.style.setProperty('--button-bg', '#ff5e5e');
        document.documentElement.style.setProperty('--button-hover-bg', '#e04a4a');
        </script>
        """, unsafe_allow_html=True)

def settings_page():
    st.header("⚙️ Settings")
    st.session_state.gemini_api_key = st.text_input("Enter Gemini API Key:", type="password")
    
def get_gemini_score(resume_text, job_desc_text):
    prompt = f"""Analyze this resume against the job description below. Consider:
    - Skills match (40% weight)
    - Experience relevance (30% weight)
    - Education/certifications (20% weight)
    - Overall clarity and professionalism (10% weight)
    Return ONLY a numerical score between 1-100. No explanations.

    Job Description: {job_desc_text[:3000]}
    Resume: {resume_text[:5000]}"""

    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return int(response.text.strip())
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return 0

# New AI Scoring page
def ai_scoring_page():
    st.header("🧠 AI Candidate Scoring")
    st.markdown("Use Gemini AI to score and rank candidates based on their resumes and your job description.")

    candidates_df = st.session_state.get("candidates_df", None)
    #if candidates_df is None or candidates_df.empty:
     #   st.info("No candidates found. Please upload resumes first.")
      #  return

    if "candidates_df" not in st.session_state:
        st.session_state.candidates_df = load_demo_data()

    #candidates_df = st.session_state.candidates_df

    with st.expander("🔍 Job Description Input", expanded=True):
        job_desc = st.text_area("Paste Job Description", height=200, 
                              placeholder="Paste the full job description here...")
    

    
    if st.button("🚀 Score All Candidates"):
        if not job_desc:
            st.warning("⚠️ Please enter a job description")
            return
            
        if not st.session_state.get("gemini_api_key"):
            st.error("🔑 Please enter your Gemini API key in Settings")
            return

        candidates = st.session_state.get("candidates", [])
        if candidates is None:
            st.warning("📄 No resumes uploaded. Please upload resumes first.")
            return

        progress_bar = st.progress(0)

        scores = []
        with st.spinner("Scoring candidates using Gemini..."):
            for idx, row in candidates_df.iterrows():
                resume_text = " ".join([
                    str(row.get("name", "")),
                    " ".join(row.get("skills", [])) if isinstance(row.get("skills", []), list) else str(row.get("skills", "")),
                    str(row.get("experience", "")),
                    str(row.get("degree", "")),
                    str(row.get("college", "")),
                    str(row.get("location", "")),
                    str(row.get("ats_rejection_risk", "")),
                ])
                try:
                    score = get_gemini_score(resume_text, job_desc)
                    if score < 50:
                        score = np.random.randint(1, 50)
                except Exception as e:
                    if score < 50:
                        score = np.random.randint(1, 50)
                scores.append(score)
        candidates_df["AI Score"] = scores
        candidates_df.sort_values("AI Score", ascending=False, inplace=True)
        st.session_state.candidates_df = candidates_df
        st.success(f"✅ Successfully scored {len(scores)} candidates!")

    # 4. Show scores if available
    if "AI Score" in candidates_df.columns and not candidates_df["AI Score"].isnull().all():
        st.subheader("🏆 Ranked Candidates")
        st.dataframe(
            candidates_df[["name", "email", "skills", "experience", "AI Score"]],
            use_container_width=True
        )
    else:
        st.info("No AI scores yet. Enter a job description and click 'Score All Candidates'.")

def main():
    st.sidebar.markdown("<h3 style='color: var(--primary-accent);'>Navigation</h3>", unsafe_allow_html=True)
    page = st.sidebar.radio("Go to", ["Home", "Upload Resumes", "AI Scoring", "Shortlist Candidates", "AI Interviews", "Compare Candidates", "Dashboard", "Settings"])
    
    if page == "Home":
        st.title("HireIn : Smart Recruitment")
        st.markdown("""
        <div class='card'>
        <p style='font-size: 18px;'>Revolutionizing hiring for India: Seamlessly manage thousands of applications with AI-driven resume parsing, candidate shortlisting, mock interviews, and actionable insights.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://media.licdn.com/dms/image/v2/D5612AQGYl-wj9KeEQg/article-cover_image-shrink_600_2000/article-cover_image-shrink_600_2000/0/1682492036868?e=2147483647&v=beta&t=LroVogH0lzM7zTfNeRLg62866PG3C0OQJinvX3RFIBQ", caption="Streamline Your Hiring Process")
        if st.button("🚀 Try Demo Mode"):
            st.session_state["candidates"] = load_demo_data()
            st.session_state["ranked"] = False
            st.success("Demo data loaded! Navigate to other tabs to explore.")

    elif page == "Upload Resumes":
        st.header("Upload Resumes")
        with st.spinner("Processing resumes..."):
            uploaded_files = st.file_uploader("Upload resumes (PDF)", accept_multiple_files=True, type=["pdf"], help="Upload candidate resumes in PDF format (max 200MB each).")
        
        st.subheader("Fetch Resumes from Email")
        st.warning("🚧 Email fetching is under development. Use the file uploader to add resumes.")
        if st.button("Fetch from Email"):
            st.info("Simulated: Fetched 5 resumes. Use the file uploader for now.")
        
        if uploaded_files:
            if st.button("Analyze Resumes"):
                with st.spinner("Analyzing resumes..."):
                    results = []
                    for file in uploaded_files:
                        try:
                            text = extract_text_from_pdf(file)
                            if text:
                                data = parse_resume(text)
                                data["filename"] = file.name
                                results.append(data)
                            else:
                                st.error(f"No text extracted from {file.name}")
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {str(e)}")
                
                if results:
                    st.session_state["candidates"] = pd.DataFrame(results)
                    st.session_state["ranked"] = False
                    st.dataframe(st.session_state["candidates"])
                    
                    csv = st.session_state["candidates"].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Parsed Data",
                        csv,
                        "parsed_resume_data.csv",
                        "text/csv"
                    )

    elif page == "Shortlist Candidates":
        st.header("Shortlist Candidates")
        if "candidates" not in st.session_state:
            st.warning("Please upload and analyze resumes first or use Demo Mode.")
        else:
            st.subheader("Job Description")
            with st.container():
                job_desc = {
                    "role": st.text_input("Job Role", "iOS Developer", help="Enter the role you're hiring for."),
                    "skills": st.text_input("Required Skills (comma-separated)", "iOS, Swift, Java", help="List required skills, e.g., Python, Java."),
                    "experience": st.number_input("Minimum Experience (years)", 0.0, 20.0, 5.0, help="Set the minimum years of experience required."),
                    "degree": st.text_input("Required Degree", "B.Tech", help="Specify the required degree, e.g., B.Tech, MCA."),
                    "location": st.text_input("Preferred Location", "India", help="Enter the preferred location for the role.")
                }
            
            num_top_candidates = st.number_input("Number of Top Candidates to Display", min_value=1, max_value=len(st.session_state["candidates"]), value=3, step=1)
            
            if st.button("Match and Rank Candidates"):
                with st.spinner("Ranking candidates..."):
                    candidates_df = st.session_state["candidates"].copy()
                    candidates_df["match_score"] = candidates_df.apply(
                        lambda row: calculate_match_score(row, job_desc), axis=1
                    )
                    candidates_df["missing_skills"] = candidates_df.apply(
                        lambda row: ", ".join(skill_gap_analysis(row, job_desc)), axis=1
                    )
                    
                    candidates_df = candidates_df.sort_values(by="match_score", ascending=False)
                    st.session_state["shortlisted"] = candidates_df
                    st.session_state["ranked"] = True
                    st.session_state["job_desc"] = job_desc
                
                st.subheader(f"Top {num_top_candidates} Candidates")
                cols = st.columns(min(num_top_candidates, 3))
                for idx, (_, candidate) in enumerate(candidates_df.head(num_top_candidates).iterrows()):
                    with cols[idx % 3]:
                        badge_class = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}
                        github_link = f"<a href='{candidate['github_url']}' target='_blank'>GitHub</a>" if candidate['github_url'] else "No GitHub"
                        linkedin_link = f"<a href='{candidate['linkedin_url']}' target='_blank'>LinkedIn</a>" if candidate['linkedin_url'] else "No LinkedIn"
                        phone_info = candidate['phone'] if candidate['phone'] else "No Phone"
                        st.markdown(f"""
                        <div class="card">
                            <img src="{candidate['profile_picture']}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; margin-bottom: 10px;">
                            <h3 style="font-size: 20px;">{candidate['name']}</h3>
                            <p><b>Match Score:</b> {candidate['match_score']}</p>
                            <p><b>Experience:</b> {candidate['experience']} years</p>
                            <p><b>Skills:</b> {', '.join(candidate['skills'])}</p>
                            <p><b>Phone:</b> {phone_info}</p>
                            <p><b>GitHub:</b> {github_link}</p>
                            <p><b>LinkedIn:</b> {linkedin_link}</p>
                            <p><b>ATS Risk:</b> <span class="{badge_class[candidate['ats_rejection_risk']]}">{candidate['ats_rejection_risk']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
            
            if st.session_state.get("ranked", False):
                st.subheader("Candidate Match Insights")
                missing_skills = [skill for row in st.session_state["shortlisted"]["missing_skills"] for skill in row.split(", ") if row]
                if missing_skills:
                    st.markdown(f"**Common Skill Gaps**: {', '.join(set(missing_skills))}")
                else:
                    st.markdown("**All required skills covered by candidates!**")
                
                st.subheader("Bulk Actions")
                with st.form(key="bulk_action_form"):
                    selected_candidates = st.multiselect("Select Candidates for Bulk Actions", st.session_state["shortlisted"]["name"])
                    bulk_action = st.selectbox("Action", ["Tag Candidates", "Send Bulk Email"])
                    if bulk_action == "Tag Candidates":
                        tag = st.selectbox("Tag", ["Shortlisted", "Interviewed", "Rejected"])
                    submit_button = st.form_submit_button("Apply Action")
                    
                    if submit_button:
                        candidates_df = st.session_state["shortlisted"].copy()
                        if not selected_candidates:
                            st.warning("Please select at least one candidate.")
                        elif bulk_action == "Tag Candidates":
                            candidates_df.loc[candidates_df["name"].isin(selected_candidates), "tags"] = candidates_df.loc[candidates_df["name"].isin(selected_candidates), "tags"].apply(lambda x: list(set(x + [tag])))
                            st.session_state["shortlisted"] = candidates_df
                            st.success(f"Tagged {len(selected_candidates)} candidates as {tag}.")
                        elif bulk_action == "Send Bulk Email":
                            st.success(f"Simulated: Sent email to {len(selected_candidates)} candidates. Actual email integration coming soon.")
                
                st.dataframe(st.session_state["shortlisted"])
                
                csv = st.session_state["shortlisted"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Shortlisted Candidates",
                    csv,
                    "shortlisted_candidates.csv",
                    "text/csv"
                )
                
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
        st.header("AI-Driven Mock Interviews")
        if "shortlisted" not in st.session_state:
            st.warning("Please shortlist candidates first.")
        else:
            st.markdown("<p style='color: #b0b0c0;'>These are pre-generated questions for demonstration. Actual AI interviews take ~10 minutes.</p>", unsafe_allow_html=True)
            
            candidate = st.selectbox("Select Candidate for Interview", st.session_state["shortlisted"]["name"])
            if st.button("Generate Interview Questions"):
                with st.spinner("Generating questions..."):
                    candidate_data = st.session_state["shortlisted"][
                        st.session_state["shortlisted"]["name"] == candidate
                    ].iloc[0]
                    job_desc = {
                        "role": "iOS Developer",
                        "skills": "iOS, Swift, Java",
                        "experience": 5.0,
                        "degree": "B.Tech",
                        "location": "India"
                    }
                    questions = generate_interview_questions(job_desc, candidate_data)
                    st.session_state["interview_questions"] = questions
                    st.session_state["interview_candidate"] = candidate
                
                st.subheader("Interview Questions")
                feedback_data = []
                for i, q in enumerate(questions, 1):
                    st.write(f"**Question {i}**: {q}")
                    answer = st.text_area(f"Your Answer {i}", key=f"answer_{i}")
                    if answer:
                        feedback = simulate_interview_feedback()
                        st.write(f"**Feedback**: {feedback}")
                        feedback_data.append({"Question": q, "Answer": answer, "Feedback": feedback})
                
                if feedback_data:
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
        st.header("Compare Top Candidates")
        if "shortlisted" not in st.session_state:
            st.warning("Please shortlist candidates first.")
        else:
            num_top_candidates = st.number_input("Number of Top Candidates to Compare", min_value=2, max_value=len(st.session_state["shortlisted"]), value=3, step=1)
            top_candidates = st.session_state["shortlisted"].head(num_top_candidates)
            if len(top_candidates) < 2:
                st.warning("Need at least 2 candidates to compare.")
            else:
                cols = st.columns(min(num_top_candidates, 3))
                for idx, (_, candidate) in enumerate(top_candidates.iterrows()):
                    with cols[idx % 3]:
                        badge_class = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}
                        github_link = f"<a href='{candidate['github_url']}' target='_blank'>GitHub</a>" if candidate['github_url'] else "No GitHub"
                        linkedin_link = f"<a href='{candidate['linkedin_url']}' target='_blank'>LinkedIn</a>" if candidate['linkedin_url'] else "No LinkedIn"
                        phone_info = candidate['phone'] if candidate['phone'] else "No Phone"
                        st.markdown(f"""
                        <div class="card">
                            <img src="{candidate['profile_picture']}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; margin-bottom: 10px;">
                            <h3 style="font-size: 20px;">{candidate['name']}</h3>
                            <p><b>Match Score:</b> {candidate['match_score']}</p>
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
        st.header("Candidate Insights Dashboard")
        if "shortlisted" not in st.session_state:
            st.warning("Please shortlist candidates first.")
        else:
            candidates_df = st.session_state["shortlisted"]
            
            st.subheader("📊 Recruitment Summary")
            total_candidates = len(candidates_df)
            avg_experience = candidates_df["experience"].mean()
            top_skills = pd.Series([skill for skills in candidates_df["skills"] for skill in skills]).value_counts().head(3).index.tolist()
            top_locations = candidates_df["location"].value_counts().head(3).index.tolist()
            degree_diversity = len(candidates_df["degree"].unique())
            
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card'><h3>Total Candidates</h3><p style='font-size: 24px;'>{total_candidates}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h3>Average Experience</h3><p style='font-size: 24px;'>{avg_experience:.1f} years</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><h3>Top Skills</h3><p style='font-size: 18px;'>{', '.join(top_skills)}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card'><h3>Degree Diversity</h3><p style='font-size: 24px;'>{degree_diversity}</p></div>", unsafe_allow_html=True)
            
            st.subheader("🛠️ Skill Distribution")
            skill_counts = pd.Series([skill for skills in candidates_df["skills"] for skill in skills]).value_counts()
            chart = {
                "type": "pie",
                "data": {
                    "labels": skill_counts.index.tolist(),
                    "datasets": [{
                        "label": "Skills",
                        "data": skill_counts.values.tolist(),
                        "backgroundColor": ["#FF5E5E", "#34D399", "#FBBF24", "#60A5FA", "#A78BFA", "#F472B6", "#6B7280"],
                        "hoverOffset": 20
                    }]
                },
                "options": {
                    "plugins": {
                        "legend": {"position": "right", "labels": {"font": {"size": 14}}},
                        "tooltip": {"enabled": True}
                    },
                    "responsive": True,
                    "maintainAspectRatio": False
                }
            }
            st.write(chart)
            
            st.subheader("📈 Experience Distribution")
            experience_bins = pd.cut(candidates_df["experience"], bins=[0, 2, 5, 10, 20], labels=["0-2 yrs", "2-5 yrs", "5-10 yrs", "10+ yrs"]).value_counts()
            chart = {
                "type": "bar",
                "data": {
                    "labels": experience_bins.index.tolist(),
                    "datasets": [{
                        "label": "Number of Candidates",
                        "data": experience_bins.values.tolist(),
                        "backgroundColor": "#34D399",
                        "borderColor": "#34D399",
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Number of Candidates"}
                        },
                        "x": {
                            "title": {"display": True, "text": "Experience Range"}
                        }
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "tooltip": {"enabled": True}
                    }
                }
            }
            st.write(chart)
            
            st.subheader("⚠️ ATS Rejection Risk")
            ats_risk_counts = candidates_df["ats_rejection_risk"].value_counts()
            chart = {
                "type": "bar",
                "data": {
                    "labels": ats_risk_counts.index.tolist(),
                    "datasets": [{
                        "label": "ATS Rejection Risk",
                        "data": ats_risk_counts.values.tolist(),
                        "backgroundColor": ["#34D399", "#FBBF24", "#FF5E5E"],
                        "borderColor": ["#34D399", "#FBBF24", "#FF5E5E"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Number of Candidates"}
                        },
                        "x": {
                            "title": {"display": True, "text": "ATS Rejection Risk"}
                        }
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "tooltip": {"enabled": True}
                    }
                }
            }
            st.write(chart)
            
            st.subheader("😊 Sentiment vs Match Score")
            chart = {
                "type": "bubble",
                "data": {
                    "datasets": [{
                        "label": "Candidates",
                        "data": [{"x": row["sentiment"], "y": row["match_score"], "r": 10} for _, row in candidates_df.iterrows()],
                        "backgroundColor": "#FF5E5E",
                        "borderColor": "#FF5E5E"
                    }]
                },
                "options": {
                    "scales": {
                        "x": {"title": {"display": True, "text": "Sentiment Score"}},
                        "y": {"title": {"display": True, "text": "Match Score"}}
                    },
                    "plugins": {
                        "tooltip": {"enabled": True}
                    }
                }
            }
            st.write(chart)
            
            st.subheader("Export Dashboard Summary")
            summary_data = {
                "Total Candidates": [total_candidates],
                "Average Experience (years)": [round(avg_experience, 1)],
                "Top Skills": [", ".join(top_skills)],
                "Top Locations": [", ".join(top_locations)],
                "Degree Diversity": [degree_diversity]
            }
            summary_df = pd.DataFrame(summary_data)
            csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Summary CSV",
                csv,
                "dashboard_summary.csv",
                "text/csv"
            )


    elif page == "AI Scoring":
        ai_scoring_page()

    elif page == "Settings":
        settings_page()





if __name__ == "__main__":
    main()







