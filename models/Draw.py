from typing import Optional
from datetime import date

from sqlmodel import SQLModel, UniqueConstraint, Field, Relationship

class Draw(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draw_date: date = Field(default_factory=date.today)
    group_id: int = Field(foreign_key="group.id")
    player_id: int = Field(foreign_key="player.id")

    group: "Group" = Relationship(back_populates="draws")
    player: "Player" = Relationship(back_populates="draws")
    
    __table_args__ = (
        UniqueConstraint('group_id', 'draw_date', name='uix_group_date'),
    )