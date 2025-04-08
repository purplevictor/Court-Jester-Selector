from typing import Optional, List

from sqlmodel import SQLModel, BigInteger, Column, Field, Relationship

class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    telegram_id: int = Field(sa_column=Column(BigInteger))

    players: List["Player"] = Relationship(back_populates="group")
    draws: List["Draw"] = Relationship(back_populates="group")

    class Config:
        arbitrary_types_allowed = True