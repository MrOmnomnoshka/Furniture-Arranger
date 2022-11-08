import pygame

import settings
from pygame.math import Vector2
from colors import *
from furniture import Furniture
from room_parts import Wall, Door, Window
from GA_furniture import set_sprite_values
import translate


def init_pygame(frame_name):
    # initialize the pygame module
    pygame.init()
    pygame.font.init()

    # set caption
    pygame.display.set_caption(f"Furniture Arranger | {frame_name}")

    # create the display surface object
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # create a font object.
    font = pygame.font.Font('freesansbold.ttf', 26)

    # clock object
    clock = pygame.time.Clock()

    #  reset all settings data
    settings.FONT, settings.CLOCK, settings.SCREEN = font, clock, screen


def print_furniture_sprites_info():
    print(" All furniture info ".center(60, "="))

    for sprite in settings.ALL_OBJECTS:
        if isinstance(sprite, Furniture):
            print(sprite, "fitness:", sprite.get_fitness())


def change_furniture_attr(attr):
    sprite = get_hovered_furniture()
    if sprite:  # if sprite exists
        if getattr(Furniture, attr) == sprite:  # It was me?
            setattr(Furniture, attr, None)  # Turn me off
        else:  # It is not me
            setattr(Furniture, attr, sprite)  # Make this sprite active
    else:  # Just in some free space
        setattr(Furniture, attr, None)  # Turn this attribute off


def get_hovered_sprite_fitness():
    sprite = Furniture.active if Furniture.active else get_hovered_furniture()
    if sprite:
        print(sprite, "fitness:", sprite.get_fitness())
    return None


def get_hovered_furniture():
    hovered_sprites = list()
    mouse_scaled = Vector2(pygame.mouse.get_pos()) / settings.SCALE
    for sprite in settings.ALL_OBJECTS:
        if isinstance(sprite, Furniture):
            if sprite.check_mouse_over_rotated(mouse_scaled):
                hovered_sprites.append(sprite)
    if hovered_sprites:
        return sorted(hovered_sprites, key=lambda s: s.z + s.depth)[-1]  # return the highest z-index sprite
    return None


def program_exit():
    # deactivates the pygame library
    pygame.quit()
    # exit python
    quit()


def get_mouse_offset():
    return [(p / settings.SCALE - o) for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]


def zoom_to_mouse(scroll, shift):
    old_scale = settings.SCALE
    step = 5 if shift else 20
    settings.SCALE = max(0.2, round(settings.SCALE + scroll / step, 3))

    mouse_pos = Vector2(pygame.mouse.get_pos())
    topleft = mouse_pos / settings.SCALE
    old_topleft = mouse_pos / old_scale
    difference = old_topleft - Vector2(settings.X_OFFSET, settings.Y_OFFSET)
    settings.X_OFFSET, settings.Y_OFFSET = topleft - difference


def event_handling():
    done = False

    # move_active_furniture()
    if not Furniture.active:
        move_screen()

    for event in pygame.event.get():
        shift_mod_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if event.type == pygame.QUIT:
            program_exit()
        elif event.type == pygame.MOUSEWHEEL:
            # rotate sprite
            if Furniture.active and get_hovered_furniture():
                rotate_step = 15 if shift_mod_pressed else 1
                Furniture.active.rotate(rotate_step * event.y)
            # camera zoom to mouse
            else:
                zoom_to_mouse(event.y, shift_mod_pressed)
        # ==== LMB DOWN ==== #
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            sprite = get_hovered_furniture()
            if sprite:
                # change it is difference to mouse
                sprite.mouse_diff = Vector2(get_mouse_offset()) - Vector2(sprite.rect.center)
                settings.MOUSE_MOVING_SPRITE = sprite
        # ==== LMB UP ==== #
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            settings.MOUSE_MOVING_SPRITE = None
        elif pygame.mouse.get_pressed()[0] and shift_mod_pressed:  # lmb + shift
            if event.type == pygame.MOUSEMOTION:
                settings.X_OFFSET += event.rel[0] / settings.SCALE
                settings.Y_OFFSET += event.rel[1] / settings.SCALE
        elif pygame.mouse.get_pressed()[0]:  # LMB pressed
            if settings.MOUSE_MOVING_SPRITE:
                a = [(p / settings.SCALE - o - d) for p, o, d in zip(pygame.mouse.get_pos(),
                                                                     (settings.X_OFFSET, settings.Y_OFFSET),
                                                                     settings.MOUSE_MOVING_SPRITE.mouse_diff)]
                settings.MOUSE_MOVING_SPRITE.rect.center = a
        elif event.type == pygame.FINGERMOTION:  # FOR TouchScreens (Android OS)
            settings.DEBUG = not settings.DEBUG
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and shift_mod_pressed:
                program_exit()  # Exit for program
            elif event.key == pygame.K_ESCAPE:
                done = True  # Exit for current iteration
            elif event.key == pygame.K_i:
                print_furniture_sprites_info()
            elif event.key == pygame.K_F1:
                settings.DEBUG = not settings.DEBUG
            elif event.key == pygame.K_f:
                get_hovered_sprite_fitness()
            elif event.key == pygame.K_h:
                settings.H_DEBUG = not settings.H_DEBUG
                print("'H' pressed for debug.", settings.H_DEBUG)
            elif event.key == pygame.K_n:
                settings.DRAW_EVERY_OBJ = not settings.DRAW_EVERY_OBJ
            elif event.key == pygame.K_p:
                settings.INIT_EVERY_N = not settings.INIT_EVERY_N
            elif event.key == pygame.K_SPACE:
                change_furniture_attr("active")
            elif event.key == pygame.K_l:
                change_furniture_attr("show_distances")
            elif event.key == pygame.K_r:
                settings.SCALE = 1
                settings.X_OFFSET = (settings.SCREEN_WIDTH - settings.ROOM_WIDTH) // 2
                settings.Y_OFFSET = (settings.SCREEN_HEIGHT - settings.ROOM_HEIGHT) // 2
            set_furniture_precisely(event.key)
    return done


def translate_2_to_1(value):
    """ [-2, -1, '1', 2] // 2 = [-1, -1, '0', 1]     || '1'-'0' - special if case """
    return value // 2 if value != 1 else 1


def move_screen():
    move_step = 5 / settings.SCALE
    keys = pygame.key.get_pressed()

    lr = translate_2_to_1(keys[pygame.K_LEFT] - keys[pygame.K_RIGHT] + keys[pygame.K_a] - keys[pygame.K_d])
    ud = translate_2_to_1(keys[pygame.K_UP] - keys[pygame.K_DOWN] + keys[pygame.K_w] - keys[pygame.K_s])

    settings.X_OFFSET += lr * move_step
    settings.Y_OFFSET += ud * move_step


def set_furniture_precisely(key):
    if Furniture.active:
        if key in (pygame.K_LEFT, pygame.K_a):
            Furniture.active.rect.x -= 1
        elif key in (pygame.K_RIGHT, pygame.K_d):
            Furniture.active.rect.x += 1
        elif key in (pygame.K_UP, pygame.K_w):
            Furniture.active.rect.y -= 1
        elif key in (pygame.K_DOWN, pygame.K_s):
            Furniture.active.rect.y += 1
        elif key == pygame.K_q:
            Furniture.active.rotate(1)
        elif key == pygame.K_e:
            Furniture.active.rotate(-1)


def add_offset_to_position(position):
    new_position = []
    if type(position) == Vector2:
        new_position = (position + Vector2(settings.X_OFFSET, settings.Y_OFFSET)) * settings.SCALE
    else:  # tuple/list of pos
        for pos in position:
            new_pos = (pos + Vector2(settings.X_OFFSET, settings.Y_OFFSET)) * settings.SCALE
            new_position.append(new_pos)
    return new_position


def draw_all(draw_bg=True):
    font, all_sprites, clock, screen = settings.FONT, settings.ALL_OBJECTS, settings.CLOCK, settings.SCREEN
    lang = getattr(translate, settings.LANGUAGE)

    if draw_bg:
        screen.fill(white_dark)

    if not settings.SPRITE_ORDER or len(settings.SPRITE_ORDER) != len(all_sprites):
        # sort sprites by z value
        z_sorted = sorted(all_sprites, key=lambda s: s.z + s.depth)  # z+depth//2 - is top of sprite, from top-view
        right_draw_sorted = sorted(z_sorted, key=lambda s: bool(type(s) in (Window, Door)))
        settings.SPRITE_ORDER = right_draw_sorted

    for sprite in settings.SPRITE_ORDER:
        sprite.update()
        sprite.draw(screen)

    # # solve all collisions
    # for sprite in settings.ALL_OBJECTS:
    #     if isinstance(sprite, Furniture):
    #         for other_sprite in settings.ALL_OBJECTS:
    #             sprite.solve_collisions(other_sprite)

    draw_width = max(1, round(2 * settings.SCALE))
    if settings.DEBUG:
        for sprite in all_sprites:

            # # Draw diff point from rect center to mouse diff
            # if isinstance(sprite, Furniture):
            #     pos = add_offset_to_position(sprite.rect.center + sprite.mouse_diff)
            #     pygame.draw.circle(screen, red, pos, draw_width*2)

            # # draw RED rectangle around the image
            # rect = add_offset_to_position(Vector2(sprite.rect.topleft)), sprite.image.get_size()
            # pygame.draw.rect(screen, red, rect, draw_width)

            # draw GREEN rectangle around rotated image
            pts = add_offset_to_position(sprite.get_rotated_rect())
            pygame.draw.lines(screen, green, True, pts, draw_width)

            # Draw RED sprite view arrow
            arrow_vec = Vector2(0, 50).rotate(-sprite.angle)
            lines = add_offset_to_position([Vector2(sprite.rect.center), sprite.rect.center + arrow_vec])
            pygame.draw.lines(screen, red, True, lines, draw_width)

            # Draw BLUE border of sprite offsets (if offset is not equal to sprite rect) ((and no active Furniture))
            if not Furniture.active:
                other_rect = sprite.offset_rotated_rect
                if other_rect and other_rect != sprite.get_rotated_rect():
                    other_rect = add_offset_to_position(other_rect)
                    pygame.draw.lines(screen, blue, True, other_rect, draw_width)

            # Draw BLUE distance lines from current sprite to other sprites
            if Furniture.show_distances == sprite:
                for other_sprite in all_sprites:
                    if sprite != other_sprite:
                        # DRAW DISTANCES TO OTHER SPRITES
                        distances = [sprite.calc_nearest_distance(other_sprite),
                                     other_sprite.calc_nearest_distance(sprite)]

                        dist, nearest, pnt = min(distances, key=lambda x: x[0])
                        nearest, pnt = add_offset_to_position(nearest), add_offset_to_position(pnt)

                        pygame.draw.line(screen, black, pnt, nearest, draw_width)
                        pygame.draw.circle(screen, red, pnt, draw_width)
                        pygame.draw.circle(screen, blue, nearest, draw_width)

                        text = font.render(str(round(dist)), False, blue)
                        screen.blit(text, (nearest - pnt) / 2 + pnt)

                # # FOR DEBUG DELETE THIS LATER
                # pygame.display.update()
                # DELETE LINE

        # # Draw yellow rect from room width and height
        # pos_rect = (add_offset_to_position(Vector2(0, 0)), Vector2(settings.ROOM_WIDTH, settings.ROOM_HEIGHT) * settings.SCALE)
        # pygame.draw.rect(screen, dark_yellow, pos_rect, draw_width)

    # ======= Left up corner info =======
    # Show FPS
    fps = font.render(f"{lang['fps']}: {int(clock.get_fps())}", True, magenta)
    screen.blit(fps, (10, 10))

    # Show scaled mouse pos
    pos_scaled = ','.join([str(int(p)) for p in get_mouse_offset()])
    mouse_pos = font.render(f"{lang['mouse_pos']}: {pos_scaled}", True, magenta)
    screen.blit(mouse_pos, (10, 40))

    if Furniture.active:
        sprite = Furniture.active

        # Show active sprite name
        active = font.render(f"Active: {sprite.name}", True, cyan)
        screen.blit(active, (10, 70))

        # Show active sprite x,y,z
        xyz = font.render(f"   XYZ: {sprite.coordinates}", True, cyan)
        screen.blit(xyz, (10, 100))

        # Show active sprite parameters
        params = font.render(f"   Params: {sprite.parameters}", True, cyan)
        screen.blit(params, (10, 130))

        # Show active sprite angle
        angle = font.render(f"   Angle: {sprite.angle}", True, cyan)
        screen.blit(angle, (10, 160))

        # Show active sprite fitness
        sprite_fitness = sprite.get_fitness()
        fitness = font.render(f"   Fitness: {sprite_fitness}", True, cyan)
        screen.blit(fitness, (10, 190))

        # Draw DARK BLUE border of distances ('>' '<') rules objects
        for other_sprite, other_rect in sprite.rect_rotated_rules:
            other_rect = add_offset_to_position(other_rect)
            pygame.draw.lines(screen, dark_blue, True, other_rect, draw_width)

        # Draw BLUE border of sprite offsets (if offset is not equal to sprite rect)
        for other_sprite in settings.ALL_OBJECTS:
            other_rect = other_sprite.offset_rotated_rect
            if other_rect and other_rect != other_sprite.get_rotated_rect():
                other_rect = add_offset_to_position(other_rect)
                pygame.draw.lines(screen, blue, True, other_rect, draw_width)

        # Draw cyan rect around active sprite
        pts = add_offset_to_position(Furniture.active.get_rotated_rect())
        pygame.draw.lines(screen, cyan, True, pts, draw_width*2)

        if sprite_fitness > 100_000:
            # draw RED alpha rectangle around the image
            s = pygame.Surface(sprite.scaled_original_image.get_size(), pygame.SRCALPHA)
            s.fill(red + (100,))  # notice the alpha value in the color
            screen.blit(pygame.transform.rotate(s, sprite.angle), sprite.rect_to_draw.topleft)
        elif sprite_fitness <= settings.STOP_WHEN_REACHED:
            # draw GREEN alpha rectangle around the image
            s = pygame.Surface(sprite.scaled_original_image.get_size(), pygame.SRCALPHA)
            s.fill(green + (100,))  # notice the alpha value in the color
            screen.blit(pygame.transform.rotate(s, sprite.angle), sprite.rect_to_draw.topleft)

    # =======  Right up corner info =======
    # show room width
    room_width = font.render("Room width: " + str(settings.ROOM_WIDTH - settings.WALLS_WIDTH * 2), True, magenta)
    screen.blit(room_width, (settings.SCREEN_WIDTH - room_width.get_rect().width - 10, 10))

    # show room height
    room_height = font.render("Room height: " + str(settings.ROOM_HEIGHT - settings.WALLS_WIDTH * 2), True, magenta)
    screen.blit(room_height, (settings.SCREEN_WIDTH - room_height.get_rect().width - 10, 40))

    # show room square
    room_square = font.render("Room square: " + str(settings.ROOM_SQUARE), True, magenta)
    screen.blit(room_square, (settings.SCREEN_WIDTH - room_square.get_rect().width - 10, 70))

    # =======  Right down corner info =======
    # Show scale
    scale = font.render(f"Scale: 1:{settings.SCALE}", True, magenta)
    screen.blit(scale, (settings.SCREEN_WIDTH - scale.get_rect().width - 10, settings.SCREEN_HEIGHT - 40))

    # Draws the surface object to the screen.
    pygame.display.update()


def draw_every_generation(data):
    if settings.INIT_EVERY_N:
        if not pygame.get_init():
            init_pygame("draw_every_generation")
            settings.SCREEN.fill(white_dark)

        # =======  Left down corner info =======
        # show current generation
        generation = settings.FONT.render("Generation: " + str(data["current_generation"]), True, magenta)
        settings.SCREEN.blit(generation, (10, settings.SCREEN_HEIGHT - 30))

        # show last data value
        last_data = settings.FONT.render("Fitness: " + str(data["report_list"][-1]), True, magenta)
        settings.SCREEN.blit(last_data, (10, settings.SCREEN_HEIGHT - 60))

        if settings.DRAW_EVERY_OBJ:
            for obj_data in data.last_generation.variables:
                set_sprite_values(obj_data)
                settings.CURRENT_GA_SPRITE.draw(settings.SCREEN)
        else:
            set_sprite_values(data.last_generation.variables[0])

        draw_all(False)
        settings.SCREEN.fill(white_dark)
        settings.CLOCK.tick(settings.FPS_IN_EVERY_N)

    if pygame.get_init():
        event_handling()

    return data


def draw_loop(frame_name):
    init_pygame(frame_name)

    done = False
    while not done:
        done = event_handling()

        draw_all()

        # clock tick
        settings.CLOCK.tick(60)
    pygame.quit()
