from sqlalchemy import Column, Integer, String, DateTime, Text, func, Boolean
from database import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class Board(Base):
    __tablename__ = 'board'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    modification_data = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), nullable=False) # ARCHIVED/OPEN


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    modification_data = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Boolean, nullable=False)
    text = Column(Text, nullable=False)
    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)

    board = relationship('board', backref=backref('task', lazy=True))