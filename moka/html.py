import re
import os, sys
from collections import OrderedDict

import cv2
import numpy as np
from tqdm import tqdm

import dominate
from dominate.util import text
from dominate.tags import meta, h2, h3, table, tr, td, th, p, a, img, br, video, caption, link, style, br, span, thead, tbody

from .core import *
from .video import *
from .system import *
from .mpl import *


##################################################################################
class HTML:
    """This HTML class allows us to save images and write texts into a single HTML file.
     It consists of functions such as <add_header> (add a text header to the HTML file),
     <add_images> (add a row of images to the HTML file), and <save> (save the HTML to the disk).
     It is based on Python library 'dominate', a Python library for creating and manipulating HTML documents using a DOM API.

     e.g. html = HTML('/something', 'My Awesome Page', base_url='www')
    """
    def __init__(self, web_dir, title, refresh=0, overwrite=False, base_url=None, inverted=False):
        """Initialize the HTML classes
        Parameters:
            web_dir (str) -- a directory that stores the webpage. HTML file will be created at <web_dir>/index.html; images will be saved at <web_dir/images/
            title (str)   -- the webpage name
            refresh (int) -- how often the website refresh itself; if 0; no refreshing
        """
        self.title = title
        self._url = web_dir
        self.web_dir = web_dir

        if base_url is not None:
            self.web_dir = os.path.expanduser(base_url) + self.web_dir

        self.img_dir = os.path.join(self.web_dir, 'images')
        self.image_dir = self.img_dir
        self.video_dir = os.path.join(self.web_dir, 'videos')
        self.overwrite = overwrite
        if not os.path.exists(self.web_dir):
            os.makedirs(self.web_dir)
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)

        self.doc = dominate.document(title=title)
        with self.doc.head:
            link(rel='stylesheet', href='/css/main.css')
            css = """
                table { border-collapse: collapse; border: 1px solid #ccc; margin: auto !important; table-layout: fixed; margin-bottom: 10px; }
                th, span { font-family: monospace; }
                td { word-wrap: break-word; padding: 5px; }
                caption { text-align: center; font-weight: 600; }
                h1, h2, h3 { text-align: center; font-weight: normal; }
                html, body { font-size: 18px; }
                """
            if inverted:
                css += """
                html, body { background-color: #111; color: #eee; }
                """
            style(css)
            meta(charset='utf-8')

        if refresh > 0:
            with self.doc.head:
                meta(http_equiv="refresh", content=str(refresh))

    def h2(self, txt):
        """Insert a header to the HTML file
        Parameters:
            text (str) -- the header text
        """
        with self.doc:
            h2(txt)

    def add(self, elem):
        self.doc.add(elem)

    def p(self, txt, center=False):
        with self.doc:
            kwargs = {} if not center else {'style': 'text-align:center;'}
            p(str(txt), **kwargs)

    def add_table(self, transpose=False):
        return HTMLTable(self) if not transpose else HTMLTableTranspose(self)

    def add_bigtable(self, ncols):
        return HTMLBigTable(self, ncols)

    def save(self):
        """save the current content to the HMTL file"""
        html_file = '%s/index.html' % self.web_dir
        if os.path.isfile(html_file) and not self.overwrite:
            ans = ask(f'file {html_file} exists. overwrite?')
            if ans == 'n': return
        f = open(html_file, 'wt')
        f.write(self.doc.render())
        f.close()

    def url(self, domain=None):
        if domain is None:
            url = '%s/index.html' % self.web_dir
        else:
            domain = domain.replace('localhost', '0.0.0.0')
            url = f'http://{domain}{self._url}/'
        return url

    def show(self, domain=None):
        os.system(f'chromium-browser {self.url(domain)}')

    def __repr__(self):
        return self.doc.render()


##################################################################################
class HTMLTable:
    """
    HTML Table, one data instance per row.
    Images and videos will be automatically saved or copied into the HTML folder.
    =============================================================================
    Example usage:

    >>> html = HTML('/bla', 'HTMLTable Demo', base_url='www')
    >>> row = {'a': 1, 'im': np.zeros([64, 64, 3]), 'vid': Video([])}
    >>> T = html.add_table()
    >>> T.add_row(row)                      # Adds a single row
    >>> T.add_row(**row)                    # Adds a single row
    >>> T.add([row for _ in range(10)])     # Adds 10 rows
    >>> html.save()

    ~/www$ python3 -m http.server 8080
    ===> open http://localhost:8080/bla/ in browser:

    +---+-----------------------------+-------------------------------+
    | a | im                          | vid                           |
    +---+-----------------------------+-------------------------------+
    | 1 | <img src=images/000000.png> | <video src=videos/000000.mp4> |
    +---+-----------------------------+-------------------------------+
    | 1 | <img src=images/000001.png> | <video src=videos/000001.mp4> |
    +---+-----------------------------+-------------------------------+
    ...
    """
    def __init__(self, html=None):
        if html is None: html = HTML('.', '', overwrite=True)
        self.html = html
        self.header = None
        self.t = table(border=1)
        self.html.doc.add(self.t)
        self.widths = dict()
        self.num_images = 0
        self.num_videos = 0
        self.start_im_id = len(os.listdir(html.image_dir))
        self.start_vd_id = len(os.listdir(html.video_dir))


    def parse_args(self, *args, **kwargs):
        ret = OrderedDict()
        if len(args) == 1:
            ret = OrderedDict(args[0])
        elif len(args) == 0:
            for k in kwargs:
                ret[k] = kwargs[k]
        else:
            for i, k in enumerate(self.header):
                ret[k] = args[i]
        return ret


    def escape(self, txt):
        for k, v in [("'", '&#39;'),
                        ('"', '&quot;'),
                        ('>', '&gt;'),
                        ('<', '&lt;'),
                        ('&', '&amp;')]:
            txt = txt.replace(k, v)
        return txt


    def add_text(self, value):
        # FIXME(zpzhou): ugly! remove this hack when have time.
        re_full = r'(<span style="color:.*">.*</span>)'
        re_part = r'<span style="color:(.*)">(.*)</span>'

        value = str(value)
        with p(style="line-height: 1.0; font-family: monospace"):
            for line in value.split('\n'):
                for part in re.split(re_full, line):
                    found = re.findall(re_part, part)
                    if found:
                        color, txt = found[0]
                        if color == 'red': color = '#DC6A73'
                        if color == 'green': color = '#88AE6D'
                        if color == 'yellow': color = '#E4CA6B'
                        span(txt, style=f'color:{color}')
                    else:
                        text(part)
                br()


    def add_image(self, value, width=400):
        # value can be path to image or bgr array
        im_dir = self.html.image_dir
        im_id = self.start_im_id + self.num_images
        im_path = f'{im_id:06d}.png'
        im_abs_path = f'{im_dir}/{im_path}'
        im_rel_path = f'images/{im_path}'
        
        if isinstance(value, str):
            value = cv2.imread(value)
            cv2.imwrite(im_abs_path, value)
        
        elif isinstance(value, np.ndarray):
            cv2.imwrite(im_abs_path, value)
        
        elif isinstance(value, matplotlib.legend.Legend):
            export_legend(value, im_abs_path)

        img(style=f"width:{width}px", src=im_rel_path)
        self.num_images += 1


    def add_video(self, value, width=400):
        if isinstance(value, str):
            filename = value.replace('/', '_')
            os.system(f'cp {value} {self.html.video_dir}/{filename}')
            vd_abs_path = f'{self.html.video_dir}/{filename}'
            vd_rel_path = f'videos/{filename}'

        else:
            vd_dir = self.html.video_dir
            vd_id = self.start_vd_id + self.num_videos
            vd_path = f'{vd_id:06d}.mp4'
            vd_abs_path = f'{vd_dir}/{vd_path}'
            vd_rel_path = f'videos/{vd_path}'

            save_video(vd_abs_path, value, fps=5, verbose=False)
            self.num_videos += 1

        os.system(f'ffmpeg -y -loglevel error -i {vd_abs_path} -pix_fmt rgb24 {vd_abs_path.replace(".mp4", ".gif")}')
        img(src=vd_rel_path.replace('.mp4', '.gif'), style=f"width:{width}px")

        # video(src=vd_rel_path, width=f'{width}px', height='auto', 
        #       controls='true', autoplay='true', loop='true', muted='true', playsinline='true')


    def set_header(self, *args, **kwargs):
        self.header = self.parse_args(*args, **kwargs)

        with self.t:
            with tr():
                for k in self.header:
                    th(k)
        return self


    def infer_header(self, item):
        header = OrderedDict()
        for k, v in item.items():
            if isinstance(v, np.ndarray):
                header[k] = 'img' if (v.ndim in {2, 3}) else 'int'
            elif isinstance(v, Video):
                header[k] = 'video'
            elif isinstance(v, int):
                header[k] = 'int'
            else:
                header[k] = 'txt'
        self.set_header(header)


    def set_widths(self, *args, **kwargs):
        self.widths.update(self.parse_args(*args, **kwargs))


    def add_row(self, *args, **kwargs):
        row = self.parse_args(*args, **kwargs)
        if not self.header: self.infer_header(row)

        with self.t:
            with tr() as table_row:
                for k, spec in self.header.items():
                    v = row.get(k, '')
                    td_style = {} if k not in self.widths \
                                    else {'style': f'width: {self.widths[k]}px'}

                    with td(halign="center", valign="top", **td_style):

                        if spec in {'txt', 'int', 'float'}:
                            self.add_text(f'{k}:\n{v}')
                        
                        elif spec in {'img'}:
                            self.add_image(v, self.widths.get(k, 400))
                        
                        elif spec in {'video'}:
                            self.add_video(v, self.widths.get(k, 400))
        return self


    def add(self, rows, no_tqdm=False):
        for item in tqdm(rows, disable=no_tqdm):
            self.add_row(**item)


    def __repr__(self):
        return self.t.render()


##################################################################################
class HTMLTableTranspose(HTMLTable):
    """
    HTML Table, one instance per column.
    =============================================================================
    Example usage:

    >>> html = HTML('/bla', 'HTMLTableTranspose Demo', base_url='www')
    >>> col = {'a': 1, 'im': np.zeros([64, 64, 3]), 'vid': Video([])}
    >>> T = html.add_table(transpose=True)
    >>> T.add_col(col)                      # Adds a single col
    >>> T.add_col(**col)                    # Adds a single col
    >>> T.add([col for _ in range(10)])     # Adds 10 cols
    >>> html.save()

    ~/www$ python3 -m http.server 8080
    ===> open http://localhost:8080/bla/ in browser:

    +-----+------------------------------+-------------------------------+
    | a   | 1                            | 1                             |
    +-----+------------------------------+-------------------------------+
    | im  | <img src=images/000000.png>  | <img src=images/000001.png>   | ...
    +-----+------------------------------+-------------------------------+
    | vid | <video src=videos/000000.mp4>| <video src=videos/000001.mp4> |
    +-----+------------------------------+-------------------------------+
    """
    def __init__(self, html):
        super(HTMLTableTranspose, self).__init__(html)
        self.table_rows = []
        self.heights = dict()

    def set_header(self, *args, **kwargs):
        self.header = self.parse_args(*args, **kwargs)

        with self.t:
            for k in self.header:
                table_row = tr()
                self.table_rows.append(table_row)
                with table_row:
                    td(k)
        return self

    def set_heights(self, *args, **kwargs):
        self.heights.update(self.parse_args(*args, **kwargs))

    def add_col(self, *args, **kwargs):
        col = self.parse_args(*args, **kwargs)
        if not self.header: self.infer_header(col)

        with self.t:
            for (k, spec), table_row in zip(self.header.items(), self.table_rows):
                with table_row:
                    v = col.get(k, '')
                    td_style = {} if k not in self.heights \
                                    else {'style': f'height: {self.heights[k]}px'}

                    with td(halign="center", valign="top", **td_style):
                        if spec in {'txt', 'int', 'float'}:
                            self.add_text(f'{v}')
                        elif spec in {'img'}:
                            self.add_image(v, self.widths.get(k, 400))
                        elif spec in {'video'}:
                            self.add_video(v, self.widths.get(k, 400))
        return self


##################################################################################
class HTMLBigTable(HTMLTableTranspose):
    """
    HTML BigTable, `ncols` instances per row.
    =============================================================================
    Example usage:

    >>> html = HTML('/bla', 'HTMLBigTable Demo', base_url='www')
    >>> item = {'a': 1, 'im': np.zeros([64, 64, 3]), 'vid': Video([])}
    >>> T = html.add_bigtable(2)                # 2 instances per row
    >>> T.add([item for _ in range(4)])         # Adds 4 instances
    >>> html.save()

    ~/www$ python3 -m http.server 8080
    ===> open http://localhost:8080/bla/ in browser:

    +-----+------------------------------+-------------------------------+
    | a   | 1                            | 1                             |
    +-----+------------------------------+-------------------------------+
    | im  | <img src=images/000000.png>  | <img src=images/000001.png>   | 
    +-----+------------------------------+-------------------------------+
    | vid | <video src=videos/000000.mp4>| <video src=videos/000001.mp4> |
    +-----+------------------------------+-------------------------------+
    +-----+------------------------------+-------------------------------+
    | a   | 1                            | 1                             |
    +-----+------------------------------+-------------------------------+
    | im  | <img src=images/000002.png>  | <img src=images/000003.png>   | 
    +-----+------------------------------+-------------------------------+
    | vid | <video src=videos/000002.mp4>| <video src=videos/000003.mp4> |
    +-----+------------------------------+-------------------------------+
    """
    def __init__(self, html=None, ncols=5):
        super(HTMLBigTable, self).__init__(html)
        self.ncols = ncols

    def set_header(self, *args, **kwargs):
        self.header = self.parse_args(*args, **kwargs)
        return self

    def add(self, columns, no_tqdm=False, display=False):
        if display: no_tqdm = True
        for i in tqdm(range(0, len(columns), self.ncols), disable=no_tqdm):
            T = self.html.add_table(transpose=True)
            if self.header: T.set_header(**self.header)
            for column in columns[i : min(i + self.ncols, len(columns))]:
                T.add_col(**column)
            if display:
                display_html(T)
            with self.html.doc:
                br()
        return self


##################################################################################
def display_html(html_str):
    import IPython.core.display as IPyDisp
    IPyDisp.display(IPyDisp.HTML(str(html_str)))