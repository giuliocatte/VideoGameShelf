import fire
import logging
import webbrowser
import sys

from source.datasync import DataSync
from source.db import DBConnection
from source.constants import Entity, Validation, Service


logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("vgs")

# TODO: c'e' da fare qualche capriola per far bere le annotations a fire


def read_int_value():
    val = input()
    if not val.isdigit():
        print("invalid value, quitting")
        sys.exit()
    return int(val)


def ask(text, default='n'):
    print(text, '(y/n) (default: {})'.format(default))
    val = input().lower() or default
    if val not in ('y', 'n'):
        print("invalid value, quitting")
        sys.exit()
    return val == 'y'


class Launcher:

    def __init__(self, loglevel='INFO'):
        logger.setLevel(getattr(logging, loglevel.upper()))

    def deploy_db(self):
        '''
            first creation of the database
        '''
        DBConnection().deploy()

    def download_list_from_service(self, service):
        '''
            reads the list of games on the specified server
        '''
        service = service.lower()
        if service not in {s.value for s in Service}:
            raise ValueError("unrecognised service: {}".format(service))
        DataSync().sync_list(service)

    def download_masterdata_from_db(self, limit=None, erase=False):
        '''
            downloads masterdata for all owned games
        '''
        DataSync().sync_masterdata(limit, erase)

    def process_staging(self):
        '''
            interactively process a single name in the staging table
        '''
        db = DBConnection()
        data = db.load_entities(Entity.STAGING, limit=1)
        if data:
            data = data[0]
        else:
            print("no staged results to process")
            return
        results = data['results']
        print("processing name {}, possible values are:".format(data["name"], len(results)))
        for i, rec in enumerate(results, start=1):
            print("{}. {} ({} - {})".format(
                i,
                rec['slug'],
                min(d['y'] for d in rec['release_dates'] if 'y' in d) if any('y' in d for d in rec.get('release_dates', ())) else '?',
                rec['name']
            ))
        if ask("open urls in browser?"):
            for rec in results:
                webbrowser.open(rec['url'])
        owned = [o for o in db.load_entities(Entity.OWNED,
                    {"name": data["name"]}) if o['validation'] in {Validation.CONFUSED, Validation.MULTIPLE}]
        print("you own {} games to process with this names".format(len(owned)))
        for rec in owned:
            game = None
            print("service: {0[service].value}, key: {0[key]}".format(rec))
            print("please enter the number for the correct game, or 0 if no one of the values is correct:")
            val = read_int_value()
            if val > len(data["results"]):
                print("invalid value, quitting")
                return
            elif not val:
                print("choose one of the following:")
                print("1. delete the game from list")
                print('2. input the correct "slug"')
                print("3. mark game as not found")
                val = read_int_value()
                if val == 1:
                    db.update_entities(Entity.OWNED, [rec], {"validation": Validation.DELETED})
                elif val == 2:
                    print('insert the "slug":')
                    val = input()
                    game = DataSync().game_from_slug(val)
                elif val == 3:
                    db.update_entities(Entity.OWNED, [rec], {"validation": Validation.NOT_FOUND})
                else:
                    print("unexpected value, quitting")
                    return
            else:
                game = results[val - 1]
            if game:
                previous = db.load_entities(Entity.GAME, filter={'id': game['id']}, limit=1, fields=['id'])
                if not previous:
                    db.write_entities(Entity.GAME, [{'id': game['id'], 'name': game['name'], 'data': game}])
                db.update_entities(Entity.OWNED, [rec], {"validation": Validation.MANUAL, "id": game["id"]})
        db.delete_entities(Entity.STAGING, {"name": data["name"]})
        db.connection.commit()


fire.Fire(Launcher)
