from os import path
import sys

SCRIPT_DIR = path.dirname(path.abspath(__file__))
sys.path.append(path.dirname(SCRIPT_DIR))


if __name__ == "__main__":
    from msb.serial.publisher import main
    main()
