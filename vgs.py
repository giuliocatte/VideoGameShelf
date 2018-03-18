import fire
import logging

from source.services import Service
from source.datasync import DataSync
from source.db import DBConnection


logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.INFO)
logging.getLogger("vgs").setLevel(logging.DEBUG)



class Launcher:

    def deploy_db(self):
        DBConnection().deploy()

    def download_list_from_service(self, service):  # c'e' da fare qualche capriola per far bere le annotations a fire
        '''
            reads the list of games on the specified server
        '''
        service = service.lower()
        if service not in {s.value for s in Service}:
            raise ValueError("unrecognised service: {}".format(service))
        DataSync().sync_list(service)

    def download_masterdata_from_db(self):
        DataSync().sync_masterdata()


fire.Fire(Launcher)
