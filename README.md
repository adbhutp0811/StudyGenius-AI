# StudyGenius AI

A production-ready full-stack AI Learning & Career Platform built with React.js, Django REST Framework, PostgreSQL, Tailwind CSS, JWT Authentication, and Google Gemini API.

## Features

### 1. AI Resume Builder
- Create professional resumes with multiple templates
- AI-generated professional summaries, skill suggestions, and experience enhancement
- ATS score analysis and PDF export

### 2. AI Roadmap Generator
- Personalized learning roadmaps based on career goals
- Milestone tracking with progress dashboard
- Resource recommendations and daily study planner

### 3. AI Doubt Solver
- ChatGPT-like chat interface for subject-wise doubt solving
- Code explanation support and image-based doubt solving
- Chat history with bookmarking

### 4. AI Blog Writer
- Generate blog articles from keywords with multiple tones
- SEO optimization suggestions and grammar correction
- Export as Markdown, PDF, and HTML

### 5. AI YouTube Video Summarizer
- Extract YouTube video transcripts and generate summaries
- Key points extraction, notes generation, and quiz creation

### 6. AI PDF Chat Assistant
- Upload and chat with PDF documents
- AI answers based on document content with relevant section highlighting
- Multi-PDF chat support

### 7. AI Career Guidance Platform
- Skill assessment tests with career recommendations
- Industry trend analysis and salary insights
- Career path, internship, and project suggestions

### 8. AI Question Paper Generator
- Generate MCQs, short-answer, and long-answer questions
- Multiple difficulty levels (Easy, Medium, Hard)
- Export as PDF

## Tech Stack

### Backend
- **Framework:** Django 4.2 + Django REST Framework 3.15
- **Database:** PostgreSQL
- **Authentication:** JWT (SimpleJWT)
- **AI:** Google Gemini API, LangChain
- **PDF:** PyPDF2, pdfplumber, ReportLab
- **Docs:** drf-spectacular (Swagger/OpenAPI)

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS 3 with dark mode
- **Charts:** Recharts
- **State:** Zustand + Context API
- **API Client:** Axios with JWT interceptor
- **Notifications:** react-hot-toast

## Project Structure

```
StudyGenius-AI/
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/           # User auth & profiles
│   │   ├── resumes/            # Resume builder
│   │   ├── roadmaps/           # Roadmap generator
│   │   ├── doubts/             # Doubt solver
│   │   ├── blogs/              # Blog writer
│   │   ├── youtube/            # YouTube summarizer
│   │   ├── pdfchat/            # PDF chat assistant
│   │   ├── career/             # Career guidance
│   │   ├── questionpapers/     # Question paper generator
│   │   └── notifications/      # Notifications & activity
│   ├── ai_services/            # AI integration layer
│   │   ├── gemini_service.py
│   │   ├── resume_analyzer.py
│   │   ├── roadmap_generator.py
│   │   ├── youtube_service.py
│   │   ├── pdf_service.py
│   │   ├── career_service.py
│   │   └── pdf_generator.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   └── layout/         # Layout, Sidebar, Header
│   │   ├── context/            # Auth & Theme context
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client
│   │   └── utils/              # Helpers & constants
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Groq API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and API keys

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=study_genius_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=your-groq-api-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | Login (returns JWT) |
| POST | `/api/auth/logout/` | Logout (blacklists token) |
| GET | `/api/auth/me/` | Current user details |
| GET/PATCH | `/api/auth/profile/` | User profile |
| POST | `/api/auth/change-password/` | Change password |
| POST | `/api/auth/forgot-password/` | Request password reset |
| POST | `/api/auth/reset-password/` | Reset password |
| POST | `/api/auth/token-refresh/` | Refresh JWT token |

### Module Endpoints

**Resumes:** `/api/resumes/` - CRUD + generate_summary, suggest_skills, analyze_score, export_pdf

**Roadmaps:** `/api/roadmaps/` - CRUD + generate, update_progress, generate_daily_plan

**Doubts:** `/api/doubts/` - CRUD + ask, ask_with_image, bookmark

**Blogs:** `/api/blogs/` - CRUD + generate, optimize_seo, grammar_check, publish, export

**YouTube:** `/api/youtube/` - CRUD + summarize, generate_quiz

**PDF Chat:** `/api/pdfchat/documents/`, `/api/pdfchat/sessions/` - Upload, chat, search, highlight

**Career:** `/api/career/assessments/`, `/api/career/recommendations/`, `/api/career/trends/`, `/api/career/salaries/`

**Question Papers:** `/api/question-papers/papers/` - CRUD + generate, export_pdf

**Notifications:** `/api/notifications/` - CRUD + mark_read, unread_count

## Deployment

### Docker (Recommended)

```bash
# Build and run all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### Traditional Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Collect static files: `python manage.py collectstatic`
4. Install Gunicorn: `pip install gunicorn`
5. Run: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`
6. Build frontend: `cd frontend && npm run build`
7. Serve frontend with Nginx

## Database Schema

Core models:
- **User** (custom, email-based auth)
- **Profile** (user details, skills, preferences)
- **Resume** + ResumeTemplate + ResumeAnalysis
- **Roadmap** + Milestone + DailyPlan + Resource
- **ChatSession** + ChatMessage + BookmarkedAnswer
- **Blog** + BlogVersion + SEOSuggestion
- **VideoSummary** + SavedNote
- **PDFDocument** + PDFChatSession + PDFChatMessage + DocumentHighlight
- **SkillAssessment** + CareerRecommendation + IndustryTrend + SalaryInsight
- **QuestionPaper** + QuestionBank + Subject
- **Notification** + NotificationPreference + ActivityLog

## License

MIT
