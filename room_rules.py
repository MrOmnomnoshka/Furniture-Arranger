from furniture_sprites import *


def get_bedroom_guest_17__24_9m():
    furniture_obj = [Curtains(), DoubleBed(), Nightstand(), Nightstand(optional=True), TableLamp(), Wardrobe(),
                     ComputerTable(), ComputerChair(), Armchair(optional=True), CarpetBig()]
    return furniture_obj


def get_bedroom_master_17__24_9m():
    furniture_obj = get_bedroom_guest_17__24_9m()
    # not default 55"(122x10x69)cm
    furniture_obj.insert(2, TV(122, 10, 69, optional=True))
    return furniture_obj


def living_room_9__15m():
    furniture_obj = [Curtains(), TV(), Sofa(), CoffeeTable(), Dresser(), Armchair(), FloorLamp()]
    return furniture_obj


def living_room_BIG():
    # ==================== FURNITURE ====================
    # args: width, height, depth, angle, x, y, z, optional
    furniture_obj = [TV(), Sofa(), CoffeeTable(), CarpetBig(), Table(), KitchenChair(), KitchenChair(),
                     KitchenChair(), KitchenChair(optional=True), ComputerTable(), ComputerChair(), Armchair(),
                     Dresser(), Nightstand(optional=True), FloorLamp(optional=True)]

    return furniture_obj


def all_furniture():
    import sys
    import inspect

    class_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    furniture_obj = [obj() for name, obj in class_members if name not in ('Furniture', 'Door', 'Window', 'Wall')]
    return furniture_obj
