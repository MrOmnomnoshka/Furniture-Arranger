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
    mouse_diff = np.array((0, 0))  # for sprite moving with mouse

    rules = dict()  # dict with rules from one object to another

    fitness_surface = None  # Surface to render fitness
    # recalc_draw_rect_class = False

    def __init__(self, width=50, height=50, depth=50, angle=0, x=0, y=0, z=0, optional=False):  # TODO: need xyz here or just in 'set_pos'?
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

        self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, -self.angle)
        tl_scale_offset = (np.array(self.rect.topleft) + np.array(
            (settings.X_OFFSET, settings.Y_OFFSET))) * settings.SCALE
        self.rect_to_draw = self.image_to_draw.get_rect(topleft=tl_scale_offset)

        # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

        self.update()

        # Scaled version of images, to draw it while zooming
        # self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, self.angle)
        # tl_scale_offset = (np.array(self.rect.topleft) + np.array((settings.X_OFFSET, settings.Y_OFFSET))) * settings.SCALE
        # self.rect_to_draw = self.image_to_draw.get_rect(topleft=tl_scale_offset)

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
                                                                        # TODO: or ret fit to move to the nearest wall?
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
        self.update_image()  # TODO: remove it from here?

    def update_image(self):
        if self.is_sprite_changed() or self.is_scale_changed() or self.is_offset_changed():
            self.get_rotated_rect()  # update rect angle
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

            # Update old image and rect to draw
            # TODO: !!!!calc this only if pygame exists!!!!  (пробовал через общую переменную класса, но слишком сложно получалось, упростить или переписать функции вызова отрисвки и решить что где рисем (каждое н, в мэйни и т.д))
            # if SpriteObject.recalc_draw_rect_class or settings.INIT_EVERY_N:
            if settings.INIT_EVERY_N:
                if self.is_scale_changed():# or self.is_sprite_changed():
                    # print("update image")
                    self.old_scale = settings.SCALE
                    self.scaled_original_image = self.load_and_scale_image(settings.SCALE)
                    self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, -self.angle)

                if self.is_sprite_changed():
                    self.image_to_draw = pygame.transform.rotate(self.scaled_original_image, -self.angle)

                tl_scale_offset = (np.array(self.rect.topleft) + np.array(
                    (settings.X_OFFSET, settings.Y_OFFSET))) * settings.SCALE
                self.rect_to_draw = self.image_to_draw.get_rect(topleft=tl_scale_offset)

                self.old_x_offset, self.old_y_offset = settings.X_OFFSET, settings.Y_OFFSET

            self.old_angle = self.angle

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
        # rotated_rect_copy = [np.array(point) for point in rotated_rect]
        rotated_rect_copy = rotated_rect.copy()

        # Append imaginary dist to all sides
        for side in self.offsets:
            if self.offsets[side] > 0:  # if distance greater than 0 move side to 'imaginary' side
                side_vec = convert_side(side, rotated_rect_copy)
                new_other_side_vec = move_to_distance_by_side(self.offsets[side], side, self, side_vec)

                for i, side_point in enumerate(side_vec):  # TODO: mb rethink that
                    for j, point in enumerate(rotated_rect_copy):
                        if all(point == side_point):
                            rotated_rect_copy[j] = new_other_side_vec[i]
                            break
        self.offset_rotated_rect = tuple(rotated_rect_copy)

    def get_dist_to_range(self, desired_sign, desired_dist, other_sides, other_side, self_side, related, sprite, dist_end):
        max_dist = max(settings.ROOM_WIDTH, settings.ROOM_HEIGHT) * 2
        self_vec = self.convert_self_side(self_side)
        # FIND DIST TO LINE
        other_vec = sprite.convert_self_side(other_side)

        top = other_vec[::-1]
        bottom = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
        left, right = (bottom[1], top[0]), (top[1], bottom[0])

        # if self_vec is line make it the nearest point on that line to top side
        closest = find_closest_point(self_vec, top) if type(self_vec) == tuple else self_vec
        dist = find_shortest_distance(closest, top)[0]

        left_related, right_related = find_related_sides(related, other_side, other_sides)
        to_the_left_of_border = ccw(closest, *left) or left_related
        to_the_right_of_border = ccw(closest, *right) or right_related
        under_top = ccw(closest, *top)

        if to_the_left_of_border and to_the_right_of_border and under_top:  # get left right sides under top
            dist_diff = desired_dist - dist
            if desired_sign == ">":
                dist_to_range = max(0, dist_diff)
            elif desired_sign == "<":
                dist_to_range = max(0, -dist_diff)
            elif desired_sign == "=":
                dist_to_range = abs(dist_diff)
            else:  # if desired_sign == "[]":
                dist_to_range = max(0, dist_diff, dist - dist_end)  # [] is '> dist_diff' and '< -dist_end'

        elif not under_top:  # if above top
            if desired_sign == ">":
                lines_to_follow = (bottom,)
            elif desired_sign == "<":
                lines_to_follow = (top,)
            elif desired_sign == "=":
                lines_to_follow = (bottom,)
            else:  # if desired_sign == "[]":
                lines_to_follow = [bottom]  # always follow bottom line
                if left_related:  # if left side is related follow left line
                    left_seg = tuple(move_to_distance_by_side(d, get_side_related(other_side, 1), sprite,
                                                              top[0]) for d in (dist_end, desired_dist))
                    lines_to_follow.append(left_seg)
                if right_related:  # if right side is related follow right line
                    right_seg = tuple(move_to_distance_by_side(d, get_side_related(other_side, -1), sprite,
                                                               top[1]) for d in (dist_end, desired_dist))
                    lines_to_follow.append(right_seg)

            dist_to_range = min((find_shortest_distance(closest, line)[0] for line in lines_to_follow))
        else:  # under top, but not to the left and right
            if desired_sign == ">":
                # Move all sides to max_dist (except top side, it moves to desired_dist)
                top = move_to_distance_by_side(desired_dist, other_side, sprite, top)
                bottom = move_to_distance_by_side(max_dist, other_side, sprite, bottom)
                left, right = (bottom[1], top[0]), (top[1], bottom[0])
                lines_to_follow = (left, right, top, bottom)
            elif desired_sign == "<":
                lines_to_follow = (left, right, top, bottom)
            elif desired_sign == "=":
                lines_to_follow = (bottom,)
            else:  # if desired_sign == "[]":
                seg_bottom = move_to_distance_by_side(dist_end, other_side, sprite, top)
                left_seg, right_seg = (bottom[1], seg_bottom[0]), (seg_bottom[1], bottom[0])
                lines_to_follow = (bottom, right_seg, left_seg)

            dist_to_range = min((find_shortest_distance(closest, line)[0] for line in lines_to_follow))

        return dist_to_range

    def calc_mle_rule(self, desired_sign, desired_dist, any_any, self_sides, other_sides, related, sprite, dist_end=None):
        min_dists = list()
        all_dists = list()

        # FAST way to calc 'any' to 'any' distance
        if any_any and related:
            dist = min(sprite.calc_nearest_distance(self)[0], self.calc_nearest_distance(sprite)[0])
            dist_diff = desired_dist - dist
            if desired_sign == ">":
                return (max(0, dist_diff),)
            elif desired_sign == "<":
                return (max(0, -dist_diff),)
            elif desired_sign == "=":
                return (abs(dist_diff),)
            elif desired_sign == "[]":
                return (max(0, dist_diff, dist - dist_end),)

        max_dist = max(settings.ROOM_WIDTH, settings.ROOM_HEIGHT) * 2
        for self_side in self_sides:
            self_vec = self.convert_self_side(self_side)
            for other_side in other_sides:
                # FIND DIST TO LINE
                other_vec = sprite.convert_self_side(other_side)

                if type(other_vec) == tuple:  # other line to self point/line
                    top = other_vec[::-1]
                    # if self_vec is line make it the nearest point on that line to top side
                    closest = find_closest_point(self_vec, top) if type(self_vec) == tuple else self_vec
                    dist = find_shortest_distance(closest, top)[0]
                    all_dists.append((dist, other_side, self_side))  # find min dist and count it later

                else:  # other point to self point/line
                    other_vec_moved = move_to_distance_by_side(desired_dist, other_side, sprite, other_vec)
                    if desired_sign in "><":
                        if desired_sign == ">":
                            line_to_follow = move_to_distance_by_side(max_dist, other_side, sprite,
                                                                      other_vec_moved), other_vec_moved
                        else:  # if desired_sign == "<":
                            line_to_follow = other_vec, other_vec_moved

                        dist_to_range = find_shortest_distance(self_vec, line_to_follow)[0]
                    elif desired_sign == "=":
                        dist_to_range = find_shortest_distance(self_vec, other_vec_moved)[0]
                    else:  # if desired_sign == "[]":
                        end_point = move_to_distance_by_side(dist_end, other_side, sprite, other_vec)
                        dist_to_range = find_shortest_distance(self_vec, (other_vec_moved, end_point))[0]

                    # At the end add it to min_dists
                    # "dist_to_range" - distance to the nearest point on imaginary line
                    min_dists.append(dist_to_range)

        if all_dists:  # it was line to self point/line
            # find min pair of dist and count it
            min_dist = min(all_dists, key=lambda x: x[0])[0]
            min_indices = (i for i, (d, _, _) in enumerate(all_dists) if d == min_dist)
            for i in min_indices:  # count all min dists (in case of "left, right, TOP", only TOP is correct to count)
                _, other_side, self_side = all_dists[i]
                dist_to_range = self.get_dist_to_range(desired_sign, desired_dist, other_sides, other_side, self_side,
                                                       related, sprite, dist_end)
                min_dists.append(dist_to_range)

        return min_dists

    def rule_distance_to_sprite(self, sprite, rule):
        if "sides" not in rule:
            return 0

        if len(rule["sides"]) == 3:
            self_sides, other_sides, desired_dist_str = rule["sides"]
            related = False
        else:  # len == 4
            self_sides, other_sides, desired_dist_str, related = rule["sides"]
            related = True if related else False  # TODO: add dict or smth to make it OK

        any_any = True if self_sides == "any" and other_sides == "any" else False
        self_sides, other_sides = tuple(translate_sides(self_sides)), tuple(translate_sides(other_sides))
        min_dists = []

        if type(desired_dist_str) == str:  # ">50" or "<50"
            interval = re.findall(r"\[.*\]", desired_dist_str)
            mle = re.findall(r"[><=]", desired_dist_str)
            if interval:
                d_from, d_to = map(int, interval[0][1:-1].split("-"))
                min_dists = self.calc_mle_rule("[]", d_from, any_any, self_sides, other_sides, related, sprite, d_to)
            elif mle:
                desired_sign = mle[0]
                desired_dist = int(desired_dist_str[1:])
                min_dists = self.calc_mle_rule(desired_sign, desired_dist, any_any, self_sides, other_sides, related,
                                               sprite)
            elif desired_dist_str == "any":
                min_dists.append(0)
            else:
                raise Exception("TODO: add other variants of dist rules!")

        else:  # type(int) - "50"
            desired_dist = desired_dist_str
            min_dists = self.calc_mle_rule("=", desired_dist, any_any, self_sides, other_sides, related, sprite)

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
            real_view = rotate_vec_np(np.array((0, 1), float), -self.angle)
            desired_view = unit_vector(np.array(sprite.rect.center) - np.array(self.rect.center))
            ang_dif = np.rad2deg(np.arccos(np.clip(np.dot(real_view, desired_view), -1.0, 1.0)))
            angle_diff = abs(convert_360_to_180(ang_dif))
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
        # pos_off = [p - o for p, o in zip(mouse_pos, (settings.X_OFFSET, settings.Y_OFFSET))]
        pos_off = mouse_pos - (settings.X_OFFSET, settings.Y_OFFSET)
        return point_in_rect(pos_off, self.get_rotated_rect())

    def get_rotated_rect(self):
        center = self.rect.center
        # Check if smth changed or it's first time
        if self.rotated_rect is None or self.is_sprite_changed() or self.is_scale_changed():
            self.old_center = center
            rect = self.original_image.get_rect(center=center)
            # rect = self.original_image.get_rect(topleft=self.rect.topleft)
            pts_np = np.array((rect.topleft, rect.topright, rect.bottomright, rect.bottomleft), float)
            rect_angle = np.array(tuple(rotate_vec_np(p - center, -self.angle) + center for p in pts_np))
            self.rotated_rect = rect_angle  # Replace it with new one

            # change offset rotated rect
            self.calc_offset_rotated_rect(rect_angle)

        return self.rotated_rect

    def is_sprite_changed(self):
        return self.old_center != self.rect.center or self.old_angle != self.angle

    def is_scale_changed(self):
        return self.old_scale != settings.SCALE

    def is_offset_changed(self):
        return (self.old_x_offset, self.old_y_offset) != (settings.X_OFFSET, settings.Y_OFFSET)

    def is_in_sprite(self, other_sprite):
        self_in_other = False
        other_rect = other_sprite.get_rotated_rect()
        for pnt in self.get_rotated_rect():
            if point_in_rect(pnt, other_rect):
                self_in_other = True
                break
        return self_in_other

    def __str__(self):
        # !! Внимание, параметры которые нужны, а не который показанны (xyz*10, зеркалю угол) !!
        # Если нужно зеркалить угол: {(360 - self.angle) % 360}
        return f"{self.__class__.__name__} - angle: {self.angle}, " \
               f"x: {self.rect.centerx*10}, y: {self.rect.centery*-10}, z: {self.z*10}"

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def coordinates(self):
        return f"{self.rect.centerx*10}, {self.rect.centery*-10}, {self.z*10}"

    @property
    def parameters(self):
        return f"{self.width*10}x{self.height*10}x{self.depth*10}"
