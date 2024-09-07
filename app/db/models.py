from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.types import BIGINT, JSON, TIMESTAMP, Text

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
    updated: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class Socials(Base):
    __tablename__ = "socials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)
    episodes: Mapped[int] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    score: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    added_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    completed_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    comment: Mapped[str] = mapped_column(nullable=True)
    voice_acting: Mapped[str] = mapped_column(nullable=True)
    order_by: Mapped[str] = mapped_column(nullable=True)
    series: Mapped[str] = mapped_column(nullable=True)


class Challenges(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    picture: Mapped[str] = mapped_column(nullable=True)
    order_by: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[str] = mapped_column(nullable=True)
    records: Mapped[str] = mapped_column(nullable=True)


class Games(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    subname: Mapped[str] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    genre: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=True)
    records: Mapped[list[dict[str, str | int]]] = mapped_column(JSON, nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    gift_by: Mapped[str] = mapped_column(nullable=True)
    order_by: Mapped[str] = mapped_column(nullable=True)


class Lore(Base):
    __tablename__ = "lore"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    block_id: Mapped[str] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)


class Marathons(Base):
    __tablename__ = "marathons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    records: Mapped[str] = mapped_column(nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=True)
    marathon_id: Mapped[int] = mapped_column(nullable=True)
    steam_id: Mapped[int] = mapped_column(nullable=True)


class RouletteAwards(Base):
    __tablename__ = "roulette_awards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    rarity: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)


class Merch(Base):
    __tablename__ = "merch"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    creator_name: Mapped[str] = mapped_column(nullable=True)
    creator_link: Mapped[str] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    picture_size: Mapped[str] = mapped_column(nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)
