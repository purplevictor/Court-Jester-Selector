from typing import (
    List,
    Optional,
)

from sqlmodel import (
    BigInteger,
    CheckConstraint,
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)

from config import (
    DEFAULT_WEIGHT,
    MAX_WEIGHT,
    MIN_WEIGHT,
)

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    group_id: int = Field(foreign_key="group.id")
    telegram_id: int = Field(sa_column=Column(BigInteger, index=True))
    telegram_first_name: str = Field(index=True)
    telegram_last_name: Optional[str] = None
    telegram_username: Optional[str] = Field(default=None, index=True)

    weight: int = Field(default=DEFAULT_WEIGHT, ge=MIN_WEIGHT, le=MAX_WEIGHT)

    group: "Group" = Relationship(back_populates="players")
    draws: List["Draw"] = Relationship(back_populates="player")
    
    __table_args__ = (
        UniqueConstraint("group_id", "telegram_id", name="uix_group_telegram_id"),
        CheckConstraint(f"weight >= {str(MIN_WEIGHT)} AND weight <= {str(MAX_WEIGHT)}", name="ck_weight_bounds"),
    )

    def display_name(self, without_at=False) -> str:
        return f"{'' if without_at or not self.telegram_username else '@'}{self.telegram_username if self.telegram_username else (self.telegram_first_name + ' ' + self.telegram_last_name) if self.telegram_last_name else self.telegram_first_name}"
    
    @property
    def added(self) -> str:
        return f"Player {self.display_name} (id: {self.id}, telegram_id: {self.telegram_id}) added to Group {self.group.telegram_title} (id: {self.group.id}, telegram_id: {self.group.telegram_id}) with {self.status} status."
    
    @property
    def updated(self) -> str:
        return f"Player {self.display_name} (id: {self.id}, telegram_id: {self.telegram_id}) from Group {self.group.telegram_title} (id: {self.group.id}, telegram_id: {self.group.telegram_id}) updated with {self.status} status."