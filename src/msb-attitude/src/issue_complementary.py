import numpy as np
from os import path
import sys


# add ahrs directory to PYTHONPATH
SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))

try:
    from ahrs.ahrs.filters import Complementary
except ImportError as e:
    print(f'failed to import Complementary filter from ahrs: {e}')
    sys.exit(-1)

try:
    from ahrs.ahrs.common import Quaternion
except ImportError as e:
    print(f'failed to import Quaternion from ahrs: {e}')
    sys.exit(-1)



def main():

    gyr = np.array([1, 1, 1])
    acc = np.array([0, 0, -1])
    mag = np.array([2, 22, 2])

    q0 = Quaternion(
        np.array([1,1,1,1])
    )

    complementary = Complementary(
        gyr=np.array([[1, 1, 1]]),
        acc=np.array([[0, 0, -1]]),
        mag=np.array([[2,20,2]]),
        q0=q0
    )

    q_attitude = complementary.update(
        q = q0,
        gyr=gyr,
        acc=acc,
        mag=mag,
    )

    print(f'attitude: {q_attitude}')


if __name__ == '__main__':
    main()

