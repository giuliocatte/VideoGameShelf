from collections import defaultdict
from typing import List, Dict, Optional
import logging

from igdb_api_python.igdb import igdb

from secrets import IGDB_KEY
from .db import DBConnection, Entity
from .services import Client, Service
from .constants import Validation


logger = logging.getLogger('vgs.datasync')


class DataSync:

    def __init__(self):
        self.db = DBConnection()

    def sync_list(self, service: str):
        list = Client(service).get_list()
        self.db.write_entities(Entity.OWNED, list)

    def sync_masterdata(self, limit: Optional[int]=None, erase: bool=False):
        if erase:
            owned = self.db.load_entities(Entity.OWNED)
            logger.info("deleting previously saved masterdata")
            self.db.delete_entities(Entity.GAME)
            logger.info("deleting staged records")
            self.db.delete_entities(Entity.STAGING)
            logger.info("deleting validation info on owned records")
            self.db.update_entities(Entity.OWNED, owned, {"validation": Validation.TODO, "id": None})
        else:
            logger.debug("retrieving owned records")
            owned = self.db.load_entities(Entity.OWNED, {"validation": Validation.TODO})

        games = defaultdict(list)
        for el in owned:
            games[el['name']].append(el)
            if limit and len(games) >= limit:
                break
        logger.debug("to search: %s total names in %s owned records", len(games), len(owned))
        self.download_md(games)

    def download_md(self, games: Dict[str, List[dict]]):
        '''
            downloads masterdata from igdb for every game passed in input
            input is a dictionary {'gamename': [owned_records]}

            matching is made by steam id when available, then by name
            when multiple matches are available, a row in staging table is inserted
        '''
        logging.info("loading masterdata for %s games", len(games))
        mdconn = igdb(IGDB_KEY)
        valid = []
        for game, own_recs in games.items():
            res = mdconn.games({'search': game})
            # TODO: gestire fallimento
            game_md = res.body
            if game_md:
                steam_id = False
                for own_rec in own_recs:
                    if own_rec['service'] == Service.STEAM:
                        steam_id = own_rec['key']
                        break
                namematch = []
                for val in game_md:
                    if val.get('external', {}).get('steam') == steam_id:
                        valid.append(val)
                        self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.STEAM_ID, "id": val["id"]})
                        break
                    if val['name'] == game:
                        namematch.append(val)
                else:
                    if len(namematch) == 1:
                        val = namematch[0]
                        valid.append(val)
                        self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.NAME_MATCH, "id": val["id"]})
                    elif namematch:
                        self.db.write_entities(Entity.STAGING, [{'name': game, 'results': namematch}])
                        self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.MULTIPLE})
                    elif len(game_md) == 1:
                        val = game_md[0]
                        self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.LOOSE_MATCH, "id": val["id"]})
                        valid.append(val)
                    else:
                        self.db.write_entities(Entity.STAGING, [{'name': game, 'results': game_md}])
                        self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.CONFUSED})
            else:
                self.db.update_entities(Entity.OWNED, own_recs, {"validation": Validation.NOT_FOUND})

        self.db.write_entities(Entity.GAME, [{'id': v['id'], 'name': v['name'], 'data': v} for v in valid])
