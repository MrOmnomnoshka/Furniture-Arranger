from furniture_sprites import *


def get_bedroom_guest_17__24_9m():
    furniture_obj = list()

    # generate curtains 170x20
    furniture_obj.append(Curtains(170, 20, 200))

    # generate double bed 160x200x60
    furniture_obj.append(DoubleBed(160, 200, 60))

    # generate Wardrobe 100x31x200
    furniture_obj.append(Wardrobe(150, 55, 200))

    # generate Computer table 136x60x75
    furniture_obj.append(ComputerTable(136, 60, 75))

    # generate Computer Chair # 48x52x45
    furniture_obj.append(ComputerChair(48, 52, 45))

    # generate armchair # 91x84x87
    furniture_obj.append(Armchair(91, 84, 87))

    # generate 2 nightstands 60x50x60
    furniture_obj.append(Nightstand(60, 50, 60))
    furniture_obj.append(Nightstand(60, 50, 60))

    # generate Table lamp 20x20x30
    furniture_obj.append(TableLamp(20, 20, 30))

    # generate big carpet # 230x160
    furniture_obj.append(CarpetBig(230, 160, 0))

    return furniture_obj
