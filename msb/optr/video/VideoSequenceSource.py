import os
import cv2


def get_files(img_dir):
    file_names = os.listdir(img_dir)
    return [os.path.join(img_dir, f) for f in file_names]


def video_sequence_source(img_dir_or_files):
    if type(img_dir_or_files) == list:
        img_files = img_dir_or_files
    elif os.path.isdir(img_dir_or_files):
        img_files = get_files(img_dir_or_files)

    for img_file in (img_files):
        yield cv2.imread(img_file)
