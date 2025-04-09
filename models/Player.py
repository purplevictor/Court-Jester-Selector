from typing import Optional, List

from sqlmodel import SQLModel, BigInteger, CheckConstraint, Column, UniqueConstraint, Field, Relationship

from config import MAX_WEIGHT, DEFAULT_WEIGHT

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    group_id: int = Field(foreign_key="group.id")
    telegram_id: int = Field(sa_column=Column(BigInteger))

    weight: int = Field(default=DEFAULT_WEIGHT, ge=1, le=MAX_WEIGHT)

    group: "Group" = Relationship(back_populates="players")
    draws: List["Draw"] = Relationship(back_populates="player")
    
    __table_args__ = (
        UniqueConstraint("group_id", "telegram_id", name="uix_group_telegram_id"),
        CheckConstraint(f"weight >= 1 AND weight <= {MAX_WEIGHT}", name="ck_weight_bounds"),
    )