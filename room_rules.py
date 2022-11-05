from furniture_sprites import *


def get_bedroom_guest_17__24_9m():
    furniture_obj = list()

    # generate curtains 170x20
    furniture_obj.append(Curtains(z=70))

    # generate double bed 160x200x60
    furniture_obj.append(DoubleBed())

    # generate nightstand 60x50x60
    furniture_obj.append(Nightstand())

    # generate optional nightstand 60x50x60
    furniture_obj.append(Nightstand(optional=True))

    # generate Table lamp 20x20x30
    furniture_obj.append(TableLamp(z=60))

    # generate Wardrobe 100x31x200
    furniture_obj.append(Wardrobe())

    # generate Computer table 136x60x75
    furniture_obj.append(ComputerTable())

    # generate Computer Chair # 48x52x45
    furniture_obj.append(ComputerChair())

    # generate optional armchair # 91x84x87
    furniture_obj.append(Armchair(optional=True))

    # generate big carpet # 230x160
    furniture_obj.append(CarpetBig())

    return furniture_obj


def get_bedroom_master_17__24_9m():
    furniture_obj = get_bedroom_guest_17__24_9m()

    # generate tv 55"(122x69x10cm)  # TODO: make it 55"
    furniture_obj.insert(4, TV(z=120, optional=True))

    return furniture_obj


def living_room_9__15m():
    furniture_obj = list()

    # generate tv 65"
    furniture_obj.append(TV())

    # generate curtains 170x20
    furniture_obj.append(Curtains(170, 20, 200, 0, 0, 0, 70))

    # generate sofa 180x86x86
    furniture_obj.append(Sofa())

    # generate coffee table 118x62x45
    furniture_obj.append(CoffeeTable())

    # generate dresser 110x50x100
    furniture_obj.append(Dresser())

    # generate armchair 91x84x87
    furniture_obj.append(Armchair())

    # generate floor lamp 30x30x160
    furniture_obj.append(FloorLamp())

    return furniture_obj


def generate_furniture():
    furniture_obj = list()

    # ==================== FURNITURE ====================
    # args: width, height, depth, angle, x, y, z, optional
    furniture_obj.append(TV())  # generate tv # 65"(144x81x15cm)    55"(122x69x10cm)
    furniture_obj.append(Sofa())
    furniture_obj.append(CoffeeTable())
    furniture_obj.append(Armchair())
    furniture_obj.append(CarpetBig())  # TODO: generate big carpet # 128x88
    furniture_obj.append(ComputerTable())
    furniture_obj.append(ComputerChair())
    furniture_obj.append(Nightstand(60, 50, 180))
    furniture_obj.append(Dresser())
    furniture_obj.append(FloorLamp())
    furniture_obj.append(FloorLamp(optional=True))
    furniture_obj.append(Table())  # # # generate table# 170x65
    furniture_obj.append(KitchenChair())
    furniture_obj.append(KitchenChair())
    furniture_obj.append(KitchenChair())

    return furniture_obj
