from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str
    mode: Optional[str] = "Standard"

class ConversationCreate(ConversationBase):
    pass

class ConversationOut(ConversationBase):
    id: int
    user_id: int
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True
