from enum import Enum


class Roles(str, Enum):
    Default = 'DEFAULT'


class AuthType(str, Enum):
    GROUP = 'GROUP'
    USER = 'USER'
