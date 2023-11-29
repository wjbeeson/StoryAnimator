# from narration import *
from timestamps import *
# from forge.forge_video import *
# from forge.clipanimator.clipanimator import ClipAnimator
# from matplotlib.transforms import Bbox
from forge.typesetter import *
from CharacterTimestamp import CharacterTimestamp

script_file = "test/test_script.txt"
voice = 'chad'
version = "eleven_multilingual_v2"
screen_size = (1920, 1080)
font = Font(
    name="roboto",
    size=120,
    color="white",
    stroke_color="black",
    stroke_width=3,
    highlight_color="purple",
)
y_shift_line = 800
# background_clip = VideoFileClip("C:\\Users\\wjbee\\Desktop\\abstract-looped-spinning-planet-purple-hi-tech-luminous-round-sphere-in-space-again-SBV-347806923-HD.mp4")

with open(script_file, "r") as file:
    script: str = file.read()

# narration_file = generate_narration_file(script, voice, version)

delimiters = [" ", "\n"]
# for delimiter in delimiters:
#    string = " ".join(script.split(delimiter))
# script_words = string.split()
# raw_timestamps = get_timestamps_from_narration(narration_file)
# timestamps = align_timestamps_with_script(raw_timestamps, script_words)

character_timestamps = {}
narration_file = 'test/test_narration.wav'

dummy_data = "[['Our', 0.08, 0.32], ['father', 0.32, 0.68], ['who', 0.68, 0.83], ['rolls', 0.83, 1.16], ['in', 1.16, 1.31], ['heaven,', 1.31, 1.91], ['Ameng', 1.94, 2.31], ['be', 2.33, 2.48], ['thy', 2.48, 2.69], ['name.', 2.69, 3.35], ['thy', 3.44, 3.86], ['goats', 3.89, 4.16], ['may', 4.16, 4.37], ['come,', 4.37, 4.73], ['thy', 4.73, 4.91], ['will', 4.91, 5.09], ['be', 5.12, 5.24], ['shattered,', 5.24, 5.78], ['on', 5.81, 6.08], ['earth', 6.08, 6.41], ['as', 6.41, 6.56], ['it', 6.56, 6.71], ['is', 6.71, 6.86], ['in', 6.86, 7.01], ['heaven.', 7.01, 7.58], ['Give', 7.97, 8.39], ['us', 8.39, 8.57], ['this', 8.57, 8.81], ['day', 8.81, 9.05], ['our', 9.08, 9.26], ['daily', 9.26, 9.59], ['cheese,', 9.59, 10.27], ['and', 10.28, 10.58], ['forgive', 10.58, 10.94], ['us', 10.94, 11.12], ['our', 11.12, 11.3], ['throwing,', 11.3, 11.86], ['as', 11.87, 12.2], ['we', 12.2, 12.35], ['forgive', 12.35, 12.71], ['those', 12.71, 13.01], ['who', 13.01, 13.13], ['throw', 13.16, 13.43], ['against', 13.43, 13.85], ['us,', 13.85, 14.15], ['and', 14.15, 14.48], ['lead', 14.48, 14.72], ['us', 14.72, 14.9], ['not', 14.9, 15.14], ['into', 15.14, 15.38], ['Mayhem,', 15.38, 16.16], ['but', 16.16, 16.58], ['deliver', 16.58, 17.0], ['us', 17.0, 17.15], ['from', 17.15, 17.42], ['Justice.', 17.42, 18.29]]"
timestamps = input_hardcoded_values(dummy_data)

contents = "character, start_time, end_time\n"
for timestamp in list(timestamps):
    formatted_content = ""
    for character in timestamp.content:
        if character == "\n":
            character = "\\n"
        if character == ",":
            character = "\\c"
        formatted_content += character

    contents += f"{formatted_content}, {round(timestamp.start_time, 2)}, {round(timestamp.end_time, 2)}\n"
contents = contents[0:len(contents)-1]  # remove last newline
f = open("test/charmap.csv", "w")
f.write(contents)
f.close()
'''
# calc delays

delays = []
for i, timestamp in enumerate(timestamps):
    timestamp: Word
    if i == 0:
        delays.append(timestamp.start_time)
    else:
        delays.append(timestamp.start_time - timestamps[i - 1].start_time)
i = 0
copy_script = script
for j, timestamp in enumerate(timestamps):

    # Step 1: calculate key variables
    word = timestamp.content
    start_pos = copy_script.find(word)
    end_pos = start_pos + len(word) - 1

    # Step 2: adding back delimiters to words
    if (end_pos + 1) < len(copy_script):
        while copy_script[end_pos + 1] in delimiters:
            end_pos = end_pos + 1

    # Step 3: create string of characters to associate with timestamp
    chars_to_add = copy_script[start_pos:end_pos + 1]

    # Step 4: initialize character timestamps at time 0
    char = ""
    for char in chars_to_add:  # makes all chars start and end at time 0
        character_timestamps[i] = CharacterTimestamp(char, 0, 0)
        i = i + 1

    # Step 5: add appearance delays
    if j == 0:  # add start delay if very first word
        character_timestamps[0] = CharacterTimestamp(copy_script[0], delays[j])
    if j >= len(delays) - 1:  # add delay after last word
        character_timestamps[i - 1] = CharacterTimestamp(char, 0)
    else:  # add delay to last char of word
        character_timestamps[i - 1] = CharacterTimestamp(char, delays[j + 1])

    # Step 6: add disappearance delays
    if j == 0:  # add start delay if very first word
        character_timestamps[0].disappearance_delay = 0
    if j >= len(delays) - 1:  # add delay after last word
        character_timestamps[i - 1].disappearance_delay = 0
    else:  # add delay to last char of word
        character_timestamps[i - 1].disappearance_delay = 0

    # Step 7: iterate copy script
    copy_script = copy_script[end_pos:len(copy_script) + 1]
'''
'''
contents = "character, appearanceDelay, disappearanceDelay\n"
for char_timestamp in list(character_timestamps.values()):
    if char_timestamp.character == "\n":
        char_timestamp.character = "\\n"
    if char_timestamp.character == ",":
        char_timestamp.character = "\\c"
    contents += f"{char_timestamp.character}, {round(char_timestamp.appearance_delay, 2)}, {round(char_timestamp.disappearance_delay, 2)}\n"
contents = contents[0:len(contents)-1]  # remove last newline
f = open("test/charmap.csv", "w")
f.write(contents)
f.close()
f2 = open("test/charmap.txt", "w")
f2.write(contents)
f2.close()


breakpoint()
'''
'''
animator = ClipAnimator(screen_size)
bbox = Bbox([[192,108],[1728,999999999999999999999]])
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
'''
