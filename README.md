<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=36&pause=1000&color=0EA5E9&center=true&vCenter=true&width=700&lines=AI+Scholar+Hunt;Intelligent+Scholarship+Platform;LLM+%2B+RAG+%2B+Prompt+Engineering;Built+for+Pakistani+Students" alt="Typing SVG" />
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/LLM+RAG-Powered-0EA5E9?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/No_API_Key-Required-22c55e?style=for-the-badge&logo=checkmarx&logoColor=white"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask--Login-Auth-F97316?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/ReportLab-PDF_Gen-DC2626?style=for-the-badge&logo=adobeacrobatreader&logoColor=white"/>
  <img src="https://img.shields.io/badge/python--docx-DOCX_Gen-2563EB?style=for-the-badge&logo=microsoftword&logoColor=white"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Prompt_Engineering-Advanced-8B5CF6?style=for-the-badge&logo=OpenAI&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask--Mail-Email_Service-EA4335?style=for-the-badge&logo=gmail&logoColor=white"/>
  <img src="https://img.shields.io/badge/Final_Year-Project_2026-0369A1?style=for-the-badge&logo=bookstack&logoColor=white"/>
  <img src="https://img.shields.io/badge/Made_in-Pakistan_🇵🇰-14B8A6?style=for-the-badge"/>
</p>

<br/>

<blockquote>
<strong>🎓 AI Scholar Hunt</strong> is a full-stack, LLM + RAG powered scholarship discovery and application assistance platform — purpose-built for Pakistani students pursuing international education opportunities. It runs entirely without any paid or external API key, using a custom-built AI engine powered by Retrieval-Augmented Generation and advanced Prompt Engineering on a local scholarship knowledge base.
</blockquote>

<br/>

[![Add](https://img.shields.io/badge/Add-0EA5E9?style=for-the-badge&logo=googlechrome&logoColor=white)](https://ai-scholar-hunt.vly.site/)

---

</div>

## 📌 Table of Contents

- [🌟 Project Overview](#-project-overview)
- [🎯 Problem Statement](#-problem-statement)
- [🚀 Features](#-features)
- [🧠 AI Engine — How It Works](#-ai-engine--how-it-works)
- [🗂️ Project Structure](#️-project-structure)
- [⚙️ Tech Stack](#️-tech-stack)
- [🔐 Authentication System](#-authentication-system)
- [🌍 CV Builder — Multi-Country Support](#-cv-builder--multi-country-support)
- [📊 Scholarship Knowledge Base](#-scholarship-knowledge-base)
- [🛠️ Installation & Setup](#️-installation--setup)
- [📁 Environment Configuration](#-environment-configuration)
- [🧩 Blueprint Architecture](#-blueprint-architecture)
- [👨‍💻 Authors](#-authors)

---

## 🌟 Project Overview

**AI Scholar Hunt** is a comprehensive web application that acts as an intelligent scholarship advisor for students. Instead of manually browsing dozens of websites, students can simply ask the AI chatbot questions like *"What scholarships are available for MS in Germany?"* or *"Tell me about the DAAD scholarship deadline"* — and instantly receive structured, detailed responses pulled from a curated knowledge base of **51+ international scholarships**.

The platform goes beyond just information retrieval. It also helps students:
- Check their eligibility before applying
- Analyze how strong their application is
- Write and refine their essays and SOPs
- Check if their CV is ATS-compliant
- Generate a country-specific formatted CV ready for submission

All of this runs locally — **no OpenAI, no Anthropic, no Gemini API key required.**

---

## 🎯 Problem Statement

Pakistani students face several challenges when applying for international scholarships:

- **Information Overload** — Hundreds of scholarships with different requirements, deadlines, and formats
- **No Personalized Guidance** — Generic websites don't check your specific eligibility
- **CV Format Confusion** — Different countries require radically different CV formats (e.g., Germany wants a photo, USA does not)
- **Weak Applications** — Students submit generic SOPs without tailoring them to scholarship criteria
- **Language Barrier** — Complex scholarship documents are hard to parse

**AI Scholar Hunt solves all of these problems in one platform.**

---

## 🚀 Features

### 🤖 AI-Powered Scholarship Chatbot
- Answers natural language queries about any scholarship in the database
- Returns complete scholarship details: deadlines, eligibility, coverage, documents, apply links
- Built using **RAG (Retrieval-Augmented Generation)** on a local `.txt` knowledge base
- Scoring algorithm ranks results by relevance (name → country → institution → level → full-text)
- Supports follow-up queries and related scholarship suggestions
- Markdown-formatted responses rendered beautifully in the UI

### ✅ Eligibility Checker
- Students enter their CGPA, degree level, country of interest, and other details
- Custom scoring algorithm checks eligibility against **8+ scholarships**
- Returns a match percentage and specific eligibility feedback per scholarship
- Helps students prioritize which scholarships to apply for

### 💪 Application Strength Analyzer
- Students paste their SOP or CV text
- AI evaluates the content against scholarship-specific criteria
- Returns strengths, weaknesses, and actionable improvement suggestions
- Uses Prompt Engineering to simulate expert scholarship reviewer feedback

### 📝 Essay & SOP Writing Assistant
- AI-guided drafting tool for scholarship essays and Statements of Purpose
- Helps structure arguments, highlight achievements, and tailor tone
- Supports different essay styles (motivational, research-focused, career-oriented)

### 📄 ATS CV Checker
- Scans a resume/CV against a job or scholarship description
- Returns ATS match score, matched keywords, and missing keywords
- Gives specific suggestions to improve ATS compatibility
- Essential for scholarships that use automated screening systems

### 🌍 Multi-Country CV Builder
- Generates fully formatted CVs tailored to **14 countries** across **4 template groups**
- Supports **PDF** and **DOCX** export
- Photo embedding for countries that require it (Germany, UAE, China, etc.)
- Country-specific fields: passport number (China/UAE), DOB/nationality (Germany), Europass format (Belgium/France)

### 🔐 Full Authentication System
- User registration and login with Flask-Login
- Secure password hashing
- Password reset via email (token-based, 1-hour expiry)
- Mobile + web responsive reset email template

### 👤 User Profile Management
- View and edit personal profile
- Theme and language preferences
- Security settings (change password)
- Profile completion progress tracker
- Avatar upload support

### 📧 Email Service
- Flask-Mail primary with direct SMTP fallback (5 retries)
- Supports Gmail SMTP on ports 465 (SSL) and 587 (TLS)
- Beautiful HTML email templates — mobile and web responsive

---

## 🧠 AI Engine — How It Works

The AI engine is built entirely without any external LLM API. It combines three techniques:

### 1. Knowledge Base (RAG — Retrieval)
```
scholarships/
├── daad_scholarship.txt          ← JSON-structured scholarship data
├── fulbright_scholarship.txt
├── australia_awards.txt
└── ... (51+ files)
```

Each `.txt` file contains structured JSON with fields like:
`scholarship_name`, `study_in`, `institution`, `level_of_study`,
`deadline`, `coverage`, `eligibility`, `required_documents`, `apply_link`

### 2. Scoring Algorithm (RAG — Augmented Retrieval)
```
User Query: "DAAD deadline Germany masters"
      │
      ▼
  Normalize & Tokenize
      │
      ▼
  Score Each Scholarship:
  ┌──────────────────────────────────┐
  │  Name exact match    → +100 pts  │
  │  Country match       →  +50 pts  │
  │  Institution match   →  +40 pts  │
  │  Study level match   →  +30 pts  │
  │  Full text word hit  →  +10 pts  │
  └──────────────────────────────────┘
      │
      ▼
  Sort by Score → Top Results
      │
      ▼
  Format as Markdown Response
```

### 3. Prompt Engineering (Generation)
- Response templates are carefully engineered to produce structured, readable output
- Handles 3 response modes:
  - **Exact match** → Full scholarship details
  - **General query** → Top 3 matches with summaries
  - **No match** → Suggests related scholarships from database
- Emoji-enhanced formatting for readability
- Follow-up suggestion prompts embedded in every response

---

## 🗂️ Project Structure

```
AI-Scholar-Hunt/
│
├── 📁 auth/                        # Authentication blueprint
│   ├── __init__.py
│   └── routes.py                   # /login, /signup, /forgot-password, /reset-password
│
├── 📁 blueprints/                  # Feature blueprints
│   └── cv.py                       # Multi-country CV builder (14 countries, PDF+DOCX)
│
├── 📁 cv_templates/                # Country-specific CV generation logic
│   ├── usa.py                      # ATS-friendly (USA, Canada, Australia, Ireland)
│   ├── germany.py                  # Photo + Personal Details (Germany, Austria, Turkey)
│   ├── uae.py                      # Passport/Visa format (UAE, China, Japan)
│   └── china.py                    # CSC format
│
├── 📁 scholarships/                # 📚 RAG Knowledge Base
│   └── *.txt                       # 51+ scholarship files in JSON format
│
├── 📁 user_profile/                # Profile management blueprints
│   ├── routes.py                   # /profile, /edit-profile
│   ├── preferences.py              # Theme, language preferences
│   └── security.py                 # Password change
│
├── 📁 templates/                   # Jinja2 HTML templates
│   ├── index.html                  # Landing page
│   ├── dashboard.html              # User dashboard
│   ├── chat.html                   # AI Chatbot UI
│   ├── cv-builder.html             # CV Builder country selection
│   ├── cv_form.html                # CV form (per country)
│   ├── ats.html                    # ATS CV Checker
│   ├── essay.html                  # Essay Writing Assistant
│   ├── eligibility.html            # Eligibility Checker
│   ├── search.html                 # Scholarship Search
│   ├── scholarships.html           # Scholarship listing
│   ├── profile.html                # User profile view
│   ├── edit_profile.html           # Edit profile
│   ├── login.html                  # Login page
│   ├── signup.html                 # Signup page
│   ├── 404.html                    # Error pages
│   └── 500.html
│
├── 📁 static/                      # CSS, JS, images, fonts
│
├── 🚀 app.py                       # Main Flask application entry point
├── 🤖 chatbot.py                   # RAG engine — load, search, respond
├── 🗄️ models.py                    # SQLAlchemy User model
├── ⚙️ config.py                    # App configuration (DB, Mail, Secret)
├── 📧 email_service.py             # Email sending with SMTP fallback
├── 📦 requirements.txt             # Python dependencies
└── 📖 README.md
```

---

## ⚙️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core backend language |
| **Web Framework** | Flask 2.3 | Routes, blueprints, request handling |
| **ORM** | SQLAlchemy | Database models and queries |
| **Database** | SQLite | Lightweight local database |
| **Authentication** | Flask-Login + itsdangerous | Session management + secure tokens |
| **Email** | Flask-Mail + smtplib | Password reset, notifications |
| **PDF Generation** | ReportLab | Country-specific CV PDF export |
| **DOCX Generation** | python-docx | CV Word document export |
| **Image Processing** | Pillow (PIL) | CV photo resizing and embedding |
| **AI Engine** | Custom LLM + RAG | Scholarship retrieval and response |
| **Prompt Engineering** | Custom templates | Structured AI response generation |
| **Frontend** | HTML5, CSS3, JS, Jinja2 | UI templates and interactions |
| **CORS** | Flask-CORS | Cross-origin request handling |
| **Security** | itsdangerous | Token-based password reset |

</div>

---

## 🔐 Authentication System

```
User Flow:
──────────────────────────────────────────────────────
  /signup     →  Register with name, email, password
  /login      →  Authenticate → Flask-Login session
  /dashboard  →  Protected route (login required)
  /logout     →  Clear session → redirect to home

Password Reset Flow:
──────────────────────────────────────────────────────
  /forgot-password  →  Enter email
       │
       ▼
  Generate secure token (itsdangerous, 1hr expiry)
       │
       ▼
  Send reset email (Flask-Mail → SMTP fallback)
       │
       ▼
  /reset-password/<token>  →  Set new password
       │
       ▼
  Token verified → Password updated → Login
```

---

## 🌍 CV Builder — Multi-Country Support

| Group | Countries | Format | Photo | Special Fields |
|---|---|---|---|---|
| **A** | USA 🇺🇸 Canada 🇨🇦 Australia 🇦🇺 Ireland 🇮🇪 | ATS-Friendly | ❌ | LinkedIn, GitHub |
| **B** | Germany 🇩🇪 Austria 🇦🇹 Turkey 🇹🇷 | Lebenslauf | ✅ | DOB, Nationality, Marital Status |
| **C** | China 🇨🇳 UAE 🇦🇪 Japan 🇯🇵 | Passport/Visa | ✅ | Passport No, Visa Status |
| **D** | Belgium 🇧🇪 Denmark 🇩🇰 Italy 🇮🇹 France 🇫🇷 | Europass | ❌ | Languages (very important) |

**Sections generated:** Personal Info → Education → Work Experience → Projects → Skills → Languages → Certifications → Publications

**Export formats:** `.pdf` (ReportLab) and `.docx` (python-docx)

---

## 📊 Scholarship Knowledge Base

```
Total Scholarships : 51+
Countries Covered  : 20+
Formats            : JSON-structured .txt files
Fields per entry   : 15+ (name, country, institution, level,
                     deadline, coverage, eligibility, documents,
                     courses, duration, links, notes...)

Sample Scholarships:
  🇩🇪  DAAD Scholarship 2026-2027
  🇺🇸  Fulbright Scholarship 2026-2027
  🇦🇺  Australia Awards Scholarships 2026-2027
  🇨🇳  Beijing Government Scholarship 2026-2027
  🇨🇦  Carleton University Entrance Awards
  🇰🇷  Harvard Academy Scholars Program
  🇦🇪  Khalifa University Scholarship (Fully Funded)
  🇮🇹  University of Bologna Scholarship
  🇧🇪  Master Mind Scholarships Belgium
       ... and 42 more
```

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/ai-scholar-hunt.git
cd ai-scholar-hunt
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure the App
```bash
# Edit config.py with your settings (see next section)
```

### 5️⃣ Run the Application
```bash
python app.py
```

### 6️⃣ Open in Browser
```
http://127.0.0.1:5000
```

---

## 📁 Environment Configuration

Edit `config.py` with your values:

```python
class Config:
    # Security
    SECRET_KEY = 'your-strong-secret-key-here'

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///scholar.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (Gmail SMTP)
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = 'your-email@gmail.com'
    MAIL_PASSWORD = 'your-gmail-app-password'   # Gmail App Password
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'

    # Upload limit
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16MB
```

> 💡 For Gmail, generate an **App Password** from Google Account → Security → 2-Step Verification → App Passwords

---

## 🧩 Blueprint Architecture

```
app.py  (Main Flask App)
│
├── auth_bp          →  /login, /signup, /logout, /forgot-password
├── profile_bp       →  /profile, /edit-profile
├── preferences_bp   →  /preferences
├── security_bp      →  /security (change password)
└── cv_bp            →  /cv-builder/, /cv-builder/cv_form/<country>
                         /cv-builder/generate_cv
```

Each blueprint is registered once in `app.py` after `app = Flask(__name__)` is created — ensuring no duplicate route conflicts.

---

## 📦 Requirements

```txt
Flask==2.3.0
Flask-Login
Flask-Mail
Flask-CORS
Flask-SQLAlchemy
itsdangerous
python-docx==0.8.11
reportlab==4.0.4
Pillow==10.0.0
```

---

## 👨‍💻 Authors

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&pause=1000&color=0EA5E9&width=500&lines=Final+Year+Project+2026;Department+of+Artificial+Intelligence;Built+with+❤️+by+the+team" alt="Authors"/>

<br/>

### 🧑‍💻 Asad Aziz

[![GitHub](https://img.shields.io/badge/GitHub-asadaziz-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Asad-Aziz-001)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-asadaziz-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/asad-aziz-ai)


<br/>

### 🧑‍💻 Tayyab Zunair

[![GitHub](https://img.shields.io/badge/GitHub-tayyabzunair-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Tayyabzunair)
[![LinkedIn](https://img.shields.io/badge/-tayyabzunair-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mtayyabzunair)

[![Email](https://img.shields.io/badge/Email-aischolarhunt@gmail.com-0EA5E9?style=for-the-badge&logo=gmail&logoColor=white)](mailto:aischolarhunt@gmail.com)

<br/>

---

### 🎓 Project Details

| Field | Detail |
|---|---|
| **Project Type** | Final Year Project (FYP) |
| **Year** | 2026 |
| **Domain** | Gen AI |
| **Focus** | EdTech — Scholarship Discovery for Pakistani Students |
| **AI Techniques** | LLM · RAG · Prompt Engineering |
| **External API** | ❌ None Required |

</div>

---

<div align="center">

<br/>

*"Empowering Pakistani students with AI-guided scholarship access — one query at a time."*

<br/>

<img src="https://img.shields.io/badge/⭐_Star_this_repo_if_it_helped_you!-0EA5E9?style=for-the-badge"/>

<br/><br/>

<img src="https://img.shields.io/badge/Made_with-❤️_in_Pakistan_🇵🇰-14B8A6?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge"/>

</div>
