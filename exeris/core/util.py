import random

import math


def round_probabilistic(value):
    """
    :param value: Non-negative value to be rounded probabilistically
    :return: int(value) or int(value) + 1 based on decimal fraction
    """
    if random.random() < value - int(value):
        return math.ceil(value)
    return math.floor(value)
