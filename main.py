from random import uniform
from time import time

import furniture_sprites
import room_rules
import settings
from GA_furniture import start_ga, set_sprite_values
from draw_engine import draw_loop
from room_parts import Wall, Door, Window


def generate_room_parameters(room_size, accuracy=2):
    sqr_root_size = room_size ** 0.5
    min_size_percentage = 0.50
    min_size = sqr_root_size / (2 - min_size_percentage)  # from half sqr root to 0.2 of a half of a root
    max_size = sqr_root_size  # to sqr root of a room size
    width = round(uniform(min_size, max_size), accuracy)
    height = round(room_size / width, accuracy)
    width, height = max(width, height), min(width, height)
    return int(width * 100), int(height * 100)  # , depth=250?


def generate_object_in_walls(obj, width, depth, walls, objects_in_walls, z=0, restart=0):
    from random import choice, randrange
    from pygame.math import Vector2

    if restart > 100:
        raise Exception("Can't fit this object in the room.", obj)

    wall = choice(walls)
    fit_in_wall = wall.width - width - wall.height * 2
    if fit_in_wall <= 0:  # It can't fit in the wall
        return generate_object_in_walls(obj, width, depth, walls, objects_in_walls, z, restart + 1)

    side = wall.convert_self_side("midleft")
    random_pos = Vector2(randrange(fit_in_wall) + width // 2 + wall.height, 0).rotate(-wall.angle)
    new_obj = obj(width, wall.height, depth, wall.angle, side.x + random_pos.x, side.y + random_pos.y, z)

    for old_obj in objects_in_walls:
        # TODO: make right angle intersection (example angle 45)
        if new_obj.rect.colliderect(old_obj.rect.inflate(30, 30)):  # if intersects with obj+30
            return generate_object_in_walls(obj, width, depth, walls, objects_in_walls, z, restart + 1)

    return new_obj


def generate_walls_rectangle():
    walls = list()
    # generate 4 walls in rectangular form
    walls.append(Wall(settings.ROOM_HEIGHT, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 90))
    walls[-1].set_pos(0, 0)  # left
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 0))
    walls[-1].set_pos(0, 0)  # top
    walls.append(Wall(settings.ROOM_HEIGHT, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 270))
    walls[-1].set_pos(settings.ROOM_WIDTH - settings.WALLS_WIDTH, 0)  # right
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].set_pos(0, settings.ROOM_HEIGHT - settings.WALLS_WIDTH)  # bottom
    return walls


def generate_walls_with_corners():
    walls = list()
    # generate 4 walls in rectangular form with 2 bottom corners
    walls.append(Wall(settings.ROOM_HEIGHT // 1.3, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 90))
    walls[-1].set_pos(0, 0)  # left
    walls.append(Wall(settings.ROOM_WIDTH, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 0))
    walls[-1].set_pos(0, 0)  # top
    walls.append(Wall(settings.ROOM_HEIGHT // 1.3, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 270))
    walls[-1].set_pos(settings.ROOM_WIDTH - settings.WALLS_WIDTH, 0)  # right
    walls.append(Wall(settings.ROOM_WIDTH // 4, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].set_pos(0, settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # bottom left corner
    walls.append(Wall(settings.ROOM_HEIGHT - settings.ROOM_HEIGHT // 1.3 + settings.WALLS_WIDTH, settings.WALLS_WIDTH,
                      settings.ROOM_DEPTH, 90))
    walls[-1].set_pos(settings.ROOM_WIDTH // 4 - settings.WALLS_WIDTH,
                      settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # side left corner
    walls.append(
        Wall(settings.ROOM_WIDTH // 2 + settings.WALLS_WIDTH * 2, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].set_pos(
        settings.ROOM_WIDTH // 4 - settings.WALLS_WIDTH, settings.ROOM_HEIGHT - settings.WALLS_WIDTH)  # mid bottom
    walls.append(Wall(settings.ROOM_HEIGHT - settings.ROOM_HEIGHT // 1.3 + settings.WALLS_WIDTH, settings.WALLS_WIDTH,
                      settings.ROOM_DEPTH, 270))
    walls[-1].set_pos(settings.ROOM_WIDTH - settings.ROOM_WIDTH // 4,
                      settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # side right corner
    walls.append(Wall(settings.ROOM_WIDTH // 4, settings.WALLS_WIDTH, settings.ROOM_DEPTH, 180))
    walls[-1].set_pos(settings.ROOM_WIDTH - settings.ROOM_WIDTH // 4,
                      settings.ROOM_HEIGHT // 1.3 - settings.WALLS_WIDTH)  # bottom left corner
    return walls


def generate_room():
    walls = generate_walls_rectangle()
    # walls = generate_walls_with_corners()
    objects_in_walls = list()

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

    # generate door 80x200
    objects_in_walls.append(generate_object_in_walls(Door, 80, 200, walls, objects_in_walls))

    # generate window 170x145
    objects_in_walls.append(generate_object_in_walls(Window, 170, 145, walls, objects_in_walls, 75))

    return walls + objects_in_walls


def set_room_params(room_size_sqm):
    if settings.GENERATE_RANDOM_ROOM:
        settings.ROOM_WIDTH, settings.ROOM_HEIGHT = generate_room_parameters(room_size_sqm)
    else:
        settings.ROOM_WIDTH, settings.ROOM_HEIGHT = settings.ROOM_WIDTH, settings.ROOM_HEIGHT

    settings.ROOM_SQUARE = round((settings.ROOM_WIDTH * settings.ROOM_HEIGHT) / 10000, 2)
    settings.ROOM_WIDTH += settings.WALLS_WIDTH * 2
    settings.ROOM_HEIGHT += settings.WALLS_WIDTH * 2
    settings.X_OFFSET = (settings.SCREEN_WIDTH / settings.SCALE - settings.ROOM_WIDTH) // 2
    settings.Y_OFFSET = (settings.SCREEN_HEIGHT / settings.SCALE - settings.ROOM_HEIGHT) // 2


def main():
    # room_size_sqm = float(input("Enter room size in sq meters: "))
    room_size_sqm = 32  # 24.9  # 32

    for amount in range(settings.MAIN_ITERATIONS):
        set_room_params(room_size_sqm)

        rooms_obj = generate_room()
        settings.ALL_OBJECTS = rooms_obj
        settings.SPRITE_ORDER = list()

        # furniture_obj = room_rules.get_bedroom_guest_17__24_9m()
        # furniture_obj = room_rules.get_bedroom_master_17__24_9m()
        # furniture_obj = room_rules.living_room_9__15m()
        # furniture_obj = room_rules.all_furniture()
        furniture_obj = room_rules.living_room_BIG()
        # furniture_obj = [furniture_sprites.DoubleBed(x=200, y=200), furniture_sprites.Nightstand(x=500, y=200)]

        start_time = time()
        for i, f_obj in enumerate(furniture_obj):
            if settings.START_GA:
                print(f" Now running: '{f_obj.name.upper()}' ({i + 1}/{len(furniture_obj)}) ".center(60, "="))
            settings.ALL_OBJECTS.append(f_obj)
            settings.CURRENT_GA_SPRITE = f_obj

            if settings.START_GA:
                solution = start_ga()

                if f_obj.optional:
                    if solution.score > settings.STOP_WHEN_REACHED:
                        settings.ALL_OBJECTS.remove(f_obj)
                        print("\nCan't place this optional obj:", f_obj, "\n")
                    else:  # all is OK
                        set_sprite_values(solution.variable)
                        print("\nSuccessfully placed:", f_obj, "\n")
                else:
                    set_sprite_values(solution.variable)
                    print("\nSuccessfully placed:", f_obj, "\n")

            #  ########draw_loop(f"Want to replace smth? {amount + 1}/{settings.MAIN_ITERATIONS}")

        print(f"Time takes to generate {len(furniture_obj)} objects: {time() - start_time:.2f} seconds")
        draw_loop(f"Done! {amount + 1}/{settings.MAIN_ITERATIONS}")

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
