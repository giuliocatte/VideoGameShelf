from enum import Enum


class Entity(Enum):
    OWNED = "owned"
    GAME = "games"
    STAGING = "staging"


class Validation(Enum):
    TODO = "todo"
    STEAM_ID = "steam_id"
    NAME_MATCH = "name_match"
    LOOSE_MATCH = "loose_match"
    MULTIPLE = "multiple"
    NOT_FOUND = "not_found"
    CONFUSED = "confused"
    MANUAL = "manual"  # fixed manually later
    DELETED = "deleted"  # I don't want to see this game


class Service(Enum):
    STEAM = 'steam'
    GOG = 'gog'

