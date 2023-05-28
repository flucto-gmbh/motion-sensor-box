from .VideoFormatSource import video_format_source
from .WebCamSource import webcam_source
from .PiCamSource import picam3_source
from .VideoSequenceSource import video_sequence_source
from .VideoGUISource import gui_split

available_sources = {
    "picam3" : picam3_source,
    "webcam": webcam_source,
    "file": video_sequence_source,
    "video": video_format_source,
    "gui": gui_split,
    "default": webcam_source(0),
}


def video_source(name, args):
    if name in available_sources:
        return available_sources[name](args)
    else:
        print(f"Video source {name} not found. Available sources: {available_sources.keys()}")
        print("Using default source: Webcam")
        return available_sources["default"]
