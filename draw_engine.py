import pygame

import room_parts
import settings
from pygame.math import Vector2
from colors import *
from furniture import Furniture


def init_pygame(frame_name):
    # initialize the pygame module
    pygame.init()
    pygame.font.init()

    # set caption
    pygame.display.set_caption(f"Furniture Arranger | {frame_name}")

    # create the display surface object
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # create screen surface
    display_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # create a font object.
    font = pygame.font.Font('freesansbold.ttf', 26)

    # clock object
    clock = pygame.time.Clock()

    #  reset all settings data
    settings.DISPLAY_SURFACE, settings.FONT, settings.CLOCK, settings.SCREEN = display_surface, font, clock, screen


def print_furniture_sprites_info():
    for sprite in settings.FURNITURE_OBJECTS:
        print(sprite)


def change_hovered_sprite_attr(attr):
    sprite = get_hovered_sprite()
    if sprite:
        # Turn OFF all previous
        for other_sprite in settings.FURNITURE_OBJECTS:
            if other_sprite != sprite:
                setattr(other_sprite, attr, False)

        # Toggle that sprite
        setattr(sprite, attr, not getattr(sprite, attr))


def get_hovered_sprite_fitness():
    sprite = get_hovered_sprite()
    if sprite:
        print(sprite, "fitness:", sprite.get_fitness())
        print("=" * 20)
    return None


def get_hovered_sprite():
    for sprite in settings.FURNITURE_OBJECTS:
        if sprite.check_mouse_over_rotated():
            return sprite
    return None


def program_exit():
    # deactivates the pygame library
    pygame.quit()
    # exit python
    quit()


def event_handling():
    move_step = 40 * settings.SCALE  # TODO: screen movement from mouse
    done = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # program_exit()
            done = True

        # elif event.type == pygame.MOUSEWHEEL:
        #     settings.SCALE = max(0.1, settings.SCALE + event.y / 20)  # TODO: fix zooming (if zoom even needed...)
        elif event.type == pygame.FINGERMOTION:  # FOR TouchScreens (Android OS)
            settings.DEBUG = not settings.DEBUG

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and (event.mod & pygame.KMOD_SHIFT):
                program_exit()  # Exit for program
            elif event.key == pygame.K_ESCAPE:
                done = True  # Exit for current iteration
            elif event.key == pygame.K_i:
                print_furniture_sprites_info()
            elif event.key == pygame.K_d:
                settings.DEBUG = not settings.DEBUG
            elif event.key == pygame.K_f:
                get_hovered_sprite_fitness()
            elif event.key == pygame.K_s:
                settings.S_DEBUG = not settings.S_DEBUG
            elif event.key == pygame.K_SPACE:
                change_hovered_sprite_attr("active")
            elif event.key == pygame.K_l:
                change_hovered_sprite_attr("show_distances")
            elif event.key == pygame.K_LEFT:
                settings.X_OFFSET -= move_step
            elif event.key == pygame.K_RIGHT:
                settings.X_OFFSET += move_step
            elif event.key == pygame.K_UP:
                settings.Y_OFFSET -= move_step
            elif event.key == pygame.K_DOWN:
                settings.Y_OFFSET += move_step
            elif event.key == pygame.K_r:
                for sprite in settings.FURNITURE_OBJECTS:
                    sprite.angle = 0
                    sprite.update_image()
    return done


def draw_all():
    font, camera_display, all_sprites, clock, screen = settings.FONT, settings.DISPLAY_SURFACE, settings.ALL_OBJECTS, \
                                                       settings.CLOCK, settings.SCREEN

    screen.fill(white_dark)
    # screen.fill(white)

    camera_display.fill(white_dark)

    for sprite in all_sprites[::-1]:  # draw from back to front
        sprite.update()
        sprite.draw(camera_display)

    # # solve all collisions
    # for sprite in settings.ALL_OBJECTS:
    #     if isinstance(sprite, Furniture):
    #         for other_sprite in settings.ALL_OBJECTS:
    #             sprite.solve_collisions(other_sprite)

    if settings.DEBUG:
        for sprite in all_sprites:
            # # draw RED rectangle around the image
            # pygame.draw.rect(camera_display, red, (*sprite.rect.topleft, *sprite.image.get_size()),
            #                  int(2 * settings.SCALE))

            # draw GREEN rectangle around rotated image
            pts = sprite.get_rect_angle()
            pygame.draw.lines(camera_display, green, True, pts, int(2 * settings.SCALE))

            # Draw sprite view arrow
            arrow_vec = Vector2(0, 50).rotate(-sprite.angle)
            pygame.draw.line(camera_display, red, sprite.rect.center, sprite.rect.center + arrow_vec, 2)

            # Draw border of distances ('>' '<') rules objects
            for other_sprite in sprite.rect_rotated_rules_dict:
                other_rect = sprite.rect_rotated_rules_dict[other_sprite]
                pygame.draw.lines(settings.DISPLAY_SURFACE, blue, True, other_rect, 4)

            # Draw distance lines from current sprite to other sprites
            if isinstance(sprite, Furniture) and sprite.show_distances:
                for other_sprite in all_sprites:
                    if sprite != other_sprite:
                        # sprite.solve_collisions(other_sprite)

                        # DRAW DISTANCES TO OTHER SPRITES
                        distances = [sprite.calc_nearest_distance(other_sprite),
                                     other_sprite.calc_nearest_distance(sprite)]

                        dist, nearest, pnt = min(distances, key=lambda x: x[0])

                        pygame.draw.circle(camera_display, red, pnt, 4)
                        pygame.draw.circle(camera_display, blue, nearest, 4)
                        pygame.draw.line(camera_display, black, pnt, nearest, 2)

                        text = font.render(str(round(dist)), False, blue)
                        diff = nearest - pnt
                        camera_display.blit(text, diff / 2 + pnt)

                # # FOR DEBUG DELETE THIS LATER
                # pygame.display.update()
                # DELETE LINE

        # # Draw room width and height rect
        # pygame.draw.rect(camera_display, dark_yellow, (0, 0, settings.ROOM_LENGTH, settings.ROOM_WIDTH), 2)

    screen.blit(pygame.transform.scale(
        camera_display,  # Screen with camera data
        (settings.SCREEN_WIDTH * settings.SCALE, settings.SCREEN_HEIGHT * settings.SCALE)),  # Zoom screen
        (settings.X_OFFSET, settings.Y_OFFSET))  # Move screen

    # ======= Left up corner info =======
    # Show FPS
    fps = font.render(str(int(clock.get_fps())), True, magenta)
    screen.blit(fps, (2, 2))

    # Show mouse pos
    pos_off = [p - o for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]
    mouse_pos = font.render(str(pos_off), True, magenta)
    screen.blit(mouse_pos, (0, 30))

    # =======  Right up corner info =======
    # show room width
    room_width = font.render(str(settings.ROOM_WIDTH), True, magenta)
    screen.blit(room_width, (settings.SCREEN_WIDTH - 80, 2))

    # show room height
    room_height = font.render(str(settings.ROOM_HEIGHT), True, magenta)
    screen.blit(room_height, (settings.SCREEN_WIDTH - 80, 30))

    # Draws the surface object to the screen.
    pygame.display.update()


def draw_loop(frame_name):
    init_pygame(frame_name)

    done = False
    while not done:
        done = event_handling()

        draw_all()

        # clock tick
        settings.CLOCK.tick(60)
    pygame.quit()


def debug_func():
    # ==================== DEBUG ====================
    init_pygame("DEBUG")

    # # find TV in sprites
    # for sprite in settings.ALL_SPRITES:
    #     if isinstance(sprite, TV):
    #         tv_obj = sprite

    # main loop
    done = False
    while not done:
        done = event_handling()

        draw_all()

        # settings.ALL_SPRITES.update()

        # for sprite in settings.ALL_SPRITES:
        #     draw_all(font, display_surface, settings.ALL_SPRITES, clock)
        #
        #     if settings.COLLISIONS:
        #         tv_obj.solve_collisions(sprite)#, draw_all, font, display_surface, settings.ALL_SPRITES, clock)
        #
        #     draw_all(font, display_surface, settings.ALL_SPRITES, clock)

        # clock tick
        settings.CLOCK.tick(60)

    pygame.quit()
    # exit()
    # ==================== DEBUG ====================
