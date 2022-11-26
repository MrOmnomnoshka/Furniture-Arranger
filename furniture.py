import furniture_sprites
import settings
from math_2d import *
from sprite_object import SpriteObject
from math import copysign
import room_parts
import re


class Furniture(SpriteObject):
    active = False
    show_distances = False

    # def update(self):
    #     super().update()

    def get_intersections(self, sprite):
        if self.rect.colliderect(sprite.rect):
            intersection = get_rotated_rect_intersections(self.get_rotated_rect(), sprite.get_rotated_rect())
            if intersection:  # if exists any intersection, check for depth intersection
                return self.check_for_depth_intersection(sprite)

        return False  # No collisions

    def check_for_depth_intersection(self, sprite):
        # Special case for zero-depth objects (like carpets)
        if (self.depth <= 1 or sprite.depth <= 1) and not isinstance(sprite, room_parts.Wall):
            return False  # Object with zero depth can't intersect with other objects (except Walls)

        acceptable_diff = (self.depth + sprite.depth) // 2
        current_diff = abs(self.z - sprite.z)
        if current_diff >= acceptable_diff:
            if isinstance(sprite, room_parts.Wall):
                return True, "WALL intersection"
            return False  # exit without intersection
        else:
            return True, "z intersection", acceptable_diff - current_diff

    def move_sprite(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def check_for_movement(self, move_vec, other_sprite):
        self.move_sprite(move_vec[0], move_vec[1])
        intersection_info = self.get_intersections(other_sprite)
        self.move_sprite(-move_vec[0], -move_vec[1])
        return not intersection_info

    def solve_collisions(self, other_sprite):  # , draw_all, font, display_surface, all_sprites, clock):
        # TODO: Тут пытался именно "решить" столновение, путем расстаскивания 2-ух объектов, после решил, что это не нужно и можно просто штрафить сильно
        intersection_info = self.get_intersections(other_sprite)

        if intersection_info:
            # d_info = intersection_info, self, other_sprite
            # draw_loop("COLLISION")
            # print(intersection_info)
            return settings.COLLISION_PENALTY
        # else:
        # draw_loop(f"NO COLLISION {self}  {other_sprite}")
        # return 100_000

        # max_iter = 10  # try 'max_iter' times to solve the collision and then return penalty
        # while intersection_info and max_iter:
        #     self_in_other = self.is_in_sprite(other_sprite)  # other in me or I am in the other?
        #     direction_to_move = (int(self_in_other) * 2 - 1)  # -1 out | 1 in
        #
        #     if intersection_info[0] == "inside":  # if one rect inside another
        #         follow_sprite = self if self_in_other else other_sprite  # from whom to run if inside
        #         target_sprite = other_sprite if self_in_other else self  # from whom to check is point in sprite
        #         t_pnts = target_sprite.get_rect_angle()
        #         edges = [[t_pnts[i], t_pnts[(i + 1) % len(t_pnts)]] for i in range(len(t_pnts))]
        #         dist_to_edges = [(point_to_line(follow_sprite.rect.center, edge[0], edge[1]), edge) for edge in edges]
        #         min_dist, closest_edge = min(dist_to_edges, key=lambda x: x[0][0])
        #
        #         s_pnts = follow_sprite.get_rect_angle()
        #         s_dist_to_edges = [point_to_line(point, closest_edge[0], closest_edge[1]) for point in s_pnts]
        #         max_dist = max(s_dist_to_edges, key=lambda x: x[0])
        #         dist_to_move = max_dist[1] - max_dist[2]
        #
        #     elif intersection_info[0] == "line":  # TODO: можно сделать похожую логику как с inside
        #         intersections = intersection_info[1]
        #         if len(intersections) <= 3:
        #             if not self_in_other:
        #                 for inter in intersections:  # swap a,b with c,d in every intersection
        #                     inter[1], inter[3] = inter[3], inter[1]
        #                     inter[2], inter[4] = inter[4], inter[2]
        #
        #             nearest_points = []
        #             for inter_point, sprite_l0, sprite_l1, other_l0, other_l1 in intersections:
        #                 point_in_other = [point for point in (sprite_l0, sprite_l1) if
        #                                   other_sprite.point_in_rect(point)].pop()
        #                 to_edge = point_to_line(point_in_other, other_l0, other_l1)  # returns: dist, nearest, pnt
        #                 nearest_points.append(to_edge)
        #             max_dist = max(nearest_points, key=lambda x: x[0])
        #             dist_to_move = max_dist[1] - max_dist[2]
        #         elif len(intersections) >= 4:
        #             direction_to_move = 1
        #
        #             s_pnts = self.get_rect_angle()
        #             s_edges = [[s_pnts[i], s_pnts[(i + 1) % len(s_pnts)]] for i in range(len(s_pnts))]
        #             t_pnts = other_sprite.get_rect_angle()
        #             t_edges = [[t_pnts[i], t_pnts[(i + 1) % len(t_pnts)]] for i in range(len(t_pnts))]
        #
        #             swap = False
        #             max_dist_edge = []
        #             for swap_objects in range(2):  # target to me and me to target
        #                 for i in range(len(s_edges)):  # all my ages
        #                     move_vectors = []
        #
        #                     for n in range(2):  # 2 sides of edge
        #                         side_line = s_edges[i-n*2][0], s_edges[(i+1-n*2) % len(s_edges)][0]
        #
        #                         for j in range(len(t_edges)):  # all sides of target
        #                             target_line = t_edges[j][0], t_edges[(j+1) % len(t_edges)][0]
        #
        #                             inter_point = find_intersection(side_line[0], side_line[1],
        #                                                             target_line[0], target_line[1])
        #                             if inter_point:
        #                                 vec_to_move = inter_point - side_line[0-n]
        #                                 if swap:
        #                                     vec_to_move = -vec_to_move
        #
        #                                 if self.check_for_movement(vec_to_move, other_sprite):
        #                                     move_vectors.append(vec_to_move)  # Append after check if it can move there
        #
        #                     if move_vectors:
        #                         max_dist_edge.append(max(move_vectors, key=lambda x: x.length_squared()))
        #
        #                         # for vec in move_vectors:
        #                         #     move_vec = vec
        #                         #     self.move_sprite(move_vec[0] * direction_to_move,
        #                         #                      move_vec[1] * direction_to_move)
        #                         #     draw_all(font, display_surface, all_sprites, clock)
        #                         #
        #                         #     move_vec = vec * -1
        #                         #     self.move_sprite(move_vec[0] * direction_to_move,
        #                         #                      move_vec[1] * direction_to_move)
        #                         #     draw_all(font, display_surface, all_sprites, clock)
        #
        #                 # swap edges
        #                 s_edges, t_edges = t_edges, s_edges
        #                 swap = True
        #             dist_to_move = min(max_dist_edge, key=lambda x: x.length_squared())
        #
        #     dist_to_move = [max(round((abs(xy))), 1) * copysign(1, xy) for xy in dist_to_move]
        #     self.move_sprite(dist_to_move[0] * direction_to_move, dist_to_move[1] * direction_to_move)
        #     # draw_all(font, display_surface, all_sprites, clock)
        #
        #     intersection_info = self.get_intersections(other_sprite)
        #     max_iter -= 1
        #
        #     if max_iter == 0:
        #         # Fitness penalty
        #         return 10000

    def solve_collisions_and_offsets(self):
        # TODO: ТУТ УХОДИТ 25% скорости, в нашей конкретной задаче мб попробовать просчитать один раз всю зону, куда
        #  предмету не стоит выходить, и проверять для каждого агента из ГА не в этой ли он зоне (а не счтить для
        #  каждого с нуля как сейчас)
        for other_sprite in settings.ALL_OBJECTS:
            if other_sprite != self:
                # Solve collisions
                intersection = self.get_intersections(other_sprite)
                if intersection:
                    return settings.COLLISION_PENALTY

                # OLD WAY
                # penalty = self.solve_collisions(other_sprite)
                # if penalty:
                #     # fit_sum += penalty
                #     return penalty

                # Solve sprites offsets rules
                # if (me_in_sprite_offset or sprite_in_my_offset) and depth_inter and (not me_in_rules and not rules_in_me)
                if (get_rotated_rect_intersections(self.get_rotated_rect(), other_sprite.offset_rotated_rect) or
                    get_rotated_rect_intersections(other_sprite.get_rotated_rect(), self.offset_rotated_rect)) and \
                        self.check_for_depth_intersection(other_sprite) and \
                        (not check_in_rules_recursively(self.__class__, other_sprite.__class__) and
                         not check_in_rules_recursively(other_sprite.__class__, self.__class__)):
                    return settings.COLLISION_PENALTY // 30  # 30 is just magic number to divide offset from collision

    def get_fitness(self):
        fit_sum = 0

        # Solve all collisions and offsets rules
        penalty = self.solve_collisions_and_offsets()
        if penalty:
            return penalty

        # If there are a few rules, add only the minimum one
        optional_rules_fitness = []

        for rule_obj in self.rules:
            # combine every instance by rule groups
            rule_group = []

            rules = self.rules[rule_obj]
            if rules and rule_obj in (type(obj) for obj in settings.ALL_OBJECTS):  # if rule is not 'None' and object exists in current room
                for other_sprite in settings.ALL_OBJECTS:
                    if isinstance(other_sprite, rule_obj) and other_sprite != self:
                        if type(rules) == dict:  # if there is only one rule
                            rules = (rules,)  # make it iterable (tuple)

                        for rule in rules:
                            dist = self.rule_distance_to_sprite(other_sprite, rule)
                            rule_group.append((other_sprite, rule, dist))

            # calc nearest fitness
            if any(rule_group):
                nearest = min(rule_group, key=lambda x: x[2])

                other_sprite, rule, dist = nearest
                angle = self.get_angle_to_sprite(other_sprite, rule)
                rule_required = rule["required"] if "required" in rule else False
                fitness = dist + angle

                if rule_required:
                    fit_sum += fitness
                else:
                    optional_rules_fitness.append(fitness)

        if optional_rules_fitness:  # sum of all required rules + minimum of optional rules
            fit_sum += min(optional_rules_fitness)
        return round(fit_sum, 2)  # WARNING ROUND IS VERY DANGEROUS. DO NOT FORGET ABOUT IT


def check_in_rules_recursively(slave, class_to_check):
    # Doing it recursively is wrong. TODO(MB): make exception rule for some objects? OR for objects that stay on other?
    # if slave == furniture_sprites.TableLamp - OUR EXCEPTION
    if (slave == furniture_sprites.TableLamp or class_to_check in slave.rules) and not class_to_check == room_parts.Wall:
        return True  # Find in all rules
    return False

    # if class_to_check == slave:
    #     return True
    # else:
    #     if slave.rules:
    #         if class_to_check in slave.rules:
    #             return True  # Find in all rules
    #         for rule in slave.rules:
    #             if check_in_rules_recursively(rule, class_to_check):
    #                 return True
    #     else:
    #         return False
    # return False

    # ## OLD version:
    # ## return isinstance(sprite_to_check, tuple(self.rules))
