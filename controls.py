import settings
import pygame
import numpy as np
from furniture import Furniture


def event_handling():
    done = False
    if not Furniture.active:
        move_screen()

    for event in pygame.event.get():
        shift_mod_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if event.type == pygame.QUIT:
            program_exit()
        elif event.type == pygame.MOUSEWHEEL:
            # rotate sprite
            if Furniture.active and get_hovered_furniture() == Furniture.active:
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
                sprite.mouse_diff = np.array(get_mouse_offset()) - np.array(sprite.rect.center)
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
            if event.key == pygame.K_ESCAPE:
                if shift_mod_pressed:
                    program_exit()  # Exit for program
                else:
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
            elif event.key == pygame.K_g:
                settings.FITNESS_GRADIENT_MODE = not settings.FITNESS_GRADIENT_MODE
            elif event.key == pygame.K_b:
                if settings.FITNESS_GRADIENT_MODE:  # recalc only if gradient mode is on
                    settings.FG_MODE_RECALC = True
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
            set_furniture_precisely(event.key, shift_mod_pressed)

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


def program_exit():
    # deactivates the pygame library
    pygame.quit()
    # exit python
    quit()


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
    mouse_scaled = np.array(pygame.mouse.get_pos()) / settings.SCALE
    for sprite in settings.ALL_OBJECTS:
        if isinstance(sprite, Furniture):
            if sprite.check_mouse_over_rotated(mouse_scaled):
                hovered_sprites.append(sprite)
    if hovered_sprites:
        return sorted(hovered_sprites, key=lambda s: s.z + s.depth)[-1]  # return the highest z-index sprite
    return None


def zoom_to_mouse(scroll, shift):
    old_scale = settings.SCALE
    step = 5 if shift else 20
    settings.SCALE = max(0.2, round(settings.SCALE + scroll / step, 3))

    mouse_pos = np.array(pygame.mouse.get_pos())
    topleft = mouse_pos / settings.SCALE
    old_topleft = mouse_pos / old_scale
    difference = old_topleft - np.array((settings.X_OFFSET, settings.Y_OFFSET))
    settings.X_OFFSET, settings.Y_OFFSET = topleft - difference


def get_mouse_offset():
    return [(p / settings.SCALE - o) for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]


def set_furniture_precisely(key, shift):
    step = 15 if shift else 1
    if Furniture.active:
        if key in (pygame.K_LEFT, pygame.K_a):
            Furniture.active.rect.x -= step
        elif key in (pygame.K_RIGHT, pygame.K_d):
            Furniture.active.rect.x += step
        elif key in (pygame.K_UP, pygame.K_w):
            Furniture.active.rect.y -= step
        elif key in (pygame.K_DOWN, pygame.K_s):
            Furniture.active.rect.y += step
        elif key == pygame.K_q:
            Furniture.active.rotate(-step)
        elif key == pygame.K_e:
            Furniture.active.rotate(step)


def print_furniture_sprites_info():
    print(" All furniture info ".center(60, "="))

    for sprite in settings.ALL_OBJECTS:
        if isinstance(sprite, Furniture):
            print(sprite, "fitness:", sprite.get_fitness())
