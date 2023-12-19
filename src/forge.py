import shutil
from pathlib import Path
import ffmpeg
from transform_meme import transform_meme
import os
import random
import json


def forge_meme(meme_filename, remotion_output_dirname=r"C:\Users\wjbee\JSProjects\Remotion\out"):
    file_choice = random.choice(os.listdir(r"C:\Users\wjbee\Desktop\Raptor\backgrounds\Looping"))

    # Step 0: Get all the necessary files to render
    background_filename = f"C:\\Users\\wjbee\\Desktop\\Raptor\\backgrounds\\{file_choice}"
    transform_meme(meme_filename)

    # Step 1: Copy all required files over to remotion directory
    meme_filepath = Path(meme_filename)
    remotion_output_dirpath = Path(remotion_output_dirname)
    remotion_public_dirname = str(remotion_output_dirpath.parent) + "\\public\\"

    narration = str(meme_filepath.with_suffix(".wav"))
    props = str(meme_filepath.with_suffix(".ts"))
    remotion_narration_filename = (remotion_public_dirname + str(Path(narration).name)).replace("\\", "/")
    remotion_props_filename = (remotion_public_dirname + str(Path(props).name)).replace("\\", "/")
    shutil.copy(narration, remotion_narration_filename)
    shutil.copy(props, remotion_props_filename)

    # Step 2: Compile parameters for calling remotion render
    narration_local_path = str(Path(remotion_narration_filename).name)
    props_local_path = str(Path(remotion_props_filename).stem)
    json_obj = {}
    json_obj["narrationFilename"] = narration_local_path
    json_obj["propsFilename"] = props_local_path
    json_txt = json.dumps(json_obj)
    json_filename = str(meme_filepath.with_suffix(".json"))
    with open(json_filename, "w") as outfile:
        outfile.write(json_txt)
    command = f"npx remotion render VideoComp out/{meme_filepath.stem}.mp4 --props={str(meme_filepath.with_suffix('.json'))}"

    # Step 3: Call the remotion render function and pass the parameters
    os.chdir(str(remotion_output_dirpath.parent))
    os.system(command)

    # Step 4: After done, use ffmpeg to greenscreen the background file on
    add_background(overlay_path=f"{remotion_output_dirname}\\{meme_filepath.stem}.mp4",
                   background_filename=background_filename,
                   output_path=str(meme_filepath.with_suffix(".mp4")))


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


def add_background(overlay_path, background_filename, output_path, chroma_key_hex="#0000FF"):
    music_file = r"C:\Users\wjbee\Desktop\Raptor\backgrounds\deep_sleep.mp3"
    duration = probe_video(overlay_path)[0]
    (bg_duration, bg_fps) = probe_video(background_filename)[0:2]
    bg_frames = int(bg_duration * bg_fps)
    greenscreen_overlay = (
        ffmpeg.input(overlay_path)
        .filter(filter_name="chromakey", color=chroma_key_hex, similarity=0.2, blend=0.3)
        .filter(filter_name="despill", type="blue")
    )
    video = (
        ffmpeg
        .overlay(
            main_parent_node=ffmpeg.input(background_filename).filter(filter_name="loop",loop=-1, size=bg_frames),
            overlay_parent_node=greenscreen_overlay,
            x="(W-w)/2",
            y="(H-h)/2")
        .trim(duration=duration)
        # .output(final_video_path)
        # .run(overwrite_output=True)
    )
    audio = (ffmpeg
             .filter(
        [ffmpeg.input(overlay_path).audio, ffmpeg.input(music_file).filter("volume", 0.25)],
        'amix')
             .filter("atrim", duration=duration)

             )

    input_video = video
    input_audio = audio

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path).run(overwrite_output=True)
