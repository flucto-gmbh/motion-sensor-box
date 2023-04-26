import cv2

my_draw_funcs = []


def add_draw_func(func):
    my_draw_funcs.append(func)


def gui_display(img):
    if len(my_draw_funcs):
        img_copy = img.copy()
        for draw_func in my_draw_funcs:
            draw_func(img_copy)
        cv2.imshow("frame", img_copy)
    else:
        cv2.imshow("frame", img)


def gui_split(source):
    for frame in source:
        gui_display(frame)
        yield frame
