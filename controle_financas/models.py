from datetime import date
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from controle_financas.database import db


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = 'records'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_date: Mapped[Optional[date]] = mapped_column(default=date.today())
    value: Mapped[float]


Base.metadata.create_all(db)
