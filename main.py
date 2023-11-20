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

with open(script_file, "r") as file:
    script: str = file.read()

#narration_file = generate_narration_file(script, voice, version)
narration_file = "temp/2339b1ea-2681-4397-8f1d-f6c104d485b0.wav"

#script_words = script.strip().split(" ")
#raw_timestamps = get_timestamps_from_narration(narration_file)
#timestamps = align_timestamps_with_script(raw_timestamps, script_words)
dummy_data = "[['Our', 0.12, 0.33], ['father', 0.33, 0.69], ['who', 0.69, 0.84], ['rolls', 0.84, 1.2], ['in', 1.2, 1.35], ['heaven,', 1.35, 1.86], ['Ameng', 1.89, 2.37], ['be', 2.4, 2.58], ['thy', 2.58, 2.82], ['name.', 2.82, 3.51], ['thy', 3.75, 4.17], ['goats', 4.17, 4.5], ['may', 4.5, 4.68], ['come,', 4.68, 5.13], ['thy', 5.13, 5.4], ['will', 5.4, 5.61], ['be', 5.61, 5.76], ['shattered,', 5.76, 6.42], ['on', 6.42, 6.84], ['earth', 6.84, 7.2], ['as', 7.2, 7.41], ['it', 7.41, 7.56], ['is', 7.56, 7.77], ['in', 7.77, 7.89], ['heaven.', 7.89, 8.46], ['Give', 8.55, 9.0], ['us', 9.0, 9.15], ['this', 9.15, 9.36], ['day', 9.36, 9.66], ['our', 9.66, 9.81], ['daily', 9.81, 10.14], ['cheese,', 10.14, 10.8], ['and', 10.8, 11.1], ['forgive', 11.1, 11.46], ['us', 11.46, 11.61], ['our', 11.61, 11.79], ['throwing,', 11.79, 12.42], ['as', 12.42, 12.78], ['we', 12.78, 12.9], ['forgive', 12.9, 13.29], ['those', 13.29, 13.56], ['who', 13.56, 13.71], ['throw', 13.71, 13.98], ['against', 13.98, 14.37], ['us,', 14.37, 14.76], ['and', 14.76, 15.12], ['lead', 15.12, 15.36], ['us', 15.36, 15.51], ['not', 15.51, 15.75], ['into', 15.75, 16.02], ['Mayhem,', 16.02, 16.74], ['but', 16.74, 17.13], ['deliver', 17.13, 17.55], ['us', 17.55, 17.7], ['from', 17.7, 17.91], ['Justice.', 17.91, 18.72]]"
timestamps = input_hardcoded_values(dummy_data)


animator = ClipAnimator(screen_size)
bbox = Bbox([[192,108],[1728,972]])
typeset_captions(
    animator=animator,
    font=font,
    caption_bb=bbox,
    script=script,
    sync_values=get_sync_values_from_timestamps(timestamps),
    narration_file=narration_file
)
scroll_captions(animator, y_shift_line)
breakpoint()
write_video(
    animator=animator,
    caption_bb=bbox,
    narration_file=narration_file
)