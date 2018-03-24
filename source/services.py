from typing import List
from importlib import import_module


class Client:

    def __init__(self, service: str):
        self.service = service
        mod = import_module('.clients.' + service, __package__)
        self.client = mod.Connector()

    def get_list(self) -> List[dict]:
        return self.client.get_list()
