from math import cos, sin
import numpy as np
from numba import jit


@jit(cache=True)
def rotate_vec_np(vec2d, angle):
    theta = np.deg2rad(angle)
    rot = np.array(((cos(theta), -sin(theta)), (sin(theta), cos(theta))))
    return vec2d.dot(rot)


@jit(cache=True)
def distance_np(vec1, vec2):
    """
    Compute the Euclidean distance between two vectors.
    :param vec1: Vector represented as a numpy array
    :param vec2: Vector represented as a numpy array
    :return: The Euclidean distance between the vectors
    """
    diff = vec1-vec2
    sq = np.dot(diff.T, diff)
    return np.sqrt(sq)


@jit(cache=True)
def unit_vector(vec):
    """ Returns the unit vector of the vector.  """
    return vec / length_np(vec)


@jit(cache=True)
def length_np(vec):
    return np.sqrt((vec**2).sum())


@jit(cache=True)
def ccw(a, b, c):
    # return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


@jit(cache=True)
def intersect(a, b, c, d):
    """ Return true if line segments AB and CD intersect """
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


@jit(cache=True)
def find_line_intersection(p0, p1, p2, p3):
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = s10_x * s32_y - s32_x * s10_y

    if denom == 0:
        return np.array((0.0, 0.0))  # collinear

    denom_is_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]

    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer < 0) == denom_is_positive:
        return np.array((0.0, 0.0))  # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer < 0) == denom_is_positive:
        return np.array((0.0, 0.0))  # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive:
        return np.array((0.0, 0.0))  # no collision

    # collision detected
    t = t_numer / denom
    intersection_point = np.array((p0[0] + (t * s10_x), p0[1] + (t * s10_y)))

    return intersection_point


# @jit(cache=True)
def find_shortest_distance(obj_1, obj_2):
    # TODO: for jit to work: NO isinstance, NO lambda, NO raise
    if isinstance(obj_1, tuple) and isinstance(obj_2, tuple):  # line to line
        (a, b), (c, d) = obj_1, obj_2
        inter_point = find_line_intersection(a, b, c, d)
        if inter_point.any():  # if lines intersect
            distances = ((0, inter_point, inter_point),)  # dist is zero
        else:  # find the closest point
            distances = (point_to_line(a, c, d), point_to_line(b, c, d), point_to_line(c, a, b), point_to_line(d, a, b))
    elif isinstance(obj_1, np.ndarray) and isinstance(obj_2, np.ndarray):  # point to point
        distances = ((distance_np(obj_1, obj_2), obj_1, obj_2),)
    elif isinstance(obj_1, np.ndarray) or isinstance(obj_2, np.ndarray):  # point to line
        if isinstance(obj_2, np.ndarray):  # if 2 is point - swap
            obj_1, obj_2 = obj_2, obj_1
        a, (b, c) = obj_1, obj_2
        distances = (point_to_line(a, b, c),)
    else:
        raise ValueError("Invalid arguments")

    return min(distances, key=lambda x: x[0])


# @jit(cache=True)
def find_closest_point(self_vec, side):
    dist, self_p, sprite_p = find_shortest_distance(self_vec, side)
    shortest = find_shortest_distance(self_vec, self_p), find_shortest_distance(self_vec, sprite_p)
    minp = min(shortest, key=lambda x: x[0])
    # minp = find_min_from_key(0, shortest)  # TODO: add this here (did it already when everything was polished, spent a lot of time))
    return minp[1]


@jit(cache=True)
def find_min_from_key(key, *args):
    repack_args = args[0]
    min_index = 0
    for i in range(1, len(repack_args)):
        if repack_args[i][key] < repack_args[min_index][key]:
            min_index = i
    return repack_args[min_index]


@jit(cache=True)
def find_related_sides(related, current_side, all_sides):
    left_r, right_r = False, False  # default is - cut left right segments
    if related:  # connect left right segments if related and if they are exists
        left_r = get_side_related(current_side, 1) in all_sides
        right_r = get_side_related(current_side, -1) in all_sides
    return left_r, right_r


@jit(cache=True)
def get_side_related(current_side, related_index):
    sides = ("top", "right", "bottom", "left")
    my_index = sides.index(current_side)
    return sides[(my_index + related_index) % 4]


@jit(cache=True)
def point_to_line(pnt, start, end):  # TODO: make line to line calculation
    line_vec = end - start
    pnt_vec = pnt - start
    line_len = length_np(line_vec)
    line_unitvec = line_vec / line_len
    pnt_vec_scaled = pnt_vec * (1.0 / line_len)
    t = line_unitvec.dot(pnt_vec_scaled)
    t = max(0.0, min(1.0, t))
    nearest = line_vec * t
    dist = distance_np(nearest, pnt_vec)
    nearest = nearest + start

    return dist, nearest, pnt


@jit(cache=True)
def get_line_intersection(self_pts, sprite_pts):
    # line_intersections = list()
    for i in range(4):
        a = self_pts[i]
        b = self_pts[(i + 1) % 4]
        for j in range(4):
            c = sprite_pts[j]
            d = sprite_pts[(j + 1) % 4]

            # inter_point = find_line_intersection(a, b, c, d)
            # if inter_point:
            #     line_intersections.append([Vector2(inter_point), a, b, c, d])
            if intersect(a, b, c, d):  # FOR SPEED UP (FOR NOW no need in inter point)
                return True
    # return line_intersections
    return False


@jit(cache=True)
def point_in_rect(point, rect):
    a, b, c, _ = rect
    ab, ap, bc, bp = b - a, point - a, c - b, point - b
    return 0 <= ab.dot(ap) <= ab.dot(ab) and 0 <= bc.dot(bp) <= bc.dot(bc)


@jit(cache=True)
def convert_360_to_180(angle):
    return 180 - (180 + angle) % 360  # convert [0,360] to [-180,180]


@jit(cache=True)
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


@jit(cache=True)  # Cannot determine Numba type of <class 'numba.core.dispatcher.LiftedLoop'>
def translate_sides(sides_str):
    sides = sides_str.split()
    correct_sides = set()

    for side in sides:
        for s in translate_side(side):
            if s:
                correct_sides.add(s)

    return correct_sides


@jit(cache=True)
def translate_side(side):
    if side == "any":
        side_ret = ("top", "bottom", "left", "right")
    elif side == "midany":
        side_ret = ("midtop", "midbottom", "midleft", "midright")
    elif side == "anycorner":
        side_ret = ("topleft", "topright", "bottomleft", "bottomright")
    elif side == "lr":
        side_ret = ("left", "right", "", "")
    elif side == "midlr":
        side_ret = ("midleft", "midright", "", "")
    elif side == "tb":
        side_ret = ("top", "bottom", "", "")
    elif side == "midtb":
        side_ret = ("midtop", "midbottom", "", "")
    else:
        side_ret = (side, "", "", "")
    return side_ret


# @jit(cache=True)  # can't jit this function, due to different types of return
def convert_side(side, rect):
    """ possible sides:
    topleft, bottomleft, topright, bottomright
    top, left, bottom, right
    midtop, midleft, midbottom, midright
    center"""

    # rect = [topleft, topright, bottomright, bottomleft]
    if side == "top":
        return rect[0], rect[1]
    elif side == "right":
        return rect[1], rect[2]
    elif side == "bottom":
        return rect[2], rect[3]
    elif side == "left":
        return rect[3], rect[0]
    elif side == "midtop":
        return (rect[1] + rect[0]) / 2
    elif side == "midright":
        return (rect[2] + rect[1]) / 2
    elif side == "midbottom":
        return (rect[2] + rect[3]) / 2
    elif side == "midleft":
        return (rect[3] + rect[0]) / 2
    elif side == "center":
        return (rect[2] + rect[0]) / 2
    elif side == "topleft":
        return rect[0]
    elif side == "topright":
        return rect[1]
    elif side == "bottomright":
        return rect[2]
    elif side == "bottomleft":
        return rect[3]


# def move_side_related(other_sides, desired_dist, other_sprite, other_rect):
#     # Append imaginary dist to all sides
#     for other_side in other_sides:
#         if desired_dist > 0:  # if distance greater than 0 move side to 'imaginary' side
#             other_side_vec = convert_side(other_side, other_rect)
#             new_other_side_vec = move_to_distance_by_side(desired_dist, other_side, other_sprite, other_side_vec)
#
#             for i, side_point in enumerate(other_side_vec):
#                 for j, point in enumerate(other_rect):
#                     if point == side_point:  # Moves side to 'imaginary' side, connected to all other sides
#                         other_rect[j] = new_other_side_vec[i]
#                         break
#     return other_rect


# @jit(cache=True)  # can't jit for other problem, but will be same:  "can't jit this function, due to different types of return"
def move_to_distance_by_side(desired_dist: int, side, sprite, side_vec):
    # TODO: упростить и убрать side_vec
    dist_vec = np.array((0, desired_dist), float)

    # rotate by side of other sprite
    if "topleft" == side:
        dist_vec = rotate_vec_np(dist_vec, -135)
    elif "topright" == side:
        dist_vec = rotate_vec_np(dist_vec, 135)
    elif "bottomleft" == side:
        dist_vec = rotate_vec_np(dist_vec, -45)
    elif "bottomright" == side:
        dist_vec = rotate_vec_np(dist_vec, 45)
    # 'in' is for midLEFT and other mid-sides
    elif "top" in side:
        dist_vec = rotate_vec_np(dist_vec, 180)
    elif "bottom" in side:
        dist_vec = rotate_vec_np(dist_vec, 0)
    elif "left" in side:
        dist_vec = rotate_vec_np(dist_vec, -90)
    elif "right" in side:
        dist_vec = rotate_vec_np(dist_vec, 90)
    # AND rotate by other sprite 'view'
    dist_vec = rotate_vec_np(dist_vec, -sprite.angle)

    # side_vec_test = (side_vec[1] - side_vec[0])  # works only for sides, not points
    # side_vec_test.rotate_ip(90)
    # side_vec_test.scale_to_length(desired_dist)
    # dist_vec = side_vec_test

    if type(side_vec) == tuple:
        return_vec = (side_vec[0] + dist_vec, side_vec[1] + dist_vec)
    else:  # if side is a point
        return_vec = side_vec + dist_vec

    return return_vec
