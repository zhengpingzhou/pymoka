class BGR:
    DARK_YELLOW = (0, 200, 200)
    YELLOW = (0, 255, 255)
    RED = (0, 0, 255)
    DARK_RED = (0, 0, 128)
    LIGHT_RED = (128, 128, 255)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 128, 0)
    LIGHT_GREEN = (128, 255, 128)
    BLUE = (255, 0, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


def hex2rgb(hex_string):
    h = hex_string.lstrip('#')
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

def rgb2hex(rgb):
    r, g, b = rgb
    return '#%02x%02x%02x' % (r, g, b)