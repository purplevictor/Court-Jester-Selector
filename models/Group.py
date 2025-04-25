from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from sqlmodel import (
    BigInteger,
    Column,
    Field,
    JSON,
    Relationship,
    SQLModel,
)

class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    telegram_id: int = Field(sa_column=Column(BigInteger, unique=True, index=True))
    telegram_title: str = Field(index=True)

    approved: bool = Field(default=False)

    approval_messages: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))

    players: List["Player"] = Relationship(back_populates="group")
    draws: List["Draw"] = Relationship(back_populates="group")

    @property
    def added(self) -> str:
        return f"Group {self.telegram_title} (id: {self.id}, telegram_id: {self.telegram_id}) added with {self.status} status."
    
    @property
    def updated(self) -> str:
        return f"Group {self.telegram_title} (id: {self.id}, telegram_id: {self.telegram_id}) updated with {self.status} status."