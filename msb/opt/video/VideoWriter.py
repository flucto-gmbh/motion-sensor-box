import cv2
from msb.opt.config import OptConf

def write_frame(img):
    pass

def get_output_fname(config: OptConf):
    return "output.avi"

def write_split(config: OptConf, source):
    # open video writer:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter(get_output_fname(config), fourcc, config.fps, (config.width, config.height))

    for frame in source:

        yield frame
