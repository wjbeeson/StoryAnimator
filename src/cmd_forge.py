# this script can be run on a raw, a voc xml, or a .meme, and it will perform the next required step in the apollo pipeline
import time
from pathlib import Path
import argparse
import os
import subprocess

import apollo_config as config
from apollo_log import init_log

from apollo_tts import tts
from apollo_timestamp import timestamp
from apollo_memeify import memeify
from apollo_preprocess import preprocess
from forge import forge_meme
import json


def run_command(command):
    process = subprocess.run(command, shell=True, capture_output=True)

    try:
        return process.stdout.decode('utf-8', 'ignore')
    except Exception as x:
        print(f"Unable to decode output from command {command}: {x}")


def run_apollo_command(command_filename, target_file, *params):
    command = f"{config.APOLLO_PATH}\\{command_filename} \"{target_file}\" {' '.join(params)} 2>&1"
    return run_command(command)


parser = argparse.ArgumentParser(
    description="Repeatedly performs the next step of the Apollo production process on a raw, voc xml or meme, "
                "until a video is produced or a fatal error occurs.")
parser.add_argument("filename")
args = parser.parse_args()
path = Path(args.filename)
#path = Path(r"C:\Users\wjbee\Desktop\Raptor\scripts\test\test.txt")

init_log(path)

config.initialize(["PRODUCTION"])
stem = path.parent / path.stem

output = ""
preprocessed = False
while True:
    # stop on error
    if "exception" in output.lower() or "error" in output.lower():
        break

    if os.path.exists(stem.with_suffix(".json")):
        meme = json.load(open(str(stem.with_suffix(".json"))))

        match meme["state"]:
            case "FORMATTED":
                tts(str(stem.with_suffix(".json")))

            case "TTS":
                timestamp(str(stem.with_suffix(".json")))

            case "TIMESTAMPED":
                forge_meme(str(stem.with_suffix(".json")))
                break
                # all done!
    elif os.path.exists(stem.with_suffix(".txt")) and preprocessed is True:
        memeify(str(path))

    elif os.path.exists(stem.with_suffix(".txt")):
        preprocess(str(path))
        preprocessed = True



    else:
        raise ValueError(f"{str(path)} cannot be processed by Apollo")

print(output)
