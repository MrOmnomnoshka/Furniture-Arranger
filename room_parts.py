from sprite_object import SpriteObject
from colors import *


class Door(SpriteObject):
    color = door_color
    offsets_to_this = {"bottom": 110}


class Window(SpriteObject):
    color = light_blue
    offsets_to_this = {"bottom": 75}


class Wall(SpriteObject):
    color = black
