import settings
from colors import rand_color
import pygame
from math_2d import *
import re


class SpriteObject(pygame.sprite.Sprite):
    old_scale = settings.SCALE
    old_x_offset, old_y_offset = settings.X_OFFSET, settings.Y_OFFSET
    old_center, old_angle = (0, 0), 0

    # For self rotated rect
    rotated_rect = None
    offset_rotated_rect = None

    original_image = None  # Every sprite has its own image
    mouse_diff = Vector2(0, 0)  # for sprite moving with mouse

    rules = dict()  # dict with rules from one object to another

    fitness_surface = None  # Surface to render fitness

    def __init__(self, width=50, height=50, depth=50, angle=0, x=0, y=0, z=0,
                 optional=False):  # TODO: need xyz here or just in 'set_pos'?
        pygame.sprite.Sprite.__init__(self)

        # self.rules = dict()  # dict with rules for each sprite
        # if not hasattr(self, "rules"):
        #     self.rules = dict()

        self.offsets = {"top": 0, "bottom": 0, "left": 0, "right": 0}  # offsets - dict with offsets for each side
        self.set_unique_params(width, height, depth)  # set rules, offsets and (width, height, depth) parameters

        if not hasattr(self, "z"):
            self.z = self.depth // 2 + z

        self.angle = angle
        self.x, self.y = x, y
        self.optional = optional

        self.original_image = self.load_and_scale_image()
        self.image = self.original_image
        self.scaled_original_image = self.load_and_scale_image(settings.SCALE)
        self.rect = self.image.get_rect(center=(x, y))
        # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

        self.update()

        # Scaled version of images, to draw it while zooming
        self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, self.angle)
        tl_scale_offset = (Vector2(self.rect.topleft) + Vector2(settings.X_OFFSET, settings.Y_OFFSET)) * settings.SCALE
        self.rect_to_draw = self.image_to_draw.get_rect(topleft=tl_scale_offset)

        self.rect_rotated_rules = list()

    def set_unique_params(self, width, height, depth):
        # if hasattr(self, "rules_to_this"):
        #     self.rules.update(self.rules_to_this)
        if hasattr(self, "offsets_to_this"):
            self.offsets.update(self.offsets_to_this)

        for param in ("width", "height", "depth"):
            if not hasattr(self, param):
                setattr(self, param, locals()[param])
            else:
                if locals()[param] != 50 and locals()[param] != getattr(self, param):
                    setattr(self, param, locals()[param])

    def update(self):
        # self.rect.clamp_ip(0, 0, settings.ROOM_WIDTH, settings.ROOM_HEIGHT)  # TODO:if room not a rect - need clamp?
        self.update_image()

    def draw(self, display_surface):
        display_surface.blit(self.image_to_draw, self.rect_to_draw)

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self.rect.topleft = (x, y)
        self.update()

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        # print(self.angle)
        self.update_image()

    def update_image(self):
        if self.is_sprite_changed() or self.is_scale_changed() or self.is_offset_changed():
            self.get_rotated_rect()  # update rect angle
            self.old_angle = self.angle
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

            if self.is_scale_changed():
                self.old_scale = settings.SCALE
                self.scaled_original_image = self.load_and_scale_image(settings.SCALE)

            self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, self.angle)
            tl_scale_offset = (Vector2(self.rect.topleft) + Vector2(settings.X_OFFSET,
                                                                    settings.Y_OFFSET)) * settings.SCALE
            self.rect_to_draw = self.image_to_draw.get_rect(topleft=tl_scale_offset)

            self.old_x_offset, self.old_y_offset = settings.X_OFFSET, settings.Y_OFFSET

    def load_and_scale_image(self, scale=1):
        if hasattr(self, "image_path"):  # Has Image
            original_image = pygame.image.load(self.image_path)
        else:  # No Image. just color
            if not hasattr(self, "color"):  # Hasn't color
                self.color = rand_color()
            original_image = pygame.Surface([self.width, self.height],
                                            pygame.SRCALPHA)  # SRCALPHA is for alpha background (for rect rotation)
            original_image.fill(self.color)

        return pygame.transform.scale(original_image, (self.width * scale, self.height * scale))

    def convert_self_side(self, side):
        rect = self.get_rotated_rect()  # [topleft, topright, bottomright, bottomleft]
        return convert_side(side, rect)

    # def __del__(self):
    #     print(f"Deleted {self.__class__.__name__}")

    def calc_offset_rotated_rect(self, rotated_rect):
        # Copy of rotated rect to make some changes in it
        rotated_rect_copy = [Vector2(point) for point in rotated_rect]

        # Append imaginary dist to all sides
        for side in self.offsets:
            if self.offsets[side] > 0:  # if distance greater than 0 move side to 'imaginary' side
                side_vec = convert_side(side, rotated_rect_copy)
                new_other_side_vec = move_to_distance_by_side(self.offsets[side], side, self, side_vec)

                for i, side_point in enumerate(side_vec):
                    for j, point in enumerate(rotated_rect_copy):
                        if point == side_point:
                            rotated_rect_copy[j] = new_other_side_vec[i]
                            break
        self.offset_rotated_rect = rotated_rect_copy

    def rule_distance_to_sprite(self, sprite, rule):
        if "sides" not in rule:
            return 0

        if len(rule["sides"]) == 3:
            self_sides, other_sides, desired_dist_str = rule["sides"]
            related = False
        else:  # len == 4
            self_sides, other_sides, desired_dist_str, related = rule["sides"]

        any_any = True if self_sides == "any" and other_sides == "any" else False
        self_sides, other_sides = translate_sides(self_sides), translate_sides(other_sides)
        min_dists = []

        if type(desired_dist_str) == str:  # ">50" or "<50"
            # check if <> sign in str
            if re.search(r"[<>]", desired_dist_str):
                desired_sign = re.search(r"[<>]", desired_dist_str).group()
                desired_dist = int(desired_dist_str[1:])
                max_dist = max(settings.ROOM_WIDTH, settings.ROOM_HEIGHT) * 2

                # FAST way to calc 'any' to 'any' distance
                if any_any:
                    dist = min(sprite.calc_nearest_distance(self)[0], self.calc_nearest_distance(sprite)[0])
                    sign = 1 if desired_sign == ">" else -1
                    return max(0, (desired_dist - dist) * sign)

                for self_side in self_sides:
                    self_vec = self.convert_self_side(self_side)
                    for other_side in other_sides:
                        # FIND DIST TO LINE
                        other_vec = sprite.convert_self_side(other_side)

                        if type(other_vec) == tuple:  # other line to self point/line
                            top = other_vec[::-1]
                            bottom = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                            left = bottom[1], top[0]
                            right = top[1], bottom[0]

                            left_r, right_r = find_related_sides(related, other_side, other_sides)
                            closest = find_closest_point(self_vec, top) if type(self_vec) == tuple else self_vec
                            if (ccw(closest, *left) or left_r) and (ccw(closest, *right) or right_r) and ccw(closest, *top):
                                dist = find_shortest_distance(self_vec, top)[0]
                                if desired_sign == ">":
                                    dist_to_range = max(0, desired_dist - dist)
                                else:
                                    dist_to_range = max(0, dist - desired_dist)
                            else:
                                if desired_sign == ">":
                                    # Move all sides to max_dist (except top side, it moves to desired_dist)
                                    top = move_to_distance_by_side(desired_dist, other_side, sprite, top)
                                    bottom = move_to_distance_by_side(max_dist, other_side, sprite, bottom)
                                    left = bottom[1], top[0]
                                    right = top[1], bottom[0]

                                # "dist_to_range" - distance to the nearest point at any side of imaginary rect
                                dist_to_range = min(find_shortest_distance(self_vec, left)[0],
                                                    find_shortest_distance(self_vec, right)[0],
                                                    find_shortest_distance(self_vec, top)[0],
                                                    find_shortest_distance(self_vec, bottom)[0])

                        else:  # other point to self point/line
                            other_vec_moved = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                            if desired_sign == ">":
                                line_to_follow = move_to_distance_by_side(max_dist, other_side, sprite, other_vec_moved), other_vec_moved
                            else:  # if desired_sign == "<":
                                line_to_follow = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec), other_vec

                            # "dist_to_range" - distance to the nearest point to imaginary line
                            dist_to_range = find_shortest_distance(self_vec, line_to_follow)[0]

                        # At the end add it to min_dists
                        min_dists.append(dist_to_range)

            elif desired_dist_str == "any":
                min_dists.append(0)
            else:
                raise Exception("TODO: add other variants of dist rules!")

        else:  # type(int) - "50"
            desired_dist = desired_dist_str

            # FAST way to calc 'any' to 'any' distance
            # TODO: all code from above is the same, combine and refactor
            if any_any:
                dist = min(sprite.calc_nearest_distance(self)[0], self.calc_nearest_distance(sprite)[0])
                return abs(desired_dist - dist)

            for self_side in self_sides:
                self_vec = self.convert_self_side(self_side)
                for other_side in other_sides:
                    other_vec = sprite.convert_self_side(other_side)

                    if type(other_vec) == tuple:  # other line to self point/line
                        top = other_vec[::-1]
                        bottom = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                        left = bottom[1], top[0]
                        right = top[1], bottom[0]

                        left_r, right_r = find_related_sides(related, other_side, other_sides)
                        closest = find_closest_point(self_vec, top) if type(self_vec) == tuple else self_vec
                        if (ccw(closest, *left) or left_r) and (ccw(closest, *right) or right_r) and ccw(closest, *top):
                            min_dists.append(abs(find_shortest_distance(self_vec, other_vec)[0] - desired_dist))
                        else:
                            min_dists.append(find_shortest_distance(closest, bottom)[0])

                    else:  # other point to self point/line
                        # other_vec_moved = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                        point_to = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                        min_dists.append(find_shortest_distance(self_vec, point_to)[0])

        return min(min_dists)  # Closest dist from side to side (or point)

    def calc_nearest_distance(self, sprite):
        a, b, c, d = self.get_rotated_rect()

        results = []
        for p in sprite.get_rotated_rect():
            results.append([point_to_line(p, a, b), point_to_line(p, b, c),
                            point_to_line(p, c, d), point_to_line(p, d, a)])

        # Find min dist in all 4 points, and min dist in this point to line
        return min([min(res, key=lambda x: x[0]) for res in results], key=lambda x: x[0])

    def get_angle_to_sprite(self, sprite, rule):
        if "angle" not in rule:
            return 0

        current_diff = convert_360_to_180(self.angle - sprite.angle)  # from -180 to 180

        angle_desired = rule["angle"]
        if angle_desired == "any":
            angle_diff = 0
        elif angle_desired == "center":
            real_view = Vector2(0, 1).rotate(-self.angle)
            desired_view = (Vector2(sprite.rect.center) - Vector2(self.rect.center)).normalize()
            angle_diff = abs(convert_360_to_180(real_view.angle_to(desired_view)))
        elif angle_desired == "perpendicular":
            angle_diff = abs(90 - abs(current_diff))
        elif angle_desired == "parallel":
            angle_diff = abs(current_diff)
            if angle_diff > 90:
                angle_diff = (90 - angle_diff % 90) % 90  # TODO: mb refactor with '%' usage
        else:
            angle_diff_360 = abs(angle_desired - current_diff)
            angle_diff = abs(180 - (180 + angle_diff_360) % 360)

        return angle_diff

    def check_mouse_over_mask(self, mouse_pos):
        # IF MASK NEEDED - TURN ON
        pos_in_mask = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y
        return self.rect.collidepoint(*mouse_pos) and self.mask.get_at(pos_in_mask)

    def check_mouse_over_full_size(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def check_mouse_over_rotated(self, mouse_pos):
        pos_off = [p - o for p, o in zip(mouse_pos, (settings.X_OFFSET, settings.Y_OFFSET))]
        return point_in_rect(pos_off, self.get_rotated_rect())

    def get_rotated_rect(self):
        center = Vector2(self.rect.center)
        # Check if smth changed or it's first time
        if self.is_sprite_changed() or not self.rotated_rect or self.is_scale_changed():
            self.old_center = center
            rect = self.original_image.get_rect(center=center)
            # rect = self.original_image.get_rect(topleft=self.rect.topleft)
            pts = (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft)
            rect_angle = [(Vector2(p) - center).rotate(-self.angle) + center for p in pts]
            self.rotated_rect = rect_angle  # Replace it with new one

            # change offset rotated rect
            self.calc_offset_rotated_rect(rect_angle)  # Comment this - it will work faster

        return self.rotated_rect

    def is_sprite_changed(self):
        return self.old_center != self.rect.center or self.old_angle != self.angle

    def is_scale_changed(self):
        return self.old_scale != settings.SCALE

    def is_offset_changed(self):
        return self.old_x_offset, self.old_y_offset != settings.X_OFFSET, settings.Y_OFFSET

    def is_in_sprite(self, other_sprite):
        self_in_other = False
        other_rect = other_sprite.get_rotated_rect()
        for pnt in self.get_rotated_rect():
            if point_in_rect(pnt, other_rect):
                self_in_other = True
                break
        return self_in_other

    def __str__(self):
        return f"{self.__class__.__name__} - angle: {self.angle}" \
               f", x: {self.rect.centerx}, y: {self.rect.centery}, z: {self.z}"

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def coordinates(self):
        return f"{self.rect.centerx}, {self.rect.centery}, {self.z}"

    @property
    def parameters(self):
        return f"{self.width}x{self.height}x{self.depth}"
