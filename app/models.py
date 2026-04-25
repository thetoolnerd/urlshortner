import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from .db import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code = Column(String(16), unique=True, index=True, nullable=False)
    long_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_custom = Column(Boolean, nullable=False, default=False)
    redirect_status_code = Column(Integer, nullable=False, default=302)
    click_count = Column(Integer, nullable=False, default=0)
