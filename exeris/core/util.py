import random

import math

from shapely.geometry import Point


def round_probabilistic(value):
    """
    :param value: Non-negative value to be rounded probabilistically
    :return: int(value) or int(value) + 1 based on decimal fraction
    """
    if random.random() < value - int(value):
        return math.ceil(value)
    return math.floor(value)


def distance(point_a, point_b):
    return math.sqrt((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2)


def direction(first_loc_pos, second_loc_pos):
    return math.asin(
        (second_loc_pos.x - first_loc_pos.x) / distance(first_loc_pos, second_loc_pos))


def pos_for_distance_in_direction(initial_pos, direction, distance):
    return Point(initial_pos.x + math.sin(math.radians(direction)) * distance,
                 initial_pos.y + math.cos(math.radians(direction)) * distance)
