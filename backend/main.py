from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from limiter import limiter
from database.db import init_db, SessionLocal
from database.models import User
from auth_utils import hash_password
from services.ollama_service import check_health
from routers import chat, auth, upload, history, courses, workshop


def bootstrap_admin():
    """Creates the default admin account on first run only, from .env values."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.is_admin.is_(True)).first()
        if not existing:
            admin = User(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def bootstrap_courses():
    """Bootstraps initial course records if the database is empty."""
    db = SessionLocal()
    try:
        from database.models import Course
        if db.query(Course).count() == 0:
            default_courses = [
                Course(
                    name="AI Engineering",
                    description="Comprehensive program covering Machine Learning, Deep Learning, Generative AI, and Agentic AI workflow automation.",
                    duration="6 Months",
                    fees="Rs. 45,000",
                    eligibility="Graduates or Students with basic programming knowledge.",
                    prerequisites="Basic Python programming.",
                    learning_roadmap="Python -> Machine Learning -> Deep Learning -> Generative AI -> AI Agents.",
                    modules="Module 1: Advanced Python; Module 2: ML Fundamentals; Module 3: Neural Networks; Module 4: LLMs & RAG; Module 5: Agentic Frameworks.",
                    topics_covered="Python, NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch, LangChain, Autogen, CrewAI.",
                    projects_included="Customer Churn Predictor, AI Voice Assistant, Automated Multi-Agent Dev Team.",
                    internship_details="2 Months paid internship with 21st Academy partners.",
                    certification="Certified AI Engineer by 21st Academy.",
                    placement_support="100% placement assistance & mock interviews.",
                    career_opportunities="AI Engineer, ML Engineer, NLP Specialist, Generative AI Developer.",
                    expected_salary="Rs. 6 - 15 LPA",
                    tools_used="VS Code, Jupyter, GitHub, Ollama, Hugging Face.",
                    software_required="Python 3.10+, Git.",
                    industry_applications="Autonomous systems, health tech diagnostics, automated customer service.",
                    faqs="Q: Can a non-coder join?\nA: Yes, Python is covered from scratch."
                ),
                Course(
                    name="Full Stack Development",
                    description="Master modern front-end and back-end web development tools to build scalable, database-driven web applications.",
                    duration="6 Months",
                    fees="Rs. 38,000",
                    eligibility="Open to all backgrounds.",
                    prerequisites="None, starts from basics.",
                    learning_roadmap="HTML/CSS -> JavaScript -> React -> Node.js & Express -> SQL & MongoDB -> Deployment.",
                    modules="Module 1: Frontend Basics; Module 2: React JS; Module 3: Backend Node.js; Module 4: Databases SQL/NoSQL; Module 5: DevOps & Cloud.",
                    topics_covered="HTML5, CSS3, JavaScript, React, Node.js, Express, PostgreSQL, MongoDB, Git, Docker.",
                    projects_included="E-commerce Marketplace, Real-time Collaborative Chat, Dev Portfolio.",
                    internship_details="3 Months hands-on internship with real project exposure.",
                    certification="Full Stack Developer Certification by 21st Academy.",
                    placement_support="Guaranteed interview schedules.",
                    career_opportunities="Full Stack Developer, Frontend Engineer, Backend Developer.",
                    expected_salary="Rs. 4.5 - 12 LPA",
                    tools_used="Git, GitHub, NPM, Postman, MongoDB Compass.",
                    software_required="NodeJS, VS Code.",
                    industry_applications="SaaS applications, corporate websites, e-commerce.",
                    faqs="Q: Is placement support included?\nA: Yes, all graduates receive mock interview training and direct placement drives."
                )
            ]
            db.add_all(default_courses)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bootstrap_admin()
    bootstrap_courses()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Self-hosted AI chatbot backend for 21st Academy — powered entirely by a local Ollama/Llama3 model. No third-party AI provider is ever contacted.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS: allow PUT and DELETE for Admin actions ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# --- Routers ---
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(courses.router, prefix="/api", tags=["courses"])
app.include_router(workshop.router, prefix="/api", tags=["workshop"])


@app.get("/")
async def root():
    return {"success": True, "message": f"{settings.APP_NAME} backend is running."}


@app.get("/health")
async def health():
    ollama_ok = await check_health()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama_reachable": ollama_ok,
        "model": settings.OLLAMA_CHAT_MODEL,
    }
