from furniture_sprites import *
from sprite_object import SpriteObject


def get_bedroom_guest_17__24_9m():
    furniture_obj = list()

    # # generate curtains 170x20
    # furniture_obj.append(Curtains(170, 20, 200, 0, 0, 0, 70))

    # generate double bed 160x200x60
    furniture_obj.append(DoubleBed(160, 200, 60, 45, 300, 100))

    # # generate nightstand 60x50x60
    # furniture_obj.append(Nightstand(60, 50, 60))
    #
    # # generate optional nightstand 60x50x60
    # furniture_obj.append(Nightstand(60, 50, 60, 0, 0, 0, 0, True))
    #
    # # generate Table lamp 20x20x30
    # furniture_obj.append(TableLamp(30, 30, 30, 0, 0, 0, 60))
    #
    # generate Wardrobe 100x31x200
    furniture_obj.append(Wardrobe(150, 55, 200, 0, 300, 200))
    #
    # # generate Computer table 136x60x75
    # furniture_obj.append(ComputerTable(136, 60, 75))
    #
    # # generate Computer Chair # 48x52x45
    # furniture_obj.append(ComputerChair(48, 52, 45))
    #
    # # generate optional armchair # 91x84x87
    # furniture_obj.append(Armchair(91, 84, 87, 0, 0, 0, 0, True))

    # # generate big carpet # 230x160
    # furniture_obj.append(CarpetBig(230, 160, 0))

    return furniture_obj


def get_bedroom_master_17__24_9m():
    furniture_obj = get_bedroom_guest_17__24_9m()

    # # generate tv 55"(122x69x10cm)
    # furniture_obj.insert(4, TV(122, 10, 69, 0, 0, 0, 120, True))

    return furniture_obj


def living_room_9__15m():
    furniture_obj = list()

    # generate tv 65"
    furniture_obj.append(TV(144, 15, 81, 0, 0, 0, 120))

    # generate curtains 170x20
    furniture_obj.append(Curtains(170, 20, 200, 0, 0, 0, 70))

    # generate sofa 180x86x86
    furniture_obj.append(Sofa(180, 86, 86))

    # generate coffee table 118x62x45
    furniture_obj.append(CoffeeTable(118, 62, 45))

    # generate dresser 110x50x100
    furniture_obj.append(Dresser(110, 50, 100))

    # generate armchair 91x84x87
    furniture_obj.append(Armchair(91, 84, 87))

    # generate floor lamp 30x30x30
    furniture_obj.append(FloorLamp(30, 30, 160))

    return furniture_obj
