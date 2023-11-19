from narration import *
from timestamps import *
from forge.forge_video import *
from forge.clipanimator.clipanimator import ClipAnimator
from matplotlib.transforms import Bbox
from forge.typesetter import *
script_file = "C:\\Users\\wjbee\\Desktop\\Example File.txt"
voice = 'chad'
version = "eleven_multilingual_v2"
screen_size = (1920, 1080)
font = Font(
    name="Ariel",
    size=20,
    color="white",
    stroke_color="pink",
    stroke_width=5,
    highlight_color="blue",
)

with open(script_file, "r") as file:
    script: str = file.read()

#narration_file = generate_narration_file(script, voice, version)
narration_file = "C:\\Users\\wjbee\\PycharmProjects\\RedditScriptAnimator\\temp\\b795653f-0621-487f-97ac-834930a7fcf4.wav"

#script_words = script.strip().split(" ")
#raw_timestamps = get_timestamps_from_narration(narration_file)
#timestamps = align_timestamps_with_script(raw_timestamps, script_words)
dummy_data = "[['So', 0.03, 0.21], ['to', 0.21, 0.33], ['recap,', 0.33, 1.02], ['I', 1.02, 1.38], ['(38F)', 1.38, 1.89], ['had', 2.13, 2.34], ['an', 2.34, 2.46], ['affair', 2.46, 2.76], ['with', 2.76, 2.91], ['my', 2.91, 3.09], ['coworker.', 3.09, 3.9]]"
timestamps = input_hardcoded_values(dummy_data)


animator = ClipAnimator(screen_size)
bbox = Bbox([[0,0],[1920,1080]])
typeset_captions(
    animator=animator,
    font=font,
    caption_bb=bbox,
    script=script,
    sync_values=get_sync_values_from_timestamps(timestamps)

)
