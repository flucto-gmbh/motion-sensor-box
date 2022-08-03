import cv2 as cv
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import Rectangle
import numpy as np
import os
import pandas as pd
from scipy.optimize import curve_fit
import signal
import sys
import time
from tkinter import E
import video

from pile_vision import find_meter_digits, get_meter_templates

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from PileTrackConfig import PileTrackConfig
from msb_config.zeromq import open_zmq_pub_socket

# TODO
# - open camera stream an show it
# - implement simple tracking
# - implement calculations

def signal_handler(sig, frame):
    print('msb_piletrack.py exit')
    sys.exit(0)

def msb_piletrack(piletrack_config : PileTrackConfig):
    signal.signal(signal.SIGINT, signal_handler)
    zmq_pub_socket = open_zmq_pub_socket(piletrack_config.zmq["xsub_connect_string"]),
    # 2. open camera
    # 3. iterate over frames
    # 4. track features
    # 5. calculate speed and send to zmq

if __name__ == "__main__":
    piletrack_config = PileTrackConfig()
    msb_piletrack(piletrack_config)
