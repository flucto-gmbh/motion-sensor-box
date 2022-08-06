import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from msb_config.MSBConfig import MSBConfig

class CameraConfig(MSBConfig):
    def __init__(self, subconf = "msb-camera"):
        super().__init__()
        self._load_conf(subconf=subconf)
        self._parse_cmdline_args()
        self._cmdline_config_override()
        self._create_video_dir

    def _create_video_dir(self):
        if not os.path.isdir(self.video_dir):
            print(f"no such file or directory: {self.video_dir}, creating")
        try:
            os.makedirs(self.video_dir, exist_ok=True)
        except Exception as e:
            print(f"failed to create data directory {self.video_dir} : {e}")
            print(f"falling back to $HOME/msb_data/cam")
            self.video_dir = path.join(path.join(os.environ["HOME"], "msb_data"), "cam")
            self._create_video_dir()


    def _parse_cmdline_args(self):
        args = argparse.ArgumentParser()

        args.add_argument(
            "--verbose",
            action="store_true",
            help="output debugging information"
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
            "--rollover-period",
            type=int,
            help="time after which a new video file is generated"
        )

        args.add_argument(
            "--video-dir",
            type=str,
            help="directory to store videos in"
        )
        cmdline_conf = args.parse_args().__dict__
        self._cmdline_conf = cmdline_conf

    def _cmdline_config_override(self):
        if self._cmdline_conf['verbose'] and not self.verbose:
            print(f"overriding verbose flag with command line flag")
            self.verbose = True

        if self._cmdline_conf['print_stdout'] and not self.print_stdout:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding print flag with command line flag")
            self.print_stdout = True

        if self._cmdline_conf['fps']:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding fps setting with command line flag: {self._cmdline_conf['fps']}")
            self.fps = self._cmdline_conf["fps"]
        
        if self._cmdline_conf['width']:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding width setting with command line flag: {self._cmdline['width']}")
            self.width = self._cmdline_conf["width"]

        if self._cmdline_conf['height']:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding height setting with command line flag: {self._cmdline['height']}")
            self.height = self._cmdline_conf["height"]
        
        if self._cmdline_conf['rollover_period']:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding rollover period setting with command line flag: {self._cmdline['rollover_period']}")
            self.rollover_period = self._cmdline_conf["rollover_period"]
        
        if self._cmdline_conf['video_dir']:
            if self._cmdline_conf['verbose'] or self.verbose:
                print(f"overriding video dir setting with command line flag: {self._cmdline['video_dir']}")
            self.video_dir = self._cmdline_conf["video_dir"]

if __name__ == "__main__":
    config = CameraConfig()
    if config.verbose:
        print(json.dumps(config.__dict__, indent=4))
