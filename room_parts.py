from sprite_object import SpriteObject
from colors import *


class Door(SpriteObject):
    rules = dict()
    color = door_color
    offsets_to_this = {"bottom": 110}


class Window(SpriteObject):
    rules = dict()
    color = light_blue
    offsets_to_this = {"bottom": 75}


class Wall(SpriteObject):
    rules = dict()
    color = black
