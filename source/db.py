
import sqlite3
from collections import OrderedDict
import json
from typing import List, Optional
import logging
from enum import Enum

from .constants import Entity, Validation, Service

logger = logging.getLogger('vgs.db')


DBNAME = 'vgshelf.db'


class JSON(str):
    pass


COLUMNS = {
    Entity.OWNED: OrderedDict((
        ('service', Service),
        ('key', str),
        ('name', str),
        ('validation', Validation),
        ('id', int)
    )),
    Entity.GAME: OrderedDict((
        ('id', int),
        ('name', str),
        ('data', JSON),
    )),
    Entity.STAGING: OrderedDict((
        ('name', str),
        ('results', JSON)
    ))
}

KEYS = {
    Entity.OWNED: ('service', 'key'),
    Entity.GAME: ('id',),
    Entity.STAGING: ('name',)
}

COLUMN_TYPES = {
    'enum': 'text',
    'str': 'text',
    'json': 'text',
    'int': 'integer'
}


class DBConnection:
    '''
        wrapper class around db connection
        some sort of super-light orm
    '''

    def __init__(self):
        conn = sqlite3.connect(DBNAME)
        conn.row_factory = sqlite3.Row
        self.connection = conn

    @staticmethod
    def convert(value, column_type):
        if value is not None:
            if column_type == 'json':
                return json.dumps(value)
            elif column_type == 'enum':
                return value.value
        return value

    @staticmethod
    def parse(value, column_type):
        if value is not None:
            if column_type == 'json':
                return json.loads(value)
            elif column_type == 'enum':
                return
        return value

    @staticmethod
    def column_from_type(cls):
        if issubclass(cls, (Enum, str)):
            return 'text'
        elif issubclass(cls, int):
            return 'integer'
        else:
            raise ValueError("unexpected class: {}".format(cls))

    def deploy(self, erase: bool=False):
        '''
            method for db generation
            tables:

            owned: (service, key), name, validation, id
            games: (id), name, data
            staging: (name), results
        '''
        conn = self.connection
        for k, v in COLUMNS.items():
            if erase:
                conn.execute('DROP TABLE {}'.format(k))
            create = 'CREATE TABLE {} ({})'.format(k.value, ', '.join(
               '{} {}'.format(n, self.column_from_type(t)) for n, t in v.items()
            ))
            logger.debug('QUERY: %s', create)
            conn.execute(create)
        conn.commit()

    def write_entities(self, name: Entity, entities: List[dict]):
        conn = self.connection
        conv = self.convert
        columns = COLUMNS[name]
        q = '''
            INSERT INTO {} VALUES ({})
        '''.format(name.value, ', '.join('?' for _ in columns))
        p = [[conv(ent.get(k), v) for k, v in columns.items()] for ent in entities]
        logger.debug('QUERY: %s\nwith parameters: %s', q, p)
        conn.executemany(q, p)
        conn.commit()

    def update_entities(self, name: Entity, entities: List[dict], attributes: dict):
        conn = self.connection
        conv = self.convert
        columns = COLUMNS[name]
        keys = KEYS[name]
        set_pars = [conv(v, columns[k]) for k, v in attributes.items()]
        q = 'UPDATE {} SET {} WHERE {}'.format(
                name.value,
                ', '.join('{} = ?'.format(k) for k in attributes),
                ' AND '.join('{} = ?'.format(k) for k in keys)
        )
        p = [set_pars + [conv(ent[k], columns[k]) for k in keys] for ent in entities]
        logger.debug('QUERY: %s\nwith parameters: %s', q, p)
        conn.executemany(q, p)
        conn.commit()

    def load_entities(self, name: Entity, filter: Optional[dict]=None) -> List[dict]:
        conn = self.connection
        conv = self.convert
        columns = COLUMNS[name]
        if filter:
            q = 'SELECT * FROM {} WHERE {}'.format(name.value, ' AND '.join("{} = ?".format(k) for k in filter))
            p = [conv(v, columns[k]) for k, v in filter.items()]
            logger.debug('QUERY: %s\nwith parameters: %s', q, p)
            res = conn.execute(q, p)
        else:
            q = 'SELECT * FROM {}'.format(name.value)
            logger.debug('QUERY: %s', q)
            res = conn.execute(q)
        return [dict(rec) for rec in iter(res.fetchone, None)]

    def delete_entities(self, name: Entity, filter: Optional[dict]=None):
        conn = self.connection
        conv = self.convert
        columns = COLUMNS[name]
        if filter:
            q = 'DELETE FROM {} WHERE {}'.format(name.value, ' AND '.join("{} = ?".format(k) for k in filter))
            p = [conv(v, columns[k]) for k, v in filter.items()]
            logger.debug('QUERY: %s\nwith parameters: %s', q, p)
            conn.execute(q, p)
        else:
            q = 'DELETE FROM {}'.format(name.value)
            logger.debug('QUERY: %s', q)
            conn.execute(q)
        conn.commit()
