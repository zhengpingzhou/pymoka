import math
import numpy as np

import matplotlib
import matplotlib.pyplot as plt


##################################################################################
# matplotlib
##################################################################################
def subplots(rows, cols, dpi=100, keep_dim=False, flatten=False, figsize=3, aspect_ratio=1.0):
    """aspect_ratio = width / height"""
    fig, ax = plt.subplots(nrows=rows, ncols=cols,
        dpi=dpi, figsize=(int(cols*figsize*aspect_ratio), rows*figsize))
    if keep_dim:
        if rows == 1:
            ax = ax.reshape([1, -1])
        if cols == 1:
            ax = ax.reshape([-1, 1])
    if flatten:
        ax = np.reshape([ax], -1)
    return fig, ax


def compact(fig=plt.gcf(), ax=plt.gca(), padding=0, margin=0, h_margin=0, w_margin=0, ticks=False):
    if not ticks:
        for a in np.reshape([ax], -1):
            a.axis('off')
            a.set_xticklabels([])
            a.set_yticklabels([])
    fig.tight_layout(pad=margin, h_pad=h_margin, w_pad=w_margin)
    fig.subplots_adjust(wspace=padding, hspace=padding)
    return fig, ax


def fig2im(fig, ax, dpi=40, padding=0, margin=0, h_margin=0, w_margin=0, channels='rgb', ticks=False):
    """
    in:
        @fig, ax: a matplotlib fig to rasterize
    out:
        @im: RGB image
    """
    fig.set_dpi(dpi)
    fig, ax = compact(fig, ax, padding, margin, h_margin, w_margin, ticks)
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    if channels == 'bgr': data = data[:, :, ::-1]
    return data


def gridview(im, rows=-1, cols=-1, dpi=100, keep_dim=False, flatten=False, figsize=3, titles=None,
    padding=0.05, margin=0, h_margin=0, w_margin=0, ticks=True, fontsize=3, title_fontsize=5):
    """
    in:
        @im: [N, H, W] or [N, H, W, 3] images.
    out:
        @fig, ax: a visualized matplotlib fig
    """
    n = len(im)
    assert n > 0

    try:
        h, w = im[0].shape
    except:
        h, w, c = im[0].shape
        assert c == 3, c

    aspect_ratio = w / h

    if ticks:
        padding = 0.2

    if rows == -1 and cols == -1:
        rows, cols = math.ceil(n/4), min(n, 4)
    elif rows == -1:
        rows = math.ceil(n/cols)
    elif cols == -1:
        cols = math.ceil(n/rows)
    else:
        assert rows * cols >= n, (rows, cols)

    fig, ax = subplots(rows, cols, dpi, keep_dim, flatten, figsize, aspect_ratio=aspect_ratio)
    for i in range(n):
        a = np.reshape([ax], -1)[i]
        if len(im[i].shape) == 3:
            a.imshow(im[i][:, :, ::-1])
        else:
            a.imshow(im[i])
        if titles:
            a.set_title(np.reshape([titles], -1)[i])

    matplotlib.rc('xtick', labelsize=fontsize)
    matplotlib.rc('ytick', labelsize=fontsize)
    matplotlib.rc('axes', titlesize=title_fontsize)

    fig, ax = compact(fig, ax, padding, margin, h_margin, w_margin, ticks)
    return fig, ax


def export_legend(legend, filename="legend.png"):
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)
    plt.close(fig)


def mplrc(*args, **kwargs):
    if 'fontsize' in kwargs:
        fontsize = kwargs['fontsize']
        matplotlib.rc('xtick', labelsize=fontsize)
        matplotlib.rc('ytick', labelsize=fontsize)
        matplotlib.rc('axes', titlesize=fontsize)
    if 'dpi' in kwargs:
        dpi = kwargs['dpi']
        matplotlib.rc('figure', dpi=dpi)

    if len(args) == 1:
        a = args[0]
        if isinstance(a, str):
            return matplotlib.rcParams[a]
        elif isinstance(a, dict):
            for k, v in a.items():
                matplotlib.rcParams[k] = v
    else:
        return [matplotlib.rcParams[a] for a in args]