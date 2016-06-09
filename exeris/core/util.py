import random

import math

from exeris.core import map_data
from shapely.geometry import Point


def round_probabilistic(value):
    """
    :param value: Non-negative value to be rounded probabilistically
    :return: int(value) or int(value) + 1 based on decimal fraction
    """
    if random.random() < value - int(value):
        return math.ceil(value)
    return math.floor(value)


def euclidean_distance(point_a, point_b):
    return math.sqrt((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2)


def distance(point_a, point_b):
    """
    Distance with respect to map edges wrapping algorithm.
    :param point_a: first point. Should have attrs "x" and "y"
    :param point_b: first point. Should have attrs "x" and "y"
    :return: Distance assuming there can be a shorter distance than euclidean distance by wrapping the map around edges.
    """
    projections_of_point_b = get_all_projected_points(point_b)
    return min([euclidean_distance(point_a, projection_b) for projection_b in projections_of_point_b])


def get_closest_projection_of_second_point(point_a, point_b):
    projected_points = get_all_projected_points(point_b)

    return sorted(projected_points, key=lambda x: euclidean_distance(point_a, x))[0]


def get_all_projected_points(center_point):
    cloned_points = []
    for x in [-map_data.MAP_WIDTH, 0, map_data.MAP_WIDTH]:  # left and right
        cloned_points.append(Point(center_point.x + x, center_point.y))
    for x in [-0.5 * map_data.MAP_WIDTH, 0.5 * map_data.MAP_WIDTH]:  # top and bottom
        for y in [0, 2 * map_data.MAP_HEIGHT]:
            cloned_points.append(Point(center_point.x + x, y - center_point.y))

    return cloned_points


def direction_degrees(point_a, point_b):
    closest_point_projection = get_closest_projection_of_second_point(point_a, point_b)

    x_difference = closest_point_projection.x - point_a.x
    y_difference = closest_point_projection.y - point_a.y
    return (360 + math.degrees(math.atan2(y_difference, x_difference))) % 360


def pos_for_distance_in_direction(initial_pos, direction_deg, distance):
    return Point(initial_pos.x + math.cos(math.radians(direction_deg)) * distance,
                 initial_pos.y + math.sin(math.radians(direction_deg)) * distance)


def serialize_notifications(notifications, pyslate):
    return [{"notification_id": n.id, "title": pyslate.t(n.title_tag, **n.title_params),
             "count": n.count, "date": n.game_date} for n in notifications]
