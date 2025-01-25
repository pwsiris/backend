from crud.anime import AnimeData
from crud.auctions import AuctionsData
from crud.challenges import ChallengesData
from crud.credits import CreditsData
from crud.games import GamesData
from crud.lore import LoreData
from crud.marathons import MarathonsData
from crud.merch import MerchData
from crud.roulette import RouletteData
from crud.socials import SocialsData
from crud.twitchbot_counters import TwitchBotCounter
from crud.twitchbot_lists import TwitchBotList
from sqlalchemy.ext.asyncio import AsyncSession


class AllData:
    def __init__(self) -> None:
        self.TIMECODE_MESSAGE = "Saved"

        self.SITE_MESSAGES_ENABLED = False
        self.SITE_MESSAGES_TITLE_TEXT = ""
        self.SITE_MESSAGES_TITLE_EDITABLE = False

        self.SAVE_CHOICES = TwitchBotList("save_choices")

        self.BITE_CHEAT_STREAMER_PERCENT = 0
        self.BITE_CHEAT_DEFENSE_PERCENT = 0

        self.BITE_IGNORE_LIST = TwitchBotList("bite_ignore_list")
        self.BITE_ACTIONS = TwitchBotList("bite_actions")
        self.BITE_PLACES = TwitchBotList("bite_places")
        self.BITE_BODY_PARTS = TwitchBotList("bite_body_parts")

        self.COUNTER = TwitchBotCounter("count")
        self.COUNTER_DEATH = TwitchBotCounter("death")
        self.COUNTER_GLOBAL = TwitchBotCounter("global")

        self.ANIME = AnimeData()
        self.AUCTIONS = AuctionsData()
        self.CHALLENGES = ChallengesData()
        self.CREDITS = CreditsData()
        self.GAMES = GamesData()
        self.LORE = LoreData()
        self.MARATHONS = MarathonsData()
        self.MERCH = MerchData()
        self.ROULETTE = RouletteData()
        self.SOCIALS = SocialsData()

    async def setup(self, session: AsyncSession) -> None:
        await self.SAVE_CHOICES.setup(session)

        await self.BITE_IGNORE_LIST.setup(session)
        await self.BITE_ACTIONS.setup(session)
        await self.BITE_PLACES.setup(session)
        await self.BITE_BODY_PARTS.setup(session)

        await self.COUNTER.setup(session)
        await self.COUNTER_DEATH.setup(session)
        await self.COUNTER_GLOBAL.setup(session)

        await self.ANIME.setup(session)
        await self.AUCTIONS.setup(session)
        await self.CHALLENGES.setup(session)
        await self.CREDITS.setup(session)
        await self.GAMES.setup(session)
        await self.LORE.setup(session)
        await self.MARATHONS.setup(session)
        await self.MERCH.setup(session)
        await self.ROULETTE.setup(session)
        await self.SOCIALS.setup(session)

    def has_list(self, name: str) -> bool:
        return name.upper() in (
            "SAVE_CHOICES",
            "BITE_IGNORE_LIST",
            "BITE_ACTIONS",
            "BITE_PLACES",
            "BITE_BODY_PARTS",
        )

    def is_twitchbot(self, name: str) -> bool:
        return name.upper() in (
            "SAVE_CHOICES",
            "BITE_IGNORE_LIST",
            "BITE_ACTIONS",
            "BITE_PLACES",
            "BITE_BODY_PARTS",
            "COUNTER",
            "COUNTER_DEATH",
            "COUNTER_GLOBAL",
        )


all_data = AllData()
