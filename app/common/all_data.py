from crud.anime import AnimeData
from crud.challenges import ChallengesData
from crud.games import GamesData
from crud.lore import LoreData
from crud.socials import SocialsData
from crud.twitchbot_counters import TwitchBotCounter
from crud.twitchbot_lists import TwitchBotList


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

        self.LORE = LoreData()
        self.ANIME = AnimeData()
        self.CHALLENGES = ChallengesData()
        self.GAMES = GamesData()
        self.SOCIALS = SocialsData()

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
