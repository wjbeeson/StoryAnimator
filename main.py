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
    name="roboto",
    size=60,
    color="white",
    stroke_color="black",
    stroke_width=3,
    highlight_color="orange",
)
y_shift_line = 200
background_clip = VideoFileClip("C:\\Users\\wjbee\\Desktop\\burning-tree-stunning-flames-SBV-346704080-HD.mp4")

with open(script_file, "r") as file:
    script: str = file.read()

#narration_file = generate_narration_file(script, voice, version)

#script_words = script.strip().split(" ")
#raw_timestamps = get_timestamps_from_narration(narration_file)
#timestamps = align_timestamps_with_script(raw_timestamps, script_words)


narration_file = 'temp/68aca237-8c58-4eaa-82f1-a6973f0b8508.wav'


dummy_data = "[['Our', 0.12, 0.3], ['father', 0.3, 0.69], ['who', 0.69, 0.84], ['rolls', 0.84, 1.14], ['in', 1.14, 1.26], ['heaven,', 1.26, 1.77], ['Ameng', 1.8, 2.29], ['be', 2.31, 2.52], ['thy', 2.52, 2.73], ['name.', 2.73, 3.42], ['thy', 3.48, 3.96], ['goats', 3.96, 4.29], ['may', 4.29, 4.47], ['come,', 4.47, 5.01], ['thy', 5.01, 5.34], ['will', 5.34, 5.55], ['be', 5.55, 5.7], ['shattered,', 5.7, 6.21], ['on', 6.21, 6.6], ['earth', 6.6, 6.9], ['as', 6.9, 7.05], ['it', 7.05, 7.17], ['is', 7.17, 7.35], ['in', 7.35, 7.47], ['heaven.', 7.47, 8.1], ['Give', 8.49, 8.94], ['us', 8.94, 9.12], ['this', 9.12, 9.33], ['day', 9.33, 9.63], ['our', 9.63, 9.78], ['daily', 9.78, 10.11], ['cheese,', 10.11, 10.74], ['and', 10.74, 11.01], ['forgive', 11.01, 11.37], ['us', 11.37, 11.52], ['our', 11.52, 11.67], ['throwing,', 11.67, 12.36], ['as', 12.36, 12.72], ['we', 12.72, 12.87], ['forgive', 12.87, 13.29], ['those', 13.29, 13.59], ['who', 13.59, 13.71], ['throw', 13.71, 13.98], ['against', 13.98, 14.37], ['us,', 14.37, 14.79], ['and', 14.79, 15.12], ['lead', 15.12, 15.36], ['us', 15.36, 15.48], ['not', 15.48, 15.75], ['into', 15.75, 15.99], ['Mayhem,', 15.99, 16.65], ['but', 16.65, 17.04], ['deliver', 17.04, 17.43], ['us', 17.43, 17.61], ['from', 17.61, 17.85], ['Justice.', 17.85, 18.66]]"
timestamps = input_hardcoded_values(dummy_data)


animator = ClipAnimator(screen_size)
bbox = Bbox([[192,108],[1728,972]])
positions = typeset_captions(
    animator=animator,
    font=font,
    caption_bb=bbox,
    script=script,
    sync_values=get_sync_values_from_timestamps(timestamps),
    narration_file=narration_file
)
scroll_captions(animator, y_shift_line, positions)
write_video(
    animator=animator,
    caption_bb=bbox,
    narration_file=narration_file,
    background_clip=background_clip,
    screen_size=screen_size
)