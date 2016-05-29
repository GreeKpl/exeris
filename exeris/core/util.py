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


def direction_degrees(first_loc_pos, second_loc_pos):
    x_difference = second_loc_pos.x - first_loc_pos.x
    y_difference = second_loc_pos.y - first_loc_pos.y
    return (360 + math.degrees(math.atan2(y_difference, x_difference))) % 360


def pos_for_distance_in_direction(initial_pos, direction_deg, distance):
    return Point(initial_pos.x + math.cos(math.radians(direction_deg)) * distance,
                 initial_pos.y + math.sin(math.radians(direction_deg)) * distance)


def serialize_notifications(notifications, pyslate):
    return [{"notification_id": n.id, "title": pyslate.t(n.title_tag, **n.title_params),
             "count": n.count, "date": n.game_date} for n in notifications]
