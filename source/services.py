from typing import List
from .constants import Validation, Service


class Client:

    def __init__(self, service: str):
        self.service = service

    def get_list(self) -> List[dict]:
        return getattr(self, '_list_from_' + self.service)()

    def _list_from_steam(self) -> List[dict]:
        # import nel metodo cosi' non devo necessariamente dipendere da steam
        from secrets import STEAM_KEY, STEAM_PLAYER_ID
        from steam.webapi import WebAPI

        api = WebAPI(STEAM_KEY)
        res = api.call("IPlayerService.GetOwnedGames", steamid=STEAM_PLAYER_ID, include_appinfo=True,
                        include_played_free_games=True, appids_filter=None)
        # TODO: gestire fallimento
        return [{'service': Service.STEAM, 'key': game['appid'], 'name': game['name'], 'validation': Validation.TODO}
                    for game in res['response']['games']]

