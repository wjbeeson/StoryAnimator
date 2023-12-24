import time
import os
from pathlib import Path


def rename_dir():
    files = []
    directory = r"C:\Users\wjbee\Desktop\test"
    while True:
        for filename in os.listdir(directory):
            if filename not in files:
                os.rename(directory + "\\" + filename, directory + "\\" + f"{len(files)}" + ".png")
                files.append(str(len(files)) + ".png")

        time.sleep(0.5)


def assemble_gif():
    directory = r"C:\Users\wjbee\Desktop\test"
    files = os.listdir(directory)
    unique_frames = len(files)
    max_pause = 10
    pause_count = 6  # should always be even to start where started
    frames = []
    for i in range(pause_count):
        if i % 2 == 0:
            frames.append(files[i])
        else:
            frames.append(files[unique_frames - pause_count])
            pause_count -= 2
