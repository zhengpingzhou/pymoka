from .core import *


def sort_dict(d, sort_by_index=-1, reverse=True, key=None):
    if isinstance(d, dict) or isinstance(d, Dict): d = list(d.items())
    if key is None: key = lambda x: x[sort_by_index]
    return sorted(d, key=key, reverse=reverse)