from warnings import WarningMessage
import cv2 as cv
import numpy as np
import os
import warnings


def get_meter_templates() -> list:
    templates = []
    template_folder = "image-templates"
    filenames = next(os.walk(template_folder), (None, None, []))[2]  # [] if no file
    for template_name in filenames:
        template = cv.imread(os.path.join(template_folder, template_name), 0)
        number = int(template_name[7:9])
        templates.append((template, number))
    return templates


def find_meter_digits(img_gray, number_templates:list, threshold=0.5, 
    expected_meter_digit=None, expected_ypos=[None, None], expected_digit_boost_factor=1.1, do_write_as_png=False) -> dict:
    """Finds a monopile's meter marking numbers in a given frame

    Args:
        img_gray (Mat): image that shall be searched for meter marking numbers
        number_templates (list of Mat): images of meter marking numbers
        threshold (float, optional): _description_. Defaults to 0.5.
        expected_meter_digit (int, optional): 
        expected_ypos (list of float, optional): interval of the pixel y-position where we expect the expected_meter_digit. 
            Normalized such that 0=top of image, 1=bottom of image.
        expected_digit_boost_factor (float, optional): expected digit will be multiplied with this factor (to prefer expected number)
        do_write_as_png (bool, optional): _description_. Defaults to False.

    Returns:
        dict: _description_
    """
    # Erosion gives us better results.
    # Idea based on https://stackoverflow.com/a/14799188 .
    do_erode_images = True

    #print(f"img_gray.shape {img_gray.shape}")
    # Convert expected y-position to pixels
    if expected_ypos[0] is not None:
        expected_ypos[0] = int(img_gray.shape[0] * expected_ypos[0])
        expected_ypos[1] = int(img_gray.shape[0] * expected_ypos[1])

    if do_erode_images: 
        img_gray = img_gray- cv.erode(img_gray, None)


    all_res = []
    highest_maxVal = 0
    highest_maxVal_unboosted = 0
    found_m_number = None
    x = None
    for template, number in number_templates:
        if do_erode_images:
            template = template - cv.erode(template, None)
        res = cv.matchTemplate(img_gray,template, cv.TM_CCOEFF_NORMED)
        all_res.append(res)
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(res)
        #print(f"Number {number} with maxVal={maxVal}")
        maxVal_unboosted = maxVal
        if number == expected_meter_digit:
            print(f"Number {number} with maxVal={maxVal} is expected number.")
            print(f"maxLoc[0]: {maxLoc}, expected_ypos: {expected_ypos}")
            if maxLoc[1] >  expected_ypos[0] and maxLoc[1] < expected_ypos[1]:
                print(f"Number {number} with maxVal={maxVal} is in y-range and gets expected_digit_boost_factor boost.")
                maxVal = expected_digit_boost_factor * maxVal 
        #print(f"maxVal: {maxVal}, number: {number}, location: {maxLoc}")
        if maxVal > highest_maxVal:
            #print(f"NEW WINNER: Number {number} with maxVal={maxVal}")
            highest_maxVal = maxVal
            highest_maxVal_unboosted = maxVal_unboosted
            found_m_number = number
            template_w, template_h = template.shape[::-1]

            loc = np.where(res == highest_maxVal_unboosted) # Find best matching template.
            if len(loc[0]) > 0 and maxVal > threshold: # Check wheter it matches better than the threshold.
                if do_write_as_png:
                    for pt in zip(*loc[::-1]):
                        img_rgb = cv.cvtColor(img_gray, cv.COLOR_GRAY2RGB)
                        cv.rectangle(img_rgb, pt, (pt[0] + template_w, pt[1] + template_h), (0,0,255), 2)
                        text_xy = (pt[0] + 1, pt[1] + int(0.5 * template_h))
                        cv.putText(img_rgb, str(found_m_number), text_xy, cv.FONT_HERSHEY_PLAIN, 
                            2.0, (0,0,255), thickness=1, lineType=cv.LINE_AA)
                        cv.imwrite('template_matching_result.png',img_rgb)
                if len(loc[0]) > 1:
                    warnings.warn(f"len(loc[0]) = {len(loc[0])}. Multiple locations with the same goodness score for template matching have been found. Continuing with the location with index=0.")
                    (x, y) = int(loc[1][0]), int(loc[0][0])
                else:
                    (x, y) = int(loc[1]), int(loc[0])

    res = None
    if x is not None:
        res = {"found_m_number": found_m_number, "number_xy": (x, y), 
            "number_wh": (template_w, template_h), "goodness": highest_maxVal_unboosted}

    return res


if __name__ == "__main__":
    #img_rgb = cv.imread("ocr_test.png")
    #img_rgb = cv.imread("figs/video_pile-run/pile-run.mp4_1650.jpg")
    img_rgb = cv.imread("figs/video_5-36-56(2)/Aft Door Camera_urn-uuid-00306F00-0030-6F4A-155B-00306F4A155B_2022-07-09_05-36-56(2).mp4_42000.jpg")

    if img_rgb is None:
        raise FileNotFoundError
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    res = find_meter_digits(img_gray, 0.5, True)
    print("Meter marking digits: " + str(res))