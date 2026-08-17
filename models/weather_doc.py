from datetime import datetime
import enum

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WeatherSourceType(str, enum.Enum):
    FORECAST = "forecast"
    ALERT = "alert"


class WeatherDoc(Base):
    __tablename__ = "weather_docs"

    weather_id: Mapped[str] = mapped_column(Text,
                                            primary_key=True)
    location: Mapped[str] = mapped_column(String(100),
                                          nullable=False)
    source_type: Mapped[str] = mapped_column(
                                    String(30),
                                    nullable=False,
                                    default=WeatherSourceType.FORECAST.value)
    headline: Mapped[str] = mapped_column(Text)
    narrative_text: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False)
    payload: Mapped[str] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                server_default=func.now(),
                                                nullable=False)
