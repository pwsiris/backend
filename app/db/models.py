from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.types import BIGINT, TIMESTAMP

SCHEMA = "pwsi"
Base = declarative_base(metadata=MetaData(schema=SCHEMA))


class TwitchBotLists(Base):
    __tablename__ = "twitchbot_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)


class TwitchBotCounters(Base):
    __tablename__ = "twitchbot_counters"

    name: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(nullable=False)
    updated: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))


class Socials(Base):
    __tablename__ = "socials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str]
    order: Mapped[int] = mapped_column(nullable=False)


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str]
    type: Mapped[str]
    episodes: Mapped[int]
    picture: Mapped[str]
    score: Mapped[int]
    status: Mapped[str]
    added_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    completed_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    comment: Mapped[str]
    voice_acting: Mapped[str]
    order_by: Mapped[str]
    series: Mapped[str]


class Challenges(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    picture: Mapped[str]
    order_by: Mapped[str]
    description: Mapped[str]
    comment: Mapped[str]
    status: Mapped[str]
    type: Mapped[str]
    price: Mapped[str]
    records: Mapped[str]


class Games(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    subname: Mapped[str]
    link: Mapped[str]
    picture: Mapped[str]
    status: Mapped[str]
    genre: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str]
    records: Mapped[str]
    comment: Mapped[str]
    order_by: Mapped[str]
