from crud.anime import AnimeData
from crud.challenges import ChallengesData
from crud.games import GamesData
from crud.lore import LoreData
from crud.marathons import MarathonsData
from crud.roulette import RouletteData
from crud.socials import SocialsData
from crud.twitchbot_counters import TwitchBotCounter
from crud.twitchbot_lists import TwitchBotList
from sqlalchemy.ext.asyncio import AsyncSession


class AllData:
    def __init__(self) -> None:
        self.TIMECODE_MESSAGE = "Saved"

        self.SAVE_CHOICES = TwitchBotList("saves")

        self.BITE_CHEAT_STREAMER_PERCENT = 0
        self.BITE_CHEAT_DEFENSE_PERCENT = 0

        self.BITE_IGNORE_LIST = TwitchBotList("bite_ignore_list")
        self.BITE_ACTIONS = TwitchBotList("bite_actions")
        self.BITE_PLACES = TwitchBotList("bite_places")
        self.BITE_BODY_PARTS = TwitchBotList("bite_body_parts")

        self.COUNTER_DEATH = TwitchBotCounter("death")
        self.COUNTER = TwitchBotCounter("count")
        self.COUNTER_GLOBAL = TwitchBotCounter("global")

        self.ANIME = AnimeData()
        self.CHALLENGES = ChallengesData()
        self.GAMES = GamesData()
        self.LORE = LoreData()
        self.MARATHONS = MarathonsData()
        self.ROULETTE = RouletteData()
        self.SOCIALS = SocialsData()

    async def setup(self, session: AsyncSession) -> None:
        await all_data.SAVE_CHOICES.setup(session)

        await all_data.BITE_IGNORE_LIST.setup(session)
        await all_data.BITE_ACTIONS.setup(session)
        await all_data.BITE_PLACES.setup(session)
        await all_data.BITE_BODY_PARTS.setup(session)

        await all_data.COUNTER.setup(session)
        await all_data.COUNTER_DEATH.setup(session)
        await all_data.COUNTER_GLOBAL.setup(session)

        await all_data.ANIME.setup(session)
        await all_data.CHALLENGES.setup(session)
        await all_data.GAMES.setup(session)
        await all_data.LORE.setup(session)
        await all_data.MARATHONS.setup(session)
        await all_data.ROULETTE.setup(session)
        await all_data.SOCIALS.setup(session)

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
            "COUNTER_DEATH",
            "COUNTER",
            "COUNTER_GLOBAL",
        )


all_data = AllData()
