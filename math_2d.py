from pygame.math import Vector2


def ccw(a, b, c):
    return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)


def intersect(a, b, c, d):
    """ Return true if line segments AB and CD intersect """
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def find_intersection(p0, p1, p2, p3):
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = s10_x * s32_y - s32_x * s10_y

    if denom == 0:
        return None  # collinear

    denom_is_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]

    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer < 0) == denom_is_positive:
        return None  # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer < 0) == denom_is_positive:
        return None  # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive:
        return None  # no collision

    # collision detected
    t = t_numer / denom
    intersection_point = [p0[0] + (t * s10_x), p0[1] + (t * s10_y)]

    return intersection_point


def find_shortest_distance(obj_1, obj_2):
    if isinstance(obj_1, tuple) and isinstance(obj_2, tuple):  # line to line
        (a, b), (c, d) = obj_1, obj_2
        distances = [point_to_line(a, c, d), point_to_line(b, c, d), point_to_line(c, a, b), point_to_line(d, a, b)]
    elif isinstance(obj_1, Vector2) and isinstance(obj_2, Vector2):  # point to point
        distances = [[obj_1.distance_to(obj_2)]]
    elif isinstance(obj_1, Vector2) or isinstance(obj_2, Vector2):  # point to line
        if isinstance(obj_2, Vector2):  # if 2 is point - swap
            obj_1, obj_2 = obj_2, obj_1
        a, (b, c) = obj_1, obj_2
        distances = [point_to_line(a, b, c)]
    else:
        raise ValueError("Invalid arguments")

    return min(distances, key=lambda x: x[0])


def point_to_line(pnt, start, end):  # TODO: make line to line calculation
    line_vec = end - start
    pnt_vec = pnt - start
    line_len = line_vec.length()
    line_unitvec = line_vec.normalize()
    pnt_vec_scaled = pnt_vec * (1.0 / line_len)
    t = line_unitvec.dot(pnt_vec_scaled)
    t = max(0.0, min(1.0, t))
    nearest = line_vec * t
    dist = nearest.distance_to(pnt_vec)
    nearest = nearest + start

    return dist, nearest, Vector2(pnt)


def get_line_intersection(self_pts, sprite_pts):
    line_intersections = list()
    for i in range(len(self_pts)):
        a = self_pts[i]
        b = self_pts[(i + 1) % len(self_pts)]
        for j in range(len(sprite_pts)):
            c = sprite_pts[j]
            d = sprite_pts[(j + 1) % len(sprite_pts)]

            inter_point = find_intersection(a, b, c, d)
            if inter_point:
                line_intersections.append([Vector2(inter_point), a, b, c, d])
    return line_intersections


def point_in_rect(point, rect):
    a, b, c, _ = rect
    ab, ap, bc, bp = b - a, point - a, c - b, point - b
    return 0 <= ab * ap <= ab * ab and 0 <= bc * bp <= bc * bc


def get_rotated_rect_intersections(rect_1, rect_2):
    # Check for lines intersection
    line_intersections = get_line_intersection(rect_1, rect_2)
    if line_intersections:  # Collides in some edges (2 or 4)
        return True

    # Check for points intersection
    for pnt in rect_1:
        if point_in_rect(pnt, rect_2):
            return True  # points intersection
    for pnt in rect_2:
        if point_in_rect(pnt, rect_1):
            return True  # points intersection

    return False  # No collisions


def translate_side(side_to_translate):
    side = side_to_translate.split()

    if side[0] == "any":
        side = ["top", "bottom", "left", "right"]
    elif side[0] == "midany":
        side = ["midtop", "midbottom", "midleft", "midright"]
    elif side[0] == "lr":
        side = ["left", "right"]
    elif side[0] == "midlr":
        side = ["midleft", "midright"]
    elif side[0] == "tb":
        side = ["top", "bottom"]
    elif side[0] == "midtb":
        side = ["midtop", "midbottom"]
    return side


def convert_side(side, rect):
    """ possible sides:
    topleft, bottomleft, topright, bottomright TODO: no corners
    *top, *left, *bottom, *right
    *midtop, *midleft, *midbottom, *midright
    *center"""

    # rect = [topleft, topright, bottomright, bottomleft]
    if side == "top":
        return Vector2(rect[0]), Vector2(rect[1])
    elif side == "bottom":
        return Vector2(rect[3]), Vector2(rect[2])
    elif side == "left":
        return Vector2(rect[0]), Vector2(rect[3])
    elif side == "right":
        return Vector2(rect[1]), Vector2(rect[2])
    elif side == "midtop":
        return (rect[1] - rect[0]) / 2 + rect[0]
    elif side == "midbottom":
        return (rect[2] - rect[3]) / 2 + rect[3]
    elif side == "midleft":
        return (rect[3] - rect[0]) / 2 + rect[0]
    elif side == "midright":
        return (rect[2] - rect[1]) / 2 + rect[1]
    elif side == "center":
        return (rect[2] - rect[0]) / 2 + rect[0]


def move_side_to_distance(desired_dist, other_side, other_sprite, other_side_vec):
    # if side is a line
    if isinstance(other_side_vec, tuple):
        return_vec = [Vector2(other_side_vec[0]), Vector2(other_side_vec[1])]
    else:  # if side is a point
        return_vec = Vector2(other_side_vec)

    dist_vec = Vector2(0, desired_dist)
    # rotate by side of other sprite
    if "top" in other_side:
        dist_vec.rotate_ip(180)
    elif "bottom" in other_side:
        dist_vec.rotate_ip(0)
    elif "left" in other_side:
        dist_vec.rotate_ip(90)
    elif "right" in other_side:
        dist_vec.rotate_ip(-90)
    # AND rotate by other sprite 'view'
    dist_vec.rotate_ip(-other_sprite.angle)

    # if side is a line
    if isinstance(other_side_vec, tuple):
        return_vec[0] += dist_vec
        return_vec[1] += dist_vec
    else:  # if side is a point
        return_vec += dist_vec

    return return_vec
