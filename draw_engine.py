import pygame

import settings
from colors import *
from furniture import Furniture
from room_parts import Wall, Door, Window
from GA_furniture import set_sprite_values
import translate
from math_2d import *
from controls import event_handling, get_mouse_offset


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


def add_offset_to_position(position):
    new_position = []
    if type(position) == np.ndarray:
        new_position = (position + np.array((settings.X_OFFSET, settings.Y_OFFSET))) * settings.SCALE
    else:  # tuple/list of pos  # TODO: uniform this case as: "if type == tuple"
        for pos in position:
            new_pos = (pos + np.array((settings.X_OFFSET, settings.Y_OFFSET))) * settings.SCALE
            new_position.append(new_pos)
    return new_position


def get_fitness_surface(sprite):
    start_pos = sprite.rect.center  # Save sprite start position
    precision = settings.FG_PRECISION
    surf = pygame.Surface((settings.ROOM_WIDTH, settings.ROOM_HEIGHT), pygame.SRCALPHA)
    half_precision = precision // 2

    for y in range(0, settings.ROOM_HEIGHT, precision):
        for x in range(0, settings.ROOM_WIDTH, precision):
            sprite.rect.center = (x, y)
            fit = sprite.get_fitness()
            color = (0, 0, 0, 0)

            # # Only Green
            # if fit == 0:
            #     color = green_a

            # # Only Green and Red
            # if fit == 0:
            #     color = green_a
            # elif fit >= 100_000:
            #     color = red_a

            # green->red (X2) (STRONG GREEN)
            max_fit = min(255, fit*2)
            if max_fit == 0:
                color = (0, 255, 0, 255)
            else:
                color = (max_fit, 255-max_fit, 0, 100)

            # # green->yellow->red
            # max_fit = min(510, fit)
            # if max_fit <= 255:
            #     color = (max_fit, 255, 0, 100)
            # else:  # > 255
            #     color = (255, 510 - max_fit, 0, 100)

            # Draw on that surface
            surf.fill(color, (x - half_precision, y - half_precision, precision, precision))
    sprite.rect.center = start_pos  # Load back sprite to its start position
    return surf


def draw_offset(sprite, screen, draw_width):
    offset_other_rect = sprite.offset_rotated_rect
    rect = sprite.get_rotated_rect()
    if offset_other_rect and not all(all(offset_other_rect[i] == rect[i]) for i in range(len(rect))):
        offset_other_rect = add_offset_to_position(offset_other_rect)
        pygame.draw.lines(screen, blue, True, offset_other_rect, draw_width)


def draw_all(draw_bg=True):
    font, all_sprites, clock, screen = settings.FONT, settings.ALL_OBJECTS, settings.CLOCK, settings.SCREEN
    lang = getattr(translate, settings.LANGUAGE)

    if draw_bg:
        screen.fill(background)

    if settings.FITNESS_GRADIENT_MODE and Furniture.active:
        if not Furniture.active.fitness_surface or settings.FG_MODE_RECALC:
            Furniture.active.fitness_surface = get_fitness_surface(Furniture.active)
            settings.FG_MODE_RECALC = False

        surf_scaled = pygame.transform.scale(Furniture.active.fitness_surface,
                                             (settings.ROOM_WIDTH * settings.SCALE,
                                              settings.ROOM_HEIGHT * settings.SCALE))
        screen.blit(surf_scaled, add_offset_to_position(np.array((0, 0))))

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
            arrow_vec = rotate_vec_np(np.array((0, 50), float), -sprite.angle)
            lines = add_offset_to_position([np.array(sprite.rect.center), sprite.rect.center + arrow_vec])
            pygame.draw.lines(screen, red, True, lines, draw_width)

            # Draw BLUE border of sprite offsets (if offset is not equal to sprite rect) ((and no active Furniture))
            if not Furniture.active:
                draw_offset(sprite, screen, draw_width)

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

        if settings.DEBUG_POINTS_TO_DRAW:
            for point in settings.DEBUG_POINTS_TO_DRAW:
                pos = add_offset_to_position(point)
                pygame.draw.circle(screen, red, pos, draw_width*2)

    # ======= Left up corner info =======
    # Show FPS
    fps = font.render(f"{lang['fps']}: {int(clock.get_fps())}", True, magenta)
    screen.blit(fps, (10, 10))

    # Show scaled mouse pos
    if settings.DEBUG:
        pos_scaled = ','.join([str(int(p)) for p in get_mouse_offset()])
        mouse_pos = font.render(f"{lang['mouse_pos']}: {pos_scaled}", True, magenta)
        screen.blit(mouse_pos, (10, 40))

    if Furniture.active:
        sprite = Furniture.active

        # Show active sprite name
        active = font.render(f"Active: {sprite.name}", True, active_sprite)
        screen.blit(active, (10, 70))

        # Show active sprite x,y,z
        xyz = font.render(f"   XYZ: {sprite.coordinates}", True, active_sprite)
        screen.blit(xyz, (10, 100))

        # Show active sprite parameters
        params = font.render(f"   Params: {sprite.parameters}", True, active_sprite)
        screen.blit(params, (10, 130))

        # Show active sprite angle
        angle = font.render(f"   Angle: {sprite.angle}", True, active_sprite)
        screen.blit(angle, (10, 160))

        # Show active sprite fitness
        sprite_fitness = sprite.get_fitness()
        fitness = font.render(f"   Fitness: {sprite_fitness}", True, active_sprite)
        screen.blit(fitness, (10, 190))

        # Draw BLUE border of sprite offsets (if offset is not equal to sprite rect)
        for other_sprite in settings.ALL_OBJECTS:
            draw_offset(other_sprite, screen, draw_width)

        # Draw 'active_sprite' color rect around active sprite
        pts = add_offset_to_position(Furniture.active.get_rotated_rect())
        pygame.draw.lines(screen, active_sprite, True, pts, draw_width*2)

        if sprite_fitness > 100_000:
            # draw RED alpha rectangle around the image
            surf = pygame.Surface(sprite.scaled_original_image.get_size(), pygame.SRCALPHA)
            surf.fill(red + (100,))  # notice the alpha value in the color
            screen.blit(pygame.transform.rotate(surf, -sprite.angle), sprite.rect_to_draw.topleft)
        elif sprite_fitness <= settings.STOP_WHEN_REACHED:
            # draw GREEN alpha rectangle around the image
            surf = pygame.Surface(sprite.scaled_original_image.get_size(), pygame.SRCALPHA)
            surf.fill(green + (100,))  # notice the alpha value in the color
            screen.blit(pygame.transform.rotate(surf, -sprite.angle), sprite.rect_to_draw.topleft)

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
            settings.SCREEN.fill(background)

        # =======  Left down corner info =======
        # show current generation
        generation = settings.FONT.render("Generation: " + str(data["current_generation"]), True, magenta)
        settings.SCREEN.blit(generation, (10, settings.SCREEN_HEIGHT - 30))

        # show last data value
        last_data = settings.FONT.render("Fitness: " + str(data["report_list"][-1]), True, magenta)
        settings.SCREEN.blit(last_data, (10, settings.SCREEN_HEIGHT - 60))

        # show sprite name
        sprite_name = settings.FONT.render("Object: " + settings.CURRENT_GA_SPRITE.name, True, magenta)
        settings.SCREEN.blit(sprite_name, (10, settings.SCREEN_HEIGHT - 90))

        # Sprites drawing
        if settings.DRAW_EVERY_OBJ:
            for obj_data in data.last_generation.variables:
                set_sprite_values(obj_data)
                settings.CURRENT_GA_SPRITE.draw(settings.SCREEN)
        else:
            set_sprite_values(data.last_generation.variables[0])

        draw_all(False)
        settings.SCREEN.fill(background)
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
