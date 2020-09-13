import os, sys
from copy import deepcopy

import cv2
import numpy as np

from .color import *

##################################################################################
# OpenCV
##################################################################################
def plot_dot(im, center, color=(0, 0, 255), radius=2):
    cv2.circle(im, (int(center[0]), int(center[1])), radius, color, thickness=-1)


def plot_line(im, p1, p2, color=(0, 0, 255), thickness=2):
    cv2.line(im, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color, thickness)


def plot_text(im, text, color=(0, 0, 0), scale=1, thickness=1, pos='br', box=None, margin=5,
    minScale=0.3, minThickness=1):
    """Returns: [x1, y1, x2, y2] bounding box of text"""
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    fontScale              = scale
    fontColor              = (255,255,255)
    lineType               = cv2.LINE_AA
    if box is None:
        y1, x1 = 0, 0
        y2, x2, _ = im.shape
    else:
        box = np.array(box).astype(int)
        x1, y1, x2, y2 = box
    while True:
        text_width, text_height = cv2.getTextSize(text, font, fontScale, lineType)[0]
        text_width += margin; text_height += margin
        if text_width <= x2 - x1 - 2*margin and text_height <= y2 - y1 - 2*margin: break
        if fontScale < minScale: break
        fontScale *= 0.9
        thickness = max(minThickness, thickness - 1)
    # loc = bottom left corner of text
    t = y1 + text_height + margin
    b = y2 - margin
    l = x1 + margin
    r = x2 - text_width
    if pos == 'br' or pos == 'rb':
        loc = (r, b)
    elif pos == 'tr' or pos == 'rt':
        loc = (r, t)
    elif pos == 'tl' or pos == 'lt':
        loc = (l, t)
    elif pos == 'bl' or pos == 'lb':
        loc = (l, b)
    else:
        loc = (x1 + pos[0], y1 + pos[1] + text_height)
    cv2.putText(im, text, loc, font, fontScale, color, thickness, lineType)
    return (loc[0], loc[1] - text_height, loc[0] + text_width, loc[1])


def plot_seg(I, x, color, radius=1, width=1):
    plot_dot(I, x[0], color, radius=radius)
    plot_dot(I, x[1], color, radius=radius)
    plot_line(I, x[0], x[1], color, thickness=width)


def plot_box(im, box, color, thickness=2, solid=False, alpha=1.0, verbose=True):
    """box: [x1, y1, x2, y2], color: 0~255"""
    H, W = im.shape[0], im.shape[1]
    x1, y1, x2, y2 = [int(x) for x in box]
    if not ((0 <= x1 < W) and (0 <= y1 < H) and (0 <= x2 < W) and (0 <= y2 < H) and\
            (x1 < x2) and (y1 < y2)):
        x1 = max(0, min(x1, W - 1))
        x2 = max(0, min(x2, W - 1))
        y1 = max(0, min(y1, H - 1))
        y2 = max(0, min(y2, H - 1))
        clipped = [x1, y1, x2, y2]
        # if verbose:
        #     sys.stderr.write(f'WARNING: invalid box: {box}, Clipped to: {clipped}\n')
        #     sys.stderr.flush()
        box = clipped

    if not solid:
        cv2.rectangle(im, (x1, y1), (x2, y2), color, thickness)
    else:
        mask = np.zeros_like(im)
        cv2.rectangle(mask, (x1, y1), (x2, y2), color, -1)
        patch = im[y1:y2, x1:x2, :]
        patch = np.uint8(patch * (1 - alpha) + mask[y1:y2, x1:x2, :] * alpha)
        im[y1:y2, x1:x2, :] = patch


def heatmap(x, cmap='jet', normalize=True):
    # BGR
    assert len(x.shape) == 2
    h, w = x.shape

    if normalize:
        x = (x - x.min()) / (x.max() - x.min())

    if cmap == 'jet':
        x = cv2.applyColorMap(np.uint8(x * 255), cv2.COLORMAP_JET)
        return x[..., :3]
    elif cmap == 'mpl':
        return cv2.resize(fig2im(*gridview([x])), (w, h))[:, :, ::-1]


def main_loop(images, title='main'):
    images = deepcopy(images)
    for idx, im in enumerate(images):
        plot_text(im, f'{idx}/{len(images)}', color=BGR.WHITE)

    idx = 0
    while idx < len(images):
        cv2.imshow(title, images[idx])
        key = cv2.waitKey(0)
        if key == ord('['):
            idx = (idx + len(images) - 1) % len(images)
        elif key == ord(']'):
            idx = (idx + len(images) + 1) % len(images)
        elif key == ord('0'):
            idx = 0
        elif key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit(0)

