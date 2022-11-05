import settings
from math_2d import *
from sprite_object import SpriteObject
from math import copysign
import room_parts
import re


class Furniture(SpriteObject):
    active = False
    show_distances = False

    rules_to_all_furniture = {room_parts.Door: {"sides": ("any", "bottom", ">110"), "angle": "any", "required": True},  # TODO: для двери сделать пермещение вниз на целое число и влево на половину этого числа ( если петли стоят слева и дверь вдруг открывется на все 180 градусов)
                              room_parts.Window: {"sides": ("any", "bottom", ">75"), "angle": "any", "required": True}}  # TODO: can't ues furniture_sprites, mb add more classes
                              #furniture_sprites.TV: {"sides": ("any", "bottom", ">60"), "angle": "any", "required": True}}

    def __init__(self, *args, **kwargs):
        self.rules = self.rules_to_all_furniture.copy()
        if hasattr(self, "rules_to_this_furniture"):
            self.rules.update(self.rules_to_this_furniture)

        super().__init__(*args, **kwargs)

    # def update(self):
    #     super().update()

    def get_intersections(self, sprite):
        # Special case for zero-depth objects (like carpets)
        if not isinstance(sprite, room_parts.Wall) and self.depth <= 1 or sprite.depth <= 1:
            return False  # Object with zero depth can't intersect with other objects (except Walls)

        intersection = None
        if sprite != self and self.rect.colliderect(sprite.rect):
            self_pts, sprite_pts = self.get_rect_angle(), sprite.get_rect_angle()

            # Check for lines intersection
            line_intersections = get_line_intersection(self_pts, sprite_pts)
            if line_intersections:  # Collides in some edges (2 or 4)
                intersection = "line", line_intersections

            if not intersection:  # if no lines intersections, continue to check for points intersection
                # Check for points intersection
                pnts_inside = list()
                for pnt in self_pts:
                    if point_in_rect(pnt, sprite_pts):
                        pnts_inside.append(pnt)
                for pnt in sprite_pts:
                    if point_in_rect(pnt, self_pts):
                        pnts_inside.append(pnt)

                if pnts_inside:  # Collide but one inside another
                    intersection = "inside", pnts_inside

            if intersection:  # if exists any intersection, check for depth intersection
                # check for depth collisions
                acceptable_diff = (self.depth + sprite.depth) // 2
                current_diff = abs(self.z - sprite.z)
                if current_diff >= acceptable_diff:
                    if isinstance(sprite, room_parts.Wall):
                        return "WALL", intersection
                    return False  # exit without intersection
                else:
                    return "z intersection", acceptable_diff - current_diff

        return False  # No collisions

    def move_sprite(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def check_for_movement(self, move_vec, other_sprite):
        self.move_sprite(move_vec[0], move_vec[1])
        intersection_info = self.get_intersections(other_sprite)
        self.move_sprite(-move_vec[0], -move_vec[1])
        return not intersection_info

    def solve_collisions(self, other_sprite):  # , draw_all, font, display_surface, all_sprites, clock):
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

    def get_info_by_rule(self, other_sprite, rule):
        angle_to = self.get_angle_to_sprite(other_sprite)
        dist = self.rule_distance_to_sprite(other_sprite, rule)
        return angle_to, dist

    def get_fitness(self):
        fit_sum = 0

        # Solve collisions
        for other_sprite in settings.ALL_OBJECTS:
            penalty = self.solve_collisions(other_sprite)
            if penalty:
                # fit_sum += penalty
                return penalty

        #  combine every instance by rule groups
        rule_group = []

        # delete all old 'rect_rotated_rules' for correct drawing in DEBUG mode
        self.rect_rotated_rules = []
        for rule_obj in self.rules:
            if self.rules[rule_obj]:  # if not None
                rule_group.append([])
                for other_sprite in settings.ALL_OBJECTS:
                    if isinstance(other_sprite, rule_obj) and other_sprite != self:
                        rule = self.rules[rule_obj]
                        info = self.get_info_by_rule(other_sprite, rule)  # angle, distance
                        rule_group[-1].append((other_sprite, rule, info))

        # If there are a few rules, move to the minimum one
        optional_rules_fitness = []

        # Get fitness for every group
        for rule_instance in rule_group:
            if rule_instance:  # If not empty
                for rule_obj in rule_instance:
                    other_sprite, rule, (angle_real, distances_real) = rule_obj
                    # other_sprite, rule, (angle_real, distances_real) = nearest_object
                    angle_desired, distances_desired = rule["angle"], rule["sides"]
                    rule_required = "required" in rule

                    distance_diff = abs(distances_real)  # No need in abs, because it's always positive

                    if angle_desired == "any":
                        angle_diff = 0
                    elif angle_desired == "center":
                        real_view = Vector2(0, 1).rotate(-self.angle)
                        desired_view = (Vector2(other_sprite.rect.center) - Vector2(self.rect.center)).normalize()
                        angle_diff_360 = real_view.angle_to(desired_view)
                        angle_diff = abs(180 - (180 + angle_diff_360) % 360)
                    else:
                        angle_diff_360 = abs(angle_desired - angle_real)
                        angle_diff = abs(180 - (180 + angle_diff_360) % 360)

                    # if isinstance(other_sprite, Wall):
                    #     affinity = 100
                    # # elif isinstance(self, furniture_sprites.Table):  # TODO: FOR DEBUG
                    # #     affinity = 0
                    # else:
                    #     affinity = 1
                    affinity = 1

                    fitness = (distance_diff + angle_diff) * affinity
                    if rule_required and re.search(r"[><=]", str(distances_desired[2])):  # Always immediately add it if required
                        fit_sum += fitness
                    else:  # Add it to optional rules
                        nearest_object = min(rule_instance, key=lambda x: x[2][1])
                        if rule_obj == nearest_object:
                            optional_rules_fitness.append(fitness)

                    # fit_sum += fitness
                    # fit_sum += angle_diff
        if optional_rules_fitness:  # sum of all required rules + minimum of optional rules
            fit_sum += min(optional_rules_fitness)
        return fit_sum
