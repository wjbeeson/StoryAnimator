from narration import *
from timestamps import *

text_file = "C:\\Users\\wjbee\\Desktop\\Example File.txt"
voice = 'chad'
version = "eleven_multilingual_v2"

with open(text_file, "r") as file:
    content: str = file.read()
narration_file = generate_narration_file(content, voice, version)
timestamps = get_timestamps_from_narration(content, narration_file)
breakpoint()