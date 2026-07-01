from sqlalchemy.orm import Session
from database.models import Conversation, Message

MAX_HISTORY_TURNS = 12  # keep last N messages as context sent to the model


def get_or_create_conversation(db: Session, session_id: str) -> Conversation:
    convo = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .first()
    )
    if convo:
        return convo
    convo = Conversation(session_id=session_id)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


def add_message(db: Session, conversation_id: str, role: str, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_history_for_model(db: Session, conversation_id: str) -> list:
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    recent = msgs[-MAX_HISTORY_TURNS:]
    return [{"role": m.role, "content": m.content} for m in recent]
