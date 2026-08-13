from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class City(Base):
    __tablename__ = "cities"

    city_id: Mapped[int] = mapped_column(primary_key=True,
                                         autoincrement=True)

    name: Mapped[str] = mapped_column("name",
                                      String(200),
                                      nullable=False)
    state: Mapped[str] = mapped_column("state",
                                       String(2),
                                       nullable=False)
    latitude: Mapped[Optional[Decimal]] = mapped_column(
                                    Numeric(precision=7, scale=4),
                                    nullable=True,
                                    default=None)
    longitude: Mapped[Optional[Decimal]] = mapped_column(
                                    Numeric(precision=7, scale=4),
                                    nullable=True,
                                    default=None)
    created_by: Mapped[str] = mapped_column(String(200),
                                            nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)
