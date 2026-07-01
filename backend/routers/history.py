from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Conversation, Message, Feedback
from schemas import HistoryResponse, FeedbackRequest

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_history(session_id: str, db: Session = Depends(get_db)):
    convo = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .first()
    )
    if not convo:
        return HistoryResponse(session_id=session_id, messages=[])

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == convo.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return HistoryResponse(session_id=session_id, messages=messages)


@router.delete("/history")
async def delete_history(session_id: str, db: Session = Depends(get_db)):
    convos = db.query(Conversation).filter(Conversation.session_id == session_id).all()
    if not convos:
        raise HTTPException(status_code=404, detail="No history found for this session")

    for convo in convos:
        db.query(Message).filter(Message.conversation_id == convo.id).delete()
        db.delete(convo)
    db.commit()
    return {"success": True, "message": "History cleared"}


@router.post("/feedback")
async def submit_feedback(body: FeedbackRequest, db: Session = Depends(get_db)):
    fb = Feedback(
        conversation_id=body.conversation_id,
        message_id=body.message_id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(fb)
    db.commit()
    return {"success": True}
