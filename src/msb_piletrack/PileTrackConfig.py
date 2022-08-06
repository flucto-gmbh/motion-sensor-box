import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

class PileTrackConfig(MSBConfig):

    _roi_coords = ["x1", "y1", "x2", "y2"]

    def __init__(self, subconf = "msb-piletrack"):
        super().__init__()
        self._load_conf(subconf=subconf)
        self._parse_cmdline_args()
        self._cmdline_config_override()

    def _parse_cmdline_args(self):
        """
        msb-piletrack:
            verbose : false
            show_video : false     # requires a running desktop environment!
            print_stdout : false
            fps : 10
            width : 1280
            height : 720
            record_video : false
            region_of_interest : 
                x1 : 0.2
                y1 : 0.2
                x2 : 0.8
                y2 : 0.8
            max_number_of_features : 5
            max_track_length : 10
            pile_speed_detection_interval : 5
            track_meter_markings : false
            meter_markings_score_threshold : 0.4
            meter_markings_region_of_interest:
                x1 : 0.8
                y1 : 0.2
                x2 : 0.9
                y2 : 0.8
            meter_markings_detection_interval : 10
        """

        args = argparse.ArgumentParser()

        args.add_argument(
            "--verbose",
            action="store_true",
            help="output debugging information"
        )

        args.add_argument(
            "--show-video",
            action="store_true",
            help="display the video stream. WARNING: requires a running desktop environment and puts a considerable load on the system"
        )

        args.add_argument(
            "--print-stdout",
            action="store_true",
            help="print raw data to stdout",
        )

        args.add_argument(
            "--fps",
            type=int,
            help="frames per second"
        )

        args.add_argument(
            "--width",
            type=int,
            help="width of video"
        )

        args.add_argument(
            "--height",
            type=int,
            help="height of video"
        )

        args.add_argument(
            "--rotate",
            action="store_true",
            help="rotate video 90 deg counterclockwise"
        )
        
        args.add_argument(
            "--record-video",
            action="store_true",
            help="store recordings of tracks locally"
        )

        args.add_argument(
            "--region-of-interest",
            type=str,
            help="region of interest as a dictionary. Example: {x1:0.2,y1:0.2,x2:0.8,y2:0.8}"
        )

        args.add_argument(
            "--max-number-of-features",
            type=int,
            help="minimum number of features required to successfully track a pile"
        )

        args.add_argument(
            "--max-track-length",
            type=int,
            help="maximal length of feature tracks in pixels"
        )

        args.add_argument(
            "--pile-speed-update-interval",
            type=int,
            help="interval in frames at which pile speed is calculated"
        )

        args.add_argument(
            "--px-to-m",
            type=float,
            help="conversion ratio from pixels to meters"
        )

        args.add_argument(
            "--track-meter-markings",
            action="store_true",
            help="WARNING: experimental feature. Tracks meter markings on monopile to calculate self weight penetration depth"
        )

        args.add_argument(
            "--meter-markings-score-threshold",
            type=float,
            help="template matching algorithm score threshold for number detection"
        )

        args.add_argument(
            "--meter-markings-region-of-interest",
            type=str,
            help="region of interest for tracking meter markings on the monopile. Example: {x1:0.2,y1:0.2,x2:0.8,y2:0.8}."
        )

        args.add_argument(
            "--meter-markings-calculation-interval",
            type=int,
            help="interval in frames at which pile speed is calculated"
        )

        args.add_argument(
            "--meter-markings-update-interval",
            type=int,
            help="interval in frames at which the meter markings are matched to calculate self weight penetration depth"
        )

        cmdline_conf = args.parse_args().__dict__
        self._cmdline_conf = cmdline_conf

    def _cmdline_config_override(self):
        if self._cmdline_conf['verbose'] and not self.verbose:
            print(f"overriding verbose flag with command line flag")
            self.verbose = True

        if self._cmdline_conf['show_video']:
            self._print_verbose("overriding show video flag using command line input. WARNING: requires a running desktop environment")
            self.show_video = True

        if self._cmdline_conf['print_stdout'] and not self.print_stdout:
            self._print_verbose(f"overriding print flag with command line flag")
            self.print_stdout = True

        if self._cmdline_conf['fps']:
            self._print_verbose(f"overriding fps setting with command line flag: {self._cmdline_conf['fps']}")
            self.fps = self._cmdline_conf["fps"]
        
        if self._cmdline_conf['width']:
            self._print_verbose(f"overriding width setting with command line flag: {self._cmdline['width']}")
            self.width = self._cmdline_conf["width"]

        if self._cmdline_conf['height']:
            self._print_verbose(f"overriding height setting with command line flag: {self._cmdline['height']}")
            self.height = self._cmdline_conf["height"]
        
        if self._cmdline_conf['rotate']:
            self._print_verbose(f"overriding rotate flag with command line flag: rotating video by 90 deg counterclockwise")
            self.rotate = True

        if self._cmdline_conf['record_video']:
            self._print_verbose("overriding record_video flag using command line")
            self.record_video = True

        if self._cmdline_conf['region_of_interest']:
            self._print_verbose("overrding region of interest via command line: {self._cmdline_conf['region_of_interest']}")
            self.region_of_interest = self._parse_pile_tracking_roi()

        if self._cmdline_conf['max_number_of_features']:
            self._print_verbose(f"overriding max. number of features via command line. Now tracking {self._cmdline_conf['max_number_of_features']} features")
            self.number_of_features = self._cmdline_conf['max_number_of_features']

        if self._cmdline_conf['max_track_length']:
            self._print_verbose(f"overriding max track length parameter using command line. New max track length is {self._cmdline_conf['max_track_length']}")
            self.max_track_length = self._cmdline_conf['max_track_length']

        if self._cmdline_conf['pile_speed_update_interval']:
            self._print_verbose(f"overriding pile speed calculation interval via command line. Calculating pile speed every {self._cmdline_conf['pile_speed_update_interval']} frames")
            self.pile_speed_calculation_interval = self._cmdline_conf['pile_speed_calculation_interval']
        
        if self._cmdline_conf['px_to_m']:
            self._print_verbose(f"overriding pixels to meter ratio via command line. Pixels to meters ratio is now {self._cmdline_conf['px_to_m']} frames")
            self.px_to_m = self._cmdline_conf['px_to_m']

        if self._cmdline_conf["track_meter_markings"]:
            self._print_verbose("overriding meter marking tracking flag")
            self.track_meter_markings = True

        if self._cmdline_conf['meter_markings_score_threshold']:
            self._print_verbose(f"overriding meter markings score threshold via command line. Meter marking score threshold is now {self._cmdline_conf['meter_markings_score_threshold']}")
            self.meter_markings_score_threshold = self._cmdline_conf["meter_markings_score_threshold"]

        if self._cmdline_conf["meter_markings_region_of_interest"]:
            self._print_verbose(f"overriding meter markings region of interest via command line. Meter markings region of interest is now {self._cmdline_conf['meter_markings_region_of_interest']}")
            self.meter_markings_region_of_interest = self._parse_meter_markings_roi()

        if self._cmdline_conf["meter_markings_update_interval"]:
            self._print_verbose(f"overriding meter markings calculation interval via command line. Now calculating meter marking position every {self._construct_zmq_socketstrings['meter_markings_calculation_interval']} frames")
            self.meter_markings_calculation_interval = self._cmdline_conf['meter_markings_calculation_interval']

    def _parse_pile_tracking_roi(self):
        raise NotImplementedError("not implemented yet")

    def _parse_meter_markings_roi(self):
        raise NotImplementedError("not implemented yet")

if __name__ == "__main__":
    config = PileTrackConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
