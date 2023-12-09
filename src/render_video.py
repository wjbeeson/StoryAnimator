import random
import shutil

import ffmpeg
import os
from tkinter.filedialog import askdirectory


import pandas as pd
import uuid
import cv2
import moviepy
from moviepy.editor import *
import numpy as np
from datetime import datetime
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def probe_video(video_path):
    probe = ffmpeg.probe(video_path)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if stream is None:
        raise Exception(f"File: {video_path} is not a valid file, and is likely corrupted.")
    duration = float(stream['duration'])

    fps_raw = stream['avg_frame_rate']
    fps_split = fps_raw.split("/")
    fps = float(int(fps_split[0]) / int(fps_split[1]))

    video_width = int(stream['width'])

    video_height = int(stream['height'])

    return (duration, fps, video_width, video_height)
def add_background(overlay_path, background_path, chroma_key_hex="#00FF00"):
    duration = probe_video(overlay_path)[0]
    greenscreen_overlay = (
        ffmpeg.input(overlay_path)
        .filter(filter_name="chromakey", color=chroma_key_hex, similarity=0.05, blend=0.2)
        .filter(filter_name="despill", type="green")
    )
    final_video_path = f"temp.mp4"
    (
        ffmpeg
        .overlay(
            main_parent_node=ffmpeg.input(background_path),
            overlay_parent_node=greenscreen_overlay,
            x="(W-w)/2",
            y="(H-h)/2")
        .trim(duration=duration)
        .output(final_video_path)
        .run(overwrite_output=True)
    )
    return final_video_path

def add_narration(narration_path, video_path):
    input_video = ffmpeg.input(video_path)

    input_audio = ffmpeg.input(narration_path)

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output("C:\\Users\\wjbee\\Desktop\\Raptor_Assets").run()


add_background("C:\\Users\\wjbee\\JSProjects\\Remotion\\out\\short_slim_test.mp4", "C:/Users/wjbee/JSProjects/Remotion/public/background.mp4")
