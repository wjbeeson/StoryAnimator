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
import os


def render_video(meme_dir, background_file):
    if not os.path.isfile(memefile_path):
        raise Exception(f"Invalid Path: {memefile_path}")

    remotion_dir = "C:\\Users\\wjbee\\JSProjects\\Remotion"
    remotion_out_file = "\\out\\VideoComp.mp4"
    os.chdir(remotion_dir)
    os.system("npx Remotion render VideoComp")
    out_file = f"C:\\Users\\wjbee\\Desktop\\Raptor\\out\\{uuid.uuid4()}.mp4"

    add_background(f"{remotion_dir}{remotion_out_file}", background_file, out_file)
    pass


def render_remotion_overlay():
    pass


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


def add_background(overlay_path, background_path, output_path, chroma_key_hex="#0000FF"):
    duration = probe_video(overlay_path)[0]
    greenscreen_overlay = (
        ffmpeg.input(overlay_path)
        .filter(filter_name="chromakey", color=chroma_key_hex, similarity=0.2, blend=0.3)
        .filter(filter_name="despill", type="blue")
    )
    video = (
        ffmpeg
        .overlay(
            main_parent_node=ffmpeg.input(background_path),
            overlay_parent_node=greenscreen_overlay,
            x="(W-w)/2",
            y="(H-h)/2")
        .trim(duration=duration)  # TODO: Replace with duration
        # .output(final_video_path)
        # .run(overwrite_output=True)
    )
    audio = ffmpeg.input(overlay_path).audio.filter("atrim", duration=duration)
    input_video = video
    input_audio = audio

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path).run(overwrite_output=True)


render_video(meme_dir=r"C:\Users\wjbee\Desktop\Raptor\scripts\Part_1",
             background_file=r"C:\Users\wjbee\Desktop\Raptor\backgrounds\parkour-2-of-3.mp4")
