from furniture import Furniture
from room_parts import Wall, Door, Window
# TODO: move all classes to other place, to be able to refer to each other
# TODO: add possibility to have more than 1 rule


class DoubleBed(Furniture):
    width, height, depth = 160, 200, 100
    image_path = "images/furniture/double_bed.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                     Window: {"sides": ("top", "top", "no"), "angle": "perpendicular", "required": True}}
    offsets_to_this = {"top": 0, "bottom": 50, "left": 20, "right": 20}


class SingleBed(Furniture):
    width, height, depth = 100, 200, 60
    image_path = "images/furniture/single_bed.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True}}  # TODO: common class for beds?
    offsets_to_this = {"top": 0, "bottom": 50, "left": 20, "right": 20}


class Dresser(Furniture):
    width, height, depth = 110, 50, 100
    image_path = "images/furniture/dresser.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True}}


class Table(Furniture):
    width, height, depth = 160, 90, 75
    image_path = "images/furniture/table.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 150), "angle": 0, "required": True}}
    offsets_to_this = {"top": 60, "bottom": 60, "left": 60, "right": 60}


class Armchair(Furniture):
    width, height, depth = 91, 84, 87

    image_path = "images/furniture/armchair.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True}}
    # Sofa: {"sides": ("midlr", "midlr", 0), "angle": 45}}  # TODO: add 45 angle to side and -45 to other side


class TV(Furniture):
    width, height, depth, z = 144, 15, 81, 120  # 65"(144x15x81)cm  ||  55"(122x10x69)cm
    image_path = "images/furniture/tv.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                     DoubleBed: {"sides": ("midbottom", "midbottom", "any"), "angle": 180}}
    # offsets_to_this = {"bottom": 100}


class ComputerTable(Furniture):
    width, height, depth = 136, 60, 75
    image_path = "images/furniture/computer table.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                     TV: {"sides": ("any", "any", ">50"), "angle": "any"}}
    offsets_to_this = {"bottom": 40, "left": 20, "right": 20}


class Sofa(Furniture):
    width, height, depth = 180, 86, 86
    image_path = "images/furniture/sofa.png"

    rules_to_this = {TV: {"sides": ("midbottom", "midbottom", 200), "angle": 180}}


class FloorLamp(Furniture):
    width, height, depth = 40, 40, 180
    image_path = "images/furniture/floor lamp.png"

    rules_to_this = {Sofa: {"sides": ("midlr", "midlr", 0), "angle": 0},
                     Armchair: {"sides": ("midlr", "midlr", 0), "angle": 0},
                     Dresser: {"sides": ("midlr", "midlr", 0), "angle": 0}}

    # def __init__(self, *args, **kwargs):
    #     self.rules_to_this.update({FloorLamp: {"sides": ("any", "lr", ">220"),
    #                                            "angle": "any",
    #                                            "required": True}})
    #
    #     super().__init__(*args, **kwargs)


class KitchenChair(Furniture):
    width, height, depth = 48, 52, 81
    image_path = "images/furniture/kitchen_chair.png"

    # TODO: angle - 'перпендикулярно' грани стола (и потом добавить параллельно)
    rules_to_this = {Table: {"sides": ("midbottom", "midany", 10), "angle": "center"}}


class ComputerChair(Furniture):
    width, height, depth = 48, 52, 140
    image_path = "images/furniture/chair.png"

    rules_to_this = {ComputerTable: {"sides": ("midbottom", "midbottom", 10), "angle": 180}}


class CoffeeTable(Furniture):
    width, height, depth = 118, 62, 45
    image_path = "images/furniture/coffee_table.png"

    rules_to_this = {Sofa: {"sides": ("midbottom", "midbottom", 20), "angle": 180}}


class Curtains(Furniture):
    width, height, depth, z = 170, 20, 240, 20+240//2  # TODO: for human readability add 'z_from_floor=20'
    image_path = "images/furniture/curtains.png"

    rules_to_this = {Window: {"sides": ("midtop", "midbottom", 0), "angle": 0}}


class Nightstand(Furniture):
    width, height, depth = 60, 50, 60
    image_path = "images/furniture/nightstand.png"

    rules_to_this = {Sofa: {"sides": ("midlr", "midlr", 0), "angle": 0},
                     DoubleBed: {"sides": ("top", "top", 0), "angle": 0}}


class TableLamp(Furniture):
    width, height, depth, z = 25, 25, 30, 60+30//2
    image_path = "images/furniture/table_lamp.png"

    rules_to_this = {Nightstand: {"sides": ("center", "center", 0), "angle": 0}}


class TableRound(Furniture):
    width, height, depth = 100, 100, 75
    image_path = "images/furniture/table_round.png"


class Wardrobe(Furniture):
    width, height, depth = 150, 55, 200
    image_path = "images/furniture/wardrobe.png"

    rules_to_this = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                     DoubleBed: {"sides": ("any", "any", ">70"), "angle": "perpendicular", "required": True}}
    offsets_to_this = {"bottom": 40, "left": 20, "right": 20}


class CarpetBig(Furniture):
    width, height, depth = 230, 160, 1
    image_path = "images/furniture/carpet_big.png"

    rules_to_this = {Sofa: {"sides": ("center", "midbottom", 60), "angle": 180},
                     DoubleBed: {"sides": ("midbottom", "midbottom", 30), "angle": 0}}
