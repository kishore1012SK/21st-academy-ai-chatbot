from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from limiter import limiter

from database.db import get_db
from schemas import ChatRequest, ChatResponse
from services import ollama_service, rag_service, memory_service
from config import settings

router = APIRouter()


@router.post("/chat", response_model=None)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def chat(request: Request, body: ChatRequest, db: Session = Depends(get_db)):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    convo = memory_service.get_or_create_conversation(db, body.session_id)
    memory_service.add_message(db, convo.id, "user", body.message)
    history = memory_service.get_history_for_model(db, convo.id)[:-1]  # exclude the message we just added

    # Fetch courses and workshop details dynamically
    from database.models import Course, WorkshopInfo
    courses = db.query(Course).all()
    workshop = db.query(WorkshopInfo).first()
    
    # Format them as structured context
    dynamic_context_parts = []
    if workshop:
        dynamic_context_parts.append(
            f"WORKSHOP DETAILS:\n"
            f"- Date: {workshop.date}\n"
            f"- Time: {workshop.time}\n"
            f"- Venue: {workshop.venue}\n"
            f"- Registration Process: {workshop.registration_process}\n"
            f"- Eligibility: {workshop.eligibility}\n"
            f"- Contact Number: {workshop.contact_number}\n"
            f"- WhatsApp Number: {workshop.whatsapp_number}\n"
            f"- Email: {workshop.email}\n"
            f"- Google Maps Location: {workshop.google_maps_location}\n"
            f"- Website: {workshop.website}\n"
        )
    else:
        # Fallback default workshop
        dynamic_context_parts.append(
            f"WORKSHOP DETAILS:\n"
            f"- Date: 27th June 2026\n"
            f"- Time: 9:30 AM (reporting time)\n"
            f"- Venue: Poonamalle, Chennai\n"
            f"- Contact Number: +91 99 44 74 7090\n"
            f"- Email: admin@21stacademy.in\n"
            f"- Website: https://21stacademy.in\n"
        )
    
    if courses:
        dynamic_context_parts.append("AVAILABLE ACADEMY COURSES:")
        for idx, course in enumerate(courses, 1):
            dynamic_context_parts.append(
                f"{idx}. Course Name: {course.name}\n"
                f"   - Description: {course.description}\n"
                f"   - Duration: {course.duration}\n"
                f"   - Fees: {course.fees}\n"
                f"   - Eligibility: {course.eligibility}\n"
                f"   - Prerequisites: {course.prerequisites}\n"
                f"   - Learning Roadmap: {course.learning_roadmap}\n"
                f"   - Modules: {course.modules}\n"
                f"   - Topics Covered: {course.topics_covered}\n"
                f"   - Projects Included: {course.projects_included}\n"
                f"   - Internship Details: {course.internship_details}\n"
                f"   - Certification: {course.certification}\n"
                f"   - Placement Support: {course.placement_support}\n"
                f"   - Career Opportunities: {course.career_opportunities}\n"
                f"   - Expected Salary: {course.expected_salary}\n"
                f"   - Tools Used: {course.tools_used}\n"
                f"   - Software Required: {course.software_required}\n"
                f"   - Industry Applications: {course.industry_applications}\n"
                f"   - FAQs: {course.faqs}\n"
            )
            
    # Also fetch RAG context from files
    try:
        context_chunks = await rag_service.search_similar_chunks(body.message, db)
        if context_chunks:
            dynamic_context_parts.append("RELEVANT REFERENCE MATERIAL (from uploaded files):\n" + "\n\n---\n\n".join(context_chunks))
    except Exception:
        pass
        
    context = "\n\n======================\n\n".join(dynamic_context_parts)

    if body.stream:
        async def token_stream():
            full_reply = []
            try:
                async for token in ollama_service.chat_completion_stream(history, body.message, context):
                    full_reply.append(token)
                    yield token
            finally:
                if full_reply:
                    memory_service.add_message(db, convo.id, "assistant", "".join(full_reply))

        return StreamingResponse(token_stream(), media_type="text/plain")

    try:
        reply = await ollama_service.chat_completion(history, body.message, context)
    except ollama_service.OllamaError:
        raise HTTPException(
            status_code=503,
            detail="The AI model is currently unreachable. Please try again shortly.",
        )

    if not reply:
        reply = "I'm having trouble responding right now. Please contact us at admin@21stacademy.in."

    memory_service.add_message(db, convo.id, "assistant", reply)

    return ChatResponse(success=True, response=reply, conversation_id=convo.id)
