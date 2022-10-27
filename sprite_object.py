import furniture_sprites
import settings
from colors import rand_color
import pygame
from pygame.math import Vector2
from math_2d import find_shortest_distance, point_to_line, translate_side, convert_side, move_side_to_distance, \
    get_rotated_rect_intersections
import re


class SpriteObject(pygame.sprite.Sprite):
    scale_old = settings.SCALE

    # For self rotated rect
    old_center, old_angle = (0, 0), 0
    old_rect_angle = None

    original_image = None  # Every sprite has its own image

    def __init__(self, width, height, depth, angle=0, x=0, y=0, z=0):  # TODO: need x y here or just in 'set_pos'?
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.depth = depth
        self.angle = angle

        self.reload_image()

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

        self.rect_rotated_rules_dict = dict()
        self.z = depth // 2 + z
        self.update()

    def update(self):
        self.update_image()
        self.rect.clamp_ip(0, 0, settings.ROOM_WIDTH, settings.ROOM_HEIGHT)

        if self.scale_old != settings.SCALE:
            self.original_image = pygame.transform.scale(self.original_image,
                                                         (self.width * settings.SCALE, self.height * settings.SCALE))
            self.reload_image()
            self.update_image()
            self.scale_old = settings.SCALE

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)

    # def set_pos(self, x, y, z=0):
    #     # self.rect.center = x, y
    #     self.rect.topleft = x, y
    #     self.z = z

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        self.update_image()

    def update_image(self):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        # self.mask = pygame.mask.from_surface(self.image)  # IF MASK NEEDED - TURN ON

    def reload_image(self):
        if hasattr(self, "image_path"):  # Has Image
            original_image = pygame.image.load(self.image_path)
        else:  # No Image. just color
            if not hasattr(self, "color"):  # Hasn't color
                self.color = rand_color()
            original_image = pygame.Surface([self.width * settings.SCALE, self.height * settings.SCALE])#, pygame.SRCALPHA)  #TODO: SRCALPHA NEEDED?
            original_image.fill(self.color)

        self.original_image = pygame.transform.scale(original_image,
                                                     (self.width * settings.SCALE, self.height * settings.SCALE))

    def convert_self_side(self, side):
        rect = self.get_rect_angle()  # [topleft, topright, bottomright, bottomleft]
        return convert_side(side, rect)

    # def __del__(self):
    #     print(f"Deleted {self.__class__.__name__}")

    def get_other_rect_from_rule(self, other_sprite, other_sides, desired_dist):
        if other_sprite not in self.rect_rotated_rules_dict:
            other_rect = [Vector2(point) for point in other_sprite.get_rect_angle()]

            # Append imaginary dist to all sides
            for other_side in other_sides:
                other_side_vec = convert_side(other_side, other_rect)
                if desired_dist > 0:  # if distance greater than 0 move side to 'imaginary' side
                    new_other_side_vec = move_side_to_distance(desired_dist, other_side, other_sprite, other_side_vec)

                    for i, side_point in enumerate(other_side_vec):
                        for j, point in enumerate(other_rect):
                            if point == side_point:
                                other_rect[j] = new_other_side_vec[i]
                                break
            self.rect_rotated_rules_dict.update({other_sprite: other_rect})
        return self.rect_rotated_rules_dict[other_sprite]

    def rule_distance_to_sprite(self, other_sprite, rule):
        self_sides, other_sides, desired_dist_str = rule["sides"]
        self_sides, other_sides = translate_side(self_sides), translate_side(other_sides)

        if type(desired_dist_str) == str:  # ">50" or "<50"
            desired_dist = int(re.findall(r"\d+", desired_dist_str)[0])  # 50
            desired_sign = desired_dist_str[0]  # >

            if desired_sign == ">":
                # if type(other_sprite) == furniture_sprites.FloorLamp:
                #     print("HERE")
                other_rect = self.get_other_rect_from_rule(other_sprite, other_sides, desired_dist)

                if get_rotated_rect_intersections(self.get_rect_angle(), other_rect):
                    return settings.COLLISION_PENALTY // 100  # penalty
                else:
                    return 0
            else:
                print("TODO: add < sign")
                return 0

            #     min_dists.append(find_shortest_distance(self.convert_side(self_side), other_side_vec)[0])
            # min_d = min(min_dists)  # Closest dist from side to side (or point)
            #
            # if desired_sign == ">":  # TODO: redo it
            #     if min_d < desired_dist:
            #         min_d = desired_dist - min_d
            #     else:
            #         min_d = 0
            # elif desired_sign == "<":
            #     if min_d > desired_dist:
            #         min_d = min_d - desired_dist
            #     else:
            #         min_d = 0
            #
            # return min_d

        else:  # type(int) - "50"
            desired_dist = desired_dist_str
            min_dists = []
            for self_side in self_sides:
                for other_side in other_sides:
                    other_side_vec = other_sprite.convert_self_side(other_side)
                    if desired_dist > 0:  # if distance greater than 0 move side to 'imaginary' side
                        other_side_vec = move_side_to_distance(desired_dist, other_side, other_sprite, other_side_vec)
                    min_dists.append(find_shortest_distance(self.convert_self_side(self_side), other_side_vec)[0])
            min_d = min(min_dists)  # Closest dist from side to side (or point)
            return min_d

    def calc_nearest_distance(self, sprite):
        a, b, c, d = self.get_rect_angle()

        results = []
        for p in sprite.get_rect_angle():
            results.append([point_to_line(p, a, b), point_to_line(p, b, c),
                            point_to_line(p, c, d), point_to_line(p, d, a)])

        # Find min dist in all 4 points, and min dist in this point to line
        return min([min(res, key=lambda x: x[0]) for res in results], key=lambda x: x[0])

    def get_angle_to_sprite(self, sprite):
        return 180 - (180 + self.angle - sprite.angle) % 360

    def check_mouse_over_mask(self):
        # IF MASK NEEDED - TURN ON
        pos = [p - o for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]
        pos_in_mask = pos[0] - self.rect.x, pos[1] - self.rect.y
        return self.rect.collidepoint(*pos) and self.mask.get_at(pos_in_mask)

    def check_mouse_over_full_size(self):
        pos_off = [p - o for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]
        return self.rect.collidepoint(pos_off)

    def check_mouse_over_rotated(self):
        pos_off = [p - o for p, o in zip(pygame.mouse.get_pos(), (settings.X_OFFSET, settings.Y_OFFSET))]
        return self.point_in_rect(pos_off)

    def get_rect_angle(self):
        center = self.rect.center
        # Check if smth changed or it's first time
        if self.old_center != center or self.old_angle != self.angle or not self.old_rect_angle:
            self.old_center = center
            self.old_angle = self.angle

            rect = self.original_image.get_rect(center=center)
            pts = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
            rect_angle = [(Vector2(p) - center).rotate(-self.angle) + center for p in pts]
            self.old_rect_angle = rect_angle  # Replace it with new one

        return self.old_rect_angle

    def is_in_sprite(self, other_sprite):
        self_in_other = False
        for pnt in self.get_rect_angle():
            if other_sprite.point_in_rect(pnt):
                self_in_other = True
                break
        return self_in_other

    def point_in_rect(self, p):
        a, b, c, _ = self.get_rect_angle()
        ab, ap, bc, bp = b - a, p - a, c - b, p - b
        return 0 <= ab * ap <= ab * ab and 0 <= bc * bp <= bc * bc

    def __str__(self):
        return f"{self.__class__.__name__} - angle: {self.angle}" \
               f", x: {self.rect.centerx}, y: {self.rect.centery}, z: {self.z}"
