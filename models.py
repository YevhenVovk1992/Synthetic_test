import enum as lib_enum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, func, Boolean, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import expression

from database import Base


class BoardStatus(lib_enum.Enum):
    ARCHIVED = 'ARCHIVED'
    OPEN = 'OPEN'


class Board(Base):
    __tablename__ = 'board'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    modification_data = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Enum(BoardStatus))  # ARCHIVED/OPEN

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'creation_date': self.creation_date,
            'modification_data': self.modification_data,
            'status': self.status.value
        }


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, nullable=False)
    creation_date = Column(DateTime(), server_default=func.now())
    modification_data = Column(DateTime(), nullable=True, onupdate=func.now())
    status = Column(Boolean, server_default='f', default=False)
    text = Column(Text, nullable=False)
    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)

    board = relationship('Board', backref=backref('task', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'creation_date': self.creation_date,
            'modification_data': self.modification_data,
            'status': self.status,
            'text': self.text,
            'board_id': self.board_id
        }