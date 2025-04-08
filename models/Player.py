from typing import Optional, List

from sqlmodel import SQLModel, BigInteger, Column, Field, Relationship

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    group_id: int = Field(foreign_key="group.id")
    telegram_id: int = Field(sa_column=Column(BigInteger))

    group: "Group" = Relationship(back_populates="players")
    draws: List["Draw"] = Relationship(back_populates="player")