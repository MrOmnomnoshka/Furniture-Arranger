import pygame

# import room_parts
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

    # create a font object.
    font = pygame.font.Font('freesansbold.ttf', 26)

    # clock object
    clock = pygame.time.Clock()

    #  reset all settings data
    settings.FONT, settings.CLOCK, settings.SCREEN = font, clock, screen


def print_furniture_sprites_info():
    for sprite in settings.FURNITURE_OBJECTS:
        print(sprite)


def change_furniture_attr(attr):
    sprite = get_hovered_sprite()
    if sprite:  # if sprite exists
        if getattr(Furniture, attr) == sprite:  # It was me?
            setattr(Furniture, attr, None)  # Turn me off
        else:  # It is not me
            setattr(Furniture, attr, sprite)  # Make this sprite active


def get_hovered_sprite_fitness():
    sprite = Furniture.active if Furniture.active else get_hovered_sprite()

    if sprite:
        print(sprite, "fitness:", sprite.get_fitness())
    return None


def get_hovered_sprite():
    hovered_sprites = list()
    for sprite in settings.FURNITURE_OBJECTS:
        if sprite.check_mouse_over_rotated(Vector2(pygame.mouse.get_pos()) / settings.SCALE):
            hovered_sprites.append(sprite)
            # return sprite
    if hovered_sprites:
        return sorted(hovered_sprites, key=lambda s: s.z)[-1]  # return the highest z-index sprite
    return None


def program_exit():
    # deactivates the pygame library
    pygame.quit()
    # exit python
    quit()


def get_mouse_offset():
    return [(p / settings.SCALE - o) for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]


def change_offset_and_scale(scroll):
    old_scale = settings.SCALE
    settings.SCALE = max(0.2, round(settings.SCALE + scroll / 20, 3))

    old_topleft_x = (settings.SCREEN_WIDTH / old_scale - settings.ROOM_WIDTH) // 2
    old_topleft_y = (settings.SCREEN_HEIGHT / old_scale - settings.ROOM_HEIGHT) // 2
    diff_x = settings.X_OFFSET - old_topleft_x
    diff_y = settings.Y_OFFSET - old_topleft_y

    topleft_x = (settings.SCREEN_WIDTH / settings.SCALE - settings.ROOM_WIDTH) // 2
    topleft_y = (settings.SCREEN_HEIGHT / settings.SCALE - settings.ROOM_HEIGHT) // 2

    # can remove extra parameters - but it is not clear what is happening
    # x_test = ((settings.SCREEN_WIDTH * (old_scale - settings.SCALE)) / (settings.SCALE * old_scale)) // 2 + settings.X_OFFSET

    # TODO: fix zooming to mouse
    # screen_center_x = settings.SCREEN_WIDTH // 2
    # screen_center_y = settings.SCREEN_HEIGHT // 2
    # settings.X_OFFSET = ((screen_center_x - pygame.mouse.get_pos()[0]) / settings.SCALE)# + settings.SCREEN_WIDTH
    # settings.Y_OFFSET = ((screen_center_y - pygame.mouse.get_pos()[1]) / settings.SCALE)# + settings.SCREEN_HEIGHT
    # settings.X_OFFSET = ((pygame.mouse.get_pos()[0]) / settings.SCALE) - (screen_center_x/2) / settings.SCALE
    # settings.Y_OFFSET = ((pygame.mouse.get_pos()[1]) / settings.SCALE) - (screen_center_y/2) / settings.SCALE
    settings.X_OFFSET = topleft_x + diff_x## - (pygame.mouse.get_pos()[0] / settings.SCALE - screen_center_x)
    settings.Y_OFFSET = topleft_y + diff_y## - (pygame.mouse.get_pos()[1] / settings.SCALE - screen_center_y)


def event_handling():
    move_step = 25 // settings.SCALE  # TODO: screen movement from mouse
    done = False

    if Furniture.active:
        # mouse key down
        mouse_keys = pygame.mouse.get_pressed()
        if mouse_keys[0]:  # lmb
            Furniture.active.rotate(1)
        elif mouse_keys[2]:  # rmb
            Furniture.active.rotate(-1)

        Furniture.active.rect.center = get_mouse_offset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            program_exit()
        elif event.type == pygame.MOUSEWHEEL:
            change_offset_and_scale(event.y)
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
                print("s debug", settings.S_DEBUG)
            elif event.key == pygame.K_n:
                settings.DEBUG_EVERY_N = not settings.DEBUG_EVERY_N
            elif event.key == pygame.K_SPACE:
                if Furniture.active:
                    Furniture.active = None
                else:
                    change_furniture_attr("active")
            elif event.key == pygame.K_l:
                change_furniture_attr("show_distances")
            elif event.key == pygame.K_LEFT:
                settings.X_OFFSET -= move_step
            elif event.key == pygame.K_RIGHT:
                settings.X_OFFSET += move_step
            elif event.key == pygame.K_UP:
                settings.Y_OFFSET -= move_step
            elif event.key == pygame.K_DOWN:
                settings.Y_OFFSET += move_step
            elif event.key == pygame.K_r:
                settings.SCALE = 1
                for sprite in settings.FURNITURE_OBJECTS:
                    sprite.rotate(-sprite.angle)
                settings.X_OFFSET = (settings.SCREEN_WIDTH - settings.ROOM_WIDTH) // 2
                settings.Y_OFFSET = (settings.SCREEN_HEIGHT - settings.ROOM_HEIGHT) // 2
    return done


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

    if draw_bg:
        screen.fill(white_dark)

    if not settings.SPRITE_ORDER or len(settings.SPRITE_ORDER) != len(all_sprites):
        # sort sprites by z value
        settings.SPRITE_ORDER = sorted(all_sprites, key=lambda s: s.z)

    for sprite in settings.SPRITE_ORDER:
        sprite.update()
        sprite.draw(screen)

    # # solve all collisions
    # for sprite in settings.ALL_OBJECTS:
    #     if isinstance(sprite, Furniture):
    #         for other_sprite in settings.ALL_OBJECTS:
    #             sprite.solve_collisions(other_sprite)

    if settings.DEBUG:
        draw_width = max(1, round(2 * settings.SCALE))
        for sprite in all_sprites:
            # # draw RED rectangle around the image
            # rect = add_offset_to_position(Vector2(sprite.rect.topleft)), sprite.image.get_size()
            # pygame.draw.rect(screen, red, rect, draw_width)

            # draw GREEN rectangle around rotated image
            pts = add_offset_to_position(sprite.get_rect_angle())
            pygame.draw.lines(screen, green, True, pts, draw_width)

            # Draw RED sprite view arrow
            arrow_vec = Vector2(0, 50).rotate(-sprite.angle)
            lines = add_offset_to_position([Vector2(sprite.rect.center), sprite.rect.center + arrow_vec])
            pygame.draw.lines(screen, red, True, lines, draw_width)

            # Draw BLUE border of distances ('>' '<') rules objects
            for other_sprite in sprite.rect_rotated_rules_dict:
                other_rect = add_offset_to_position(sprite.rect_rotated_rules_dict[other_sprite])
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
    fps = font.render(f"FPS: {int(clock.get_fps())}", True, magenta)
    screen.blit(fps, (10, 10))

    # Show mouse pos
    pos_scaled = [int(p) for p in get_mouse_offset()]
    mouse_pos = font.render(f"Mouse x,y: {str(pos_scaled)}", True, magenta)
    screen.blit(mouse_pos, (10, 40))

    # Show scale
    if settings.SCALE != 1:
        scale = font.render(f"Scale: {settings.SCALE}", True, magenta)
        screen.blit(scale, (10, 70))

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

    # Draws the surface object to the screen.
    pygame.display.update()


def draw_every_generation(data):
    if settings.DEBUG_EVERY_N:
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

        from GA_furniture import set_sprite_values
        for obj_data in data.last_generation.variables:
            set_sprite_values(obj_data)
            settings.CURRENT_GA_SPRITE.draw(settings.SCREEN)

        # settings.SCREEN.blit(pygame.transform.scale(
        #     settings.DISPLAY_SURFACE,  # Screen with camera data
        #     (settings.SCREEN_WIDTH * settings.SCALE, settings.SCREEN_HEIGHT * settings.SCALE)),  # Zoom screen
        #     (settings.X_OFFSET, settings.Y_OFFSET))  # Move screen

        draw_all(False)
        settings.SCREEN.fill(white_dark)

        settings.CLOCK.tick(settings.FPS_IN_EVERY_N)

        # draw_all()  # JUST fill white color?
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
