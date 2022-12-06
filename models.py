import enum as lib_enum

from sqlalchemy import Column, Integer, String, DateTime, Text, func, Boolean, Enum
from database import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class BoardStatus(lib_enum.Enum):
    ARCHIVED = 'ARCHIVED'
    OPEN = 'OPEN'


class Board(Base):
    __tablename__ = 'board'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    modification_data = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Enum(BoardStatus))  # ARCHIVED/OPEN

    def to_dict(self):
        return {
            'id': self.id,
            'creation_date': self.creation_date,
            'modification_data': self.modification_data,
            'status': self.status.value
        }


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    modification_data = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Boolean, nullable=False)
    text = Column(Text, nullable=False)
    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)

    board = relationship('Board', backref=backref('task', lazy=True))
