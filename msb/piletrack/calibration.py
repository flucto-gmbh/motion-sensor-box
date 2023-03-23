import numpy as np
from scipy.optimize import curve_fit

def calibration_function(x: np.array, a=None, b=None, c=None, cam="osbit_aft_door") -> np.array:
    """Function for converting a y-pixel distance into a meter distance given a x-pixel value. N pixel = 1 meter.


    Args:
        x (np.array): x-pixel position(s)
        a (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        b (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        c (float): parameter of the calibration function. Defaults to None - then presaved values based on cam keyword are used.
        cam (str, optional): Camera name (different cameras has different presaved calibration functions). 
            Defaults to "osbit_aft_door".

    Returns:
        np.array: meter distance(s)
    """
    x = np.array(x)

    if a is None and b is None and c is None:
        if cam == "osbit_aft_door":
            a = 1.69453802e-02
            b = 6.47904637e+02
            c = 2.75114714e+02
        elif cam == "action_cam_bridge_deck":
            a = 0
            b = 0
            c = 10.5
        else:
            raise NotImplementedError

    return -1 * (a * (x - b)) ** 2 + c


def px_to_m_conversion_factor(x, fname="x", do_calibration_fit=False, do_plot_calibration_curve=False):
    """
    Caclulates the conversion factor between y-pixel- distance and m-pixel distance given a x-pixel value.
    """

    dist_51m_to_special_marking = 1.48 # See 'calibration2.jpg' and '19A502-JBO-DWSMDD-EN-4019-06_Monopile - Paint  Markings.pdf'

    # Left image section (with special marking; from image 'calibration2.jpg')
    x_pos = [115, 193, 294]
    n_pixel_is_1m = (np.asarray([275, 328, 361]) / dist_51m_to_special_marking).tolist()

    # Middle image section (with meter markings; from image 'calibration1.jpg')
    x_pos.extend([848, 938, 1018])
    n_pixel_is_1m.extend([258, 248, 239])


    # Right image section (with special marking; from image 'calibration2.jpg'')
    x_pos.extend([1178, 1231])
    n_pixel_is_1m.extend((np.asarray([298, 256]) / dist_51m_to_special_marking).tolist())

    if do_calibration_fit:
        popt, _ = curve_fit(calibration_function, x_pos, n_pixel_is_1m)     
        a, b, c = popt # Unpack optima parameters for the objective function.
        print("popt: " + str(popt))
    else: 
        # y = np.interp(x, x_pos, n_pixel_is_1m) # Alternative to calibration function: just linearly interpolate
        #a = 1.69453802e-02
        #b = 6.47904637e+02
        #c = 2.75114714e+02
        y = calibration_function(x, cam=cam)
        #print("cam: " + str(cam))
        #print("calibration y: " + str(y))



    if do_plot_calibration_curve:
        x_new = np.arange(80, 1260, 10)
        y_new = calibration_function(x_new) # Use optimal parameters to calculate new values

        fig, ax = plt.subplots()
        ax.plot(x_pos, n_pixel_is_1m, '.b')
        ax.plot(x_pos, n_pixel_is_1m, '-b')
        ax.plot(x_new, y_new, '-r')
        x_text = 80
        ax.text(x_text, 270, 'Calibration curve', color='r')
        formula = f"-1 * ({a:.3f} * (x - {b:.0f})) ** 2 + {c:.0f}"
        ax.text(x_text, 265, formula, color='r', fontsize=6)
        ax.add_patch(Rectangle((848, 175), 1018-848, 105, facecolor='k', edgecolor='none', fill=True, alpha=0.3))
        ax.text(848, 175, "Meter markings", color='k', fontsize=6)
        #ax.plot(x, y, 'xr')
        plt.xlabel('x-Position (pixel)')
        plt.ylabel('y-pixel distance that equals 1 m')
        plt.show()

    # For videos with reduced resolution the px-to-m is different.
    if "small-res" in fname:
        y *= 478 / 1080
        
    one_pixel_is_x_m = 1 / y

    return one_pixel_is_x_m

fps = 30


