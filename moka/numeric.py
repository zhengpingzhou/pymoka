import random
import numpy.linalg as LA


def normalize(value, value_min, value_max):
    """Map value from [value_min, value_max] to [-1, 1]"""
    return 2 * ((value - value_min) / (value_max - value_min)) - 1


def unnormalize(value, value_min, value_max):
    """Map value from [-1, 1] to [value_min, value_max]"""
    return ((value + 1) / 2.0 * (value_max - value_min) + value_min)

