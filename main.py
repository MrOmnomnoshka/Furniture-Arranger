from random import randrange
from GA_furniture import start_ga, set_sprite_values
from time import time

import settings
from furniture_sprites import *
from draw_engine import draw_loop
import room_rules


def generate_room_parameters(room_size, accuracy=2):
    multiplier = 10 ** accuracy  # accuracy = 2  # how many decimal places to round to
    min_size = 3  # from 2.5m
    max_size = room_size // 2.5  # to half of a room size
    width = randrange(min_size * multiplier, max_size * multiplier) / multiplier
    height = round(room_size/width, accuracy)
    return int(width*100), int(height*100)  # , depth=250?


def generate_object_in_walls(obj, width, walls):
    from random import choice, randrange
    from pygame.math import Vector2
    wall = choice(walls)
    fit_in_wall = wall.width - width - wall.height * 2
    attempts = 100
    while fit_in_wall <= 0:  # It can't fit in the wall
        wall = choice(walls)
        fit_in_wall = wall.width - width - wall.height * 2

        attempts -= 1
        if attempts == 0:
            raise Exception("Can't fit in any wall")

    side = wall.convert_self_side("midleft")
    pos_vec = Vector2(randrange(fit_in_wall) + width // 2 + wall.height, 0).rotate(-wall.angle)
    new_obj = obj(width, wall.height, settings.ROOM_DEPTH, wall.angle, side.x + pos_vec.x, side.y + pos_vec.y,
                  settings.ROOM_DEPTH)  # Make it the highest from render order
    return new_obj


def generate_walls_rectangle():
    walls = list()
    # generate 4 walls in rectangular form
    walls.append(Wall(settings.ROOM_HEIGHT, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 90))
    walls[-1].rect.topleft = (0, 0)  # left
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 0))
    walls[-1].rect.topleft = (0, 0)  # top
    walls.append(Wall(settings.ROOM_HEIGHT, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 270))
    walls[-1].rect.topleft = (settings.ROOM_WIDTH - settings.WALLS_WIDTH, 0)  # right
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].rect.topleft = (0, settings.ROOM_HEIGHT - settings.WALLS_WIDTH)  # bottom
    return walls


def generate_walls_with_corners():
    walls = list()
    # generate 4 walls in rectangular form with 2 bottom corners
    walls.append(Wall(settings.ROOM_HEIGHT // 1.3, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 90))
    walls[-1].rect.topleft = (0, 0)  # left
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 0))
    walls[-1].rect.topleft = (0, 0)  # top
    walls.append(Wall(settings.ROOM_HEIGHT // 1.3, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 270))
    walls[-1].rect.topleft = (settings.ROOM_WIDTH - settings.WALLS_WIDTH, 0)  # right
    walls.append(Wall(settings.ROOM_WIDTH // 4, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].rect.topleft = (0, settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # bottom left corner
    walls.append(Wall(settings.ROOM_HEIGHT - settings.ROOM_HEIGHT // 1.3 + settings.WALLS_WIDTH, settings.WALLS_WIDTH,
                      settings.ROOM_DEPTH, 90))
    walls[-1].rect.topleft = (settings.ROOM_WIDTH // 4 - settings.WALLS_WIDTH,
                              settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # side left corner
    walls.append(
        Wall(settings.ROOM_WIDTH // 2 + settings.WALLS_WIDTH * 2, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].rect.topleft = (
        settings.ROOM_WIDTH // 4 - settings.WALLS_WIDTH, settings.ROOM_HEIGHT - settings.WALLS_WIDTH)  # mid bottom
    walls.append(Wall(settings.ROOM_HEIGHT - settings.ROOM_HEIGHT // 1.3 + settings.WALLS_WIDTH, settings.WALLS_WIDTH,
                      settings.ROOM_DEPTH, 270))
    walls[-1].rect.topleft = (settings.ROOM_WIDTH - settings.ROOM_WIDTH // 4,
                              settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # side right corner
    walls.append(Wall(settings.ROOM_WIDTH // 4, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].rect.topleft = (settings.ROOM_WIDTH - settings.ROOM_WIDTH // 4,
                              settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # bottom left corner
    return walls


def generate_room():
    walls = generate_walls_rectangle()
    # walls = generate_walls_with_corners()

    # corners = []
    # # Find angle from wall to each wall with get_angle_to_sprite
    # # TODO: Угол - это все углы от 90 до 179, на стыке двух стен
    # for wall in walls:
    #     for wall2 in walls:
    #         if wall != wall2 and wall.rect.colliderect(wall2.rect):
    #             angle = wall.get_angle_to_sprite(wall2)
    #             corners.append(angle)
    #             print(angle, wall, wall2)


    # # Find angle from wall to each wall with get_angle_to_sprite
    # for i in range(len(walls)):
    #     angle = walls[(i+1) % len(walls)].get_angle_to_sprite(walls[i])
    #     angles.append(angle)
    #     print(angle, (i+1) % len(walls), i)
    # wall.get_angle_to_sprite()

    # generate door 90cm
    door = generate_object_in_walls(Door, 90, walls)

    # generate window # 170cm
    window = generate_object_in_walls(Window, 170, walls)
    while window.rect.colliderect(door.rect):  # if intersects with door  # TODO: make right angle intersection
        window = generate_object_in_walls(Window, 170, walls)

    return [door, window] + walls


def generate_furniture():
    furniture_obj = list()

    # ==================== FURNITURE ====================
    # args: width, height, depth, angle, x, y, z

    # generate tv # 65"(144x81x15cm)    55"(122x69x10cm)
    furniture_obj.append(TV(144, 15, 81, 0, 650, 15, 120))

    """
    # generate sofa # 180x86x87
    furniture_obj.append(Sofa(180, 86, 87, 180, 650, 273))

    # generate coffee table # 120x70x43
    furniture_obj.append(CoffeeTable(120, 70, 43, 0, 650, 163))

    # generate armchair # 91x84x87
    furniture_obj.append(Armchair(91, 84, 87, 135, 264, 527))

    # generate big carpet # 128x88
    furniture_obj.append(CarpetBig(230, 160, 0, 180, 650, 180))

    # generate Computer table # 136x60
    furniture_obj.append(ComputerTable(136, 60, 180, 150, 560))

    # generate Computer Chair # 43x42
    furniture_obj.append(ComputerChair(48, 52, 0, 150, 504))

    # generate nightstand # 41x41
    furniture_obj.append(Nightstand(60, 50, 180, 770, 273))

    # generate dresser # 110x50
    furniture_obj.append(Dresser(106, 60, 90, 40, 218))

    # # generate floor lamp # 30x30
    furniture_obj.append(FloorLamp(40, 40, 180, 540, 273))
    furniture_obj.append(FloorLamp(40, 40, 180, 540, 273))

    # generate table# 170x65
    furniture_obj.append(Table(160, 90, 0, 420, 450))

    # # generate chair # 43x42
    furniture_obj.append(KitchenChair(48, 52, 0, 420, 365))
    furniture_obj.append(KitchenChair(48, 52, 180, 420, 540))
    furniture_obj.append(KitchenChair(48, 52, 270, 536, 450))
    """  # """

    # # Test object without image
    # furniture_obj.append(SpriteObject(135, 30, 45))

    return furniture_obj


def set_room_params(room_size_sqm):
    w, h = generate_room_parameters(room_size_sqm)
    settings.ROOM_WIDTH, settings.ROOM_HEIGHT = max([w, h]), min([w, h])
    settings.ROOM_SQUARE = round((settings.ROOM_WIDTH * settings.ROOM_HEIGHT) / 10000, 2)
    settings.ROOM_WIDTH += settings.WALLS_WIDTH * 2
    settings.ROOM_HEIGHT += settings.WALLS_WIDTH * 2
    settings.X_OFFSET = (settings.SCREEN_WIDTH - settings.ROOM_WIDTH) // 2
    settings.Y_OFFSET = (settings.SCREEN_HEIGHT - settings.ROOM_HEIGHT) // 2


def main():
    # debug_func()
    # room_size_sqm = float(input("Enter room size in sq meters: "))
    room_size_sqm = 24.9

    for amount in range(settings.MAIN_ITERATIONS):
        set_room_params(room_size_sqm)

        start_time = time()

        # furniture_obj = generate_furniture()
        # furniture_obj = room_rules.get_bedroom_guest_17__24_9m()
        furniture_obj = room_rules.get_bedroom_master_17__24_9m()

        rooms_obj = generate_room()
        settings.ALL_OBJECTS = rooms_obj
        settings.FURNITURE_OBJECTS = list()
        settings.SPRITE_ORDER = list()

        for i, f_obj in enumerate(furniture_obj):
            obj_str = f" Now running: '{f_obj.__class__.__name__.upper()}' ({i+1}/{len(furniture_obj)}) "
            print(obj_str.center(50, "="))
            settings.ALL_OBJECTS.append(f_obj)
            settings.FURNITURE_OBJECTS.append(f_obj)
            settings.CURRENT_GA_SPRITE = f_obj

            if settings.START_GA:
                solution = start_ga()

                if f_obj.optional:
                    if solution.score > settings.STOP_WHEN_REACHED:
                        settings.ALL_OBJECTS.remove(f_obj)
                        settings.FURNITURE_OBJECTS.remove(f_obj)
                        print("\nCan't place this optional obj:", f_obj, "\n")
                    else:  # all is OK
                        set_sprite_values(solution.variable)
                        print("\nSuccessfully placed:", f_obj, "\n")
                else:
                    set_sprite_values(solution.variable)
                    print("\nSuccessfully placed:", f_obj, "\n")

            #  ########draw_loop(f"Want to replace smth? {amount + 1}/{settings.MAIN_ITERATIONS}")

        print(f"Time takes to generate {len(furniture_obj)} objects: {time() - start_time:.2f} seconds")
        draw_loop(f"Done! {amount+1}/{settings.MAIN_ITERATIONS}")

    # # get different solutions
    # various_indexes = get_various_indexes(solution)
    #
    # print("\nvarious_solutions:", len(various_indexes))
    #
    # for i in various_indexes[:20]:
    # # for i in range(len(solution.last_generation.variables))[:10]:
    #     frame_name = f"{i+1}/{len(solution.last_generation.variables)} \tfitness: {solution.last_generation.scores[i]}"
    #
    #     set_sprite_values(solution.last_generation.variables[i])
    #     # main loop
    #     draw_loop(frame_name)


if __name__ == '__main__':
    main()
