import shutil
from pathlib import Path
import ffmpeg
from calculate_metadata import add_description
import os
import random
import json
import apollo_utils


def forge_meme(meme_filename, remotion_output_dirname=r"C:\Users\wjbee\JSProjects\Remotion\out"):
    file_choice = random.choice(os.listdir(r"C:\Users\wjbee\Desktop\Raptor\backgrounds\Looping"))

    # Step 0: Get all the necessary files to render
    background_filename = f"C:\\Users\\wjbee\\Desktop\\Raptor\\backgrounds\\looping\\{file_choice}"

    # Step 1: Copy all required files over to remotion directory
    meme_filepath = Path(meme_filename)
    remotion_output_dirpath = Path(remotion_output_dirname)
    remotion_public_dirname = str(remotion_output_dirpath.parent) + "\\public\\"

    narration = str(meme_filepath.with_suffix(".wav"))
    remotion_narration_filename = (remotion_public_dirname + str(Path(narration).name)).replace("\\", "/")
    shutil.copy(narration, remotion_narration_filename)

    remotion_props_filename = (remotion_public_dirname + str(Path(meme_filename).name)).replace("\\", "/")
    shutil.copy(meme_filename, remotion_props_filename)

    # Step 2: Compile parameters for calling remotion render
    narration_local_path = str(Path(remotion_narration_filename).name)
    props_local_path = str(Path(remotion_props_filename).name)
    json_obj = {}
    json_obj["propsFilename"] = props_local_path
    json_txt = json.dumps(json_obj)
    json_filename = str(meme_filepath.parent) + "\\" + (meme_filepath.stem + "_props.json")
    with open(json_filename, "w") as outfile:
        outfile.write(json_txt)
    command = f"npx remotion render VideoComp out/{meme_filepath.stem}.mp4 --props={json_filename}"

    # Step 3: Call the remotion render function and pass the parameters
    os.chdir(str(remotion_output_dirpath.parent))
    os.system(command)

    # Step 4: After done, use ffmpeg to greenscreen the background file on
    add_background(overlay_path=f"{remotion_output_dirname}\\{meme_filepath.stem}.mp4",
                   background_filename=background_filename,
                   output_path=str(meme_filepath.with_suffix(".mp4")))


def add_background(overlay_path, background_filename, output_path, chroma_key_hex="#0000FF"):
    music_file = r"C:\Users\wjbee\Desktop\Raptor\backgrounds\deep_sleep.mp3"
    duration = apollo_utils.probe_video(overlay_path)[0]
    (bg_duration, bg_fps) = apollo_utils.probe_video(background_filename)[0:2]
    bg_frames = int(bg_duration * bg_fps)
    greenscreen_overlay = (
        ffmpeg.input(overlay_path)
        .filter(filter_name="chromakey", color=chroma_key_hex, similarity=0.2, blend=0.3)
        .filter(filter_name="despill", type="blue")
    )
    video = (
        ffmpeg
        .overlay(
            main_parent_node=ffmpeg.input(background_filename).filter(filter_name="loop", loop=-1, size=bg_frames),
            overlay_parent_node=greenscreen_overlay,
            x="(W-w)/2",
            y="(H-h)/2")
        .trim(duration=duration)
        # .output(final_video_path)
        # .run(overwrite_output=True)
    )
    audio = (ffmpeg
             .filter(
        [ffmpeg.input(overlay_path).audio, ffmpeg.input(music_file).filter("volume", 0.18)],
        'amix')
             .filter("atrim", duration=duration)

             )

    input_video = video
    input_audio = audio

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path).run(overwrite_output=True)

# forge_meme(r"C:\Users\wjbee\Desktop\Raptor\scripts\test\test.json")
