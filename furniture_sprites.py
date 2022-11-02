from furniture import Furniture
from room_parts import Wall, Door, Window


class DoubleBed(Furniture):
    image_path = "images/furniture/double_bed.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True}}


class SingleBed(Furniture):
    image_path = "images/furniture/single_bed.png"


class Dresser(Furniture):
    image_path = "images/furniture/dresser.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True}}


class Table(Furniture):
    image_path = "images/furniture/table.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 150), "angle": 0, "required": True}}


class ComputerTable(Furniture):
    image_path = "images/furniture/computer table.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                               DoubleBed: {"sides": ("any", "any", ">30"), "angle": "any"}}


class Armchair(Furniture):
    image_path = "images/furniture/armchair.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                               DoubleBed: {"sides": ("any", "any", ">30"), "angle": "any"}}
             #Sofa: {"sides": ("midlr", "midlr", 0), "angle": 45}}  # TODO: add 45 angle to side and -45 to other side


class TV(Furniture):
    image_path = "images/furniture/tv.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0,  "required": True},
                               DoubleBed: {"sides": ("midbottom", "midbottom", "any"), "angle": 180}}


class Sofa(Furniture):
    image_path = "images/furniture/sofa.png"

    rules_to_this_furniture = {TV: {"sides": ("midbottom", "midbottom", 200), "angle": 180}}


class FloorLamp(Furniture):
    image_path = "images/furniture/floor lamp.png"

    rules_to_this_furniture = {Sofa: {"sides": ("midlr", "midlr", 0), "angle": 0},
                               Armchair: {"sides": ("midlr", "midlr", 0), "angle": 0},
                               Dresser: {"sides": ("midlr", "midlr", 0), "angle": 0}}

    # def __init__(self, *args):
    #     super().__init__(*args)  # TODO: this
    #     self.rules_to_this_furniture.update({FloorLamp: {"sides": ("any", "lr", ">140"), "angle": "any", "required": True}})


class KitchenChair(Furniture):
    image_path = "images/furniture/kitchen_chair.png"

    rules_to_this_furniture = {Table: {"sides": ("midbottom", "midany", 10), "angle": "center"}}  # TODO: angle - перпендикулярно грани стола


class ComputerChair(Furniture):
    image_path = "images/furniture/chair.png"

    rules_to_this_furniture = {ComputerTable: {"sides": ("midbottom", "midbottom", 10), "angle": 180}}


class CoffeeTable(Furniture):
    image_path = "images/furniture/coffee_table.png"

    rules_to_this_furniture = {Sofa: {"sides": ("midbottom", "midbottom", 20), "angle": 180},
                               Window: None}

    # rules_to_this_furniture = {Sofa: {"sides": ("center", "midbottom", 0), "angle": 0},
    #                            Window: None, Door: None}


class Curtains(Furniture):
    image_path = "images/furniture/curtains.png"

    rules_to_this_furniture = {Window: {"sides": ("midtop", "midbottom", 0), "angle": 0}}


class Nightstand(Furniture):
    image_path = "images/furniture/nightstand.png"

    rules_to_this_furniture = {Sofa: {"sides": ("midlr", "midlr", 0), "angle": 0},
                               #Armchair: {"sides": ("midlr", "midlr", 0), "angle": 0},
                               DoubleBed: {"sides": ("top", "top", 0), "angle": 0},
                               Window: None}


class TableLamp(Furniture):
    image_path = "images/furniture/table_lamp.png"

    rules_to_this_furniture = {Nightstand: {"sides": ("center", "center", 0), "angle": 0}}


class TableRound(Furniture):
    image_path = "images/furniture/table_round.png"


class Wardrobe(Furniture):
    image_path = "images/furniture/wardrobe.png"

    rules_to_this_furniture = {Wall: {"sides": ("midtop", "bottom", 0), "angle": 0, "required": True},
                               DoubleBed: {"sides": ("any", "any", ">30"), "angle": "any"}}


class CarpetBig(Furniture):
    image_path = "images/furniture/carpet_big.png"

    rules_to_this_furniture = {Sofa: {"sides": ("center", "midbottom", 60), "angle": 180},
                               DoubleBed: {"sides": ("midbottom", "midbottom", 30), "angle": 0},
                               Window: None, Door: None}
