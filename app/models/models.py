import uuid

from datetime import datetime
from sqlalchemy import (
    String,
    UUID,
    func,
    DateTime,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )


class BankruptcyStatementModel(BaseModel):
    """Объект Сведений о банкротстве"""

    __tablename__ = "bankruptcy_statement"

    inn: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    case_number: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    case_date_last: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_bankruptcy_statement_inn", inn),
        Index("ix_bankruptcy_statement_case_number", case_number),
    )


class ElectronicCaseModel(BaseModel):
    """Объект Электронных документов по делу о банкротстве"""

    __tablename__ = "electronic_case"

    case_number: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    document_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    document_date_last: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=True,
    )

    __table_args__ = (Index("ix_electronic_case_case_number", case_number),)
