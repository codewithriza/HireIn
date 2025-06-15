<div align="center">
  <h1><code>HireIn</code></h1>
  <h5>🙌 HireIn is a fast, AI-powered hiring tool that reads resumes, matches candidates to job roles, auto-generates interview questions, and gives you smart insights </h5>
</div>



---

## 🌟 Features Overview

| Feature | Description |
|--------|-------------|
| 🧾 **Resume Parsing** | Extracts name, email, skills, GitHub/LinkedIn from PDFs with sentiment insights. |
| 📌 **Candidate Ranking** | Matches applicants to job roles and displays the top N fits. |
| 🎤 **Mock Interviews** | AI-generated questions + feedback for each candidate. |
| ⚖️ **Side-by-Side Comparison** | Juxtapose top candidates for smarter selection. |
| 📊 **Dashboard** | Visual insights into skills, experience, and ATS risk factors. |
| 📝 **PDF Reports** | Generate sleek candidate reports at the click of a button. |
| 🎨 **Theme Toggle** | Light & dark UI themes for different moods. |

---

## 🛠️ Tech Stack

```txt
📦 Python  
🌐 Streamlit - Web App UI  
📄 PyPDF2 - PDF Resume Parsing  
🧠 TextBlob - Sentiment Analysis  
📊 Pandas - Data Handling  
🖨️ ReportLab - PDF Generation  
🕸️ Requests + BeautifulSoup - Web Scraping (LinkedIn & GitHub)  
🎨 Custom CSS - Theming & Styling  
````

---

## 🚀 Getting Started

<details>
  <summary><strong>📌 Prerequisites</strong></summary>

* Python 3.7+
* Git

</details>

<details>
  <summary><strong>⚙️ Installation</strong></summary>

```bash
# Clone the repo
git clone https://github.com/codewithriza/hirein.git
cd hirein-ai

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py
```

</details>

<details>
  <summary><strong>🧪 Try Demo Mode</strong></summary>

No resume? No problem. Click on `🎲 Try Demo Mode` on the home screen to test the features using sample resumes.

</details>

---

## 📂 Project Structure

```
hirein-ai/
├── main.py             # Main Streamlit application
├── requirements.txt    # Python dependencies
├── assets/             # Images (banner.png, logo.jpg)
└── README.md           # This file
```

---


## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for more info.

---
