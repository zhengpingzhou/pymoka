import tempfile

import cv2
import numpy as np

from .system import *


class Video(list):
    def __init__(self, images=[]):
        super(Video, self).__init__(images)


def save_video(filename, images, fps=20, keep_images=False, verbose=True):
    assert len(images) > 0, len(images)
    assert filename.endswith('.mp4'), filename

    def ffmpeg_cmd(input_pattern, output_filename, fps):
        return f'ffmpeg -y -loglevel warning -framerate {fps} -i {input_pattern} -vcodec libx264 -pix_fmt yuv420p {filename}'

    if not keep_images:
        with tempfile.TemporaryDirectory() as tempdir:
            for i, image in enumerate(images):
                if isinstance(image, str):
                    image = cv2.imread(image)
                cv2.imwrite(f'{tempdir}/{i:06d}.png', image)
            input_pattern = f'{tempdir}/%06d.png'
            shell(ffmpeg_cmd(input_pattern, filename, fps), verbose)

    else:
        dirname = os.path.dirname(filename)
        basename = os.path.splitext(os.path.basename(filename))[0]
        images_dir = os.path.join(dirname, basename)
        mkdir(images_dir)
        for i, image in enumerate(images):
            if isinstance(image, str):
                image = cv2.imread(image)
            cv2.imwrite(f'{images_dir}/{i:06d}.png', image)
        input_pattern = f'{images_dir}/%06d.png'
        shell(ffmpeg_cmd(input_pattern, filename, fps), verbose)


def video_size(video_path):
    vid = cv2.VideoCapture(video_path)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    return (width, height)
