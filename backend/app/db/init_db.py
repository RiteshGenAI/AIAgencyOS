import logging

from sqlalchemy import text

from backend.app.db.session import Base, engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
