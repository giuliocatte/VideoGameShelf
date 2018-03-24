from typing import List

from steam.webapi import WebAPI

from secrets import STEAM_KEY, STEAM_PLAYER_ID
from ..constants import Service, Validation


class Connector:

    def __init__(self):
        self.api = WebAPI(STEAM_KEY)

    def get_list(self) -> List[dict]:

        # TODO: c'e' modo di escludere schifezze tipo i mod, le beta, e anche i film?

        res = self.api.call("IPlayerService.GetOwnedGames", steamid=STEAM_PLAYER_ID, include_appinfo=True,
                        include_played_free_games=True, appids_filter=None)

        # TODO: gestire fallimento

        for game in res['response']['games']:
            yield {'service': Service.STEAM, 'key': str(game['appid']), 'name': game['name'], 'validation': Validation.TODO}


        # return [{'service': Service.STEAM, 'key': str(game['appid']), 'name': game['name'], 'validation': Validation.TODO}
        #             for game in res['response']['games']]

