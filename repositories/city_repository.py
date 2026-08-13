from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.city import City

SessionFactory = Callable[[], Session]


class CityRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def _session(self) -> Session:
        return self._session_factory()

    def list_cities(self) -> list[City]:
        with self._session() as session:
            return list(session.scalars(select(City)
                                        .order_by(City.name.desc())
                                        ).all())

    def get_city(self, city_id: int) -> Optional[City]:
        with self._session() as session:
            return session.get(City, city_id)

    def create_city(self, city: City) -> City:
        with self._session() as session:
            session.add(city)
            session.commit()
            session.refresh(city)
            return city

    def delete_city(self, city_id: int) -> bool:
        with self._session() as session:
            message = session.get(City, city_id)
            if message is None:
                return False
            session.delete(message)
            session.commit()
            return True
