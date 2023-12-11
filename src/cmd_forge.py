# this script can be run on a raw, a voc xml, or a .meme, and it will perform the next required step in the apollo pipeline
from pathlib import Path
import argparse
import os
import subprocess


import apollo_config as config
from apollo_log import init_log

from apollo_tts import tts
#from apollo_ocr import ocr
from apollo_timestamp import timestamp
from apollo_memeify import memeify
from forge import forge_meme


import dto_utils
import dto

def run_command( command):
    process = subprocess.run(command, shell=True, capture_output=True)

    try:
        return process.stdout.decode('utf-8', 'ignore')
    except Exception as x:
        print(f"Unable to decode output from command {command}: {x}")
def run_apollo_command(command_filename, target_file, *params):
    command = f"{config.APOLLO_PATH}\\{command_filename} \"{target_file}\" {' '.join(params)} 2>&1"
    return run_command( command )


parser = argparse.ArgumentParser(description="Repeatedly performs the next step of the Apollo production process on a raw, voc xml or meme, until a video is produced or a fatal error occurs.")
parser.add_argument("filename")
parser.add_argument("-preforge", action="store_true")
parser.add_argument("-production", "-p", action="store_true")
parser.add_argument("-use_cache", "-c", action="store_true")

args = parser.parse_args()

path = Path(args.filename)

init_log(path)
if args.production:
    config.initialize(["PRODUCTION"])

if args.use_cache:
    config.initialize(["REACTION_TUNING"])


stem = path.parent / path.stem

output = ""

while True:
    # stop on error
    if "exception" in output.lower() or "error" in output.lower():
        break

    if os.path.exists( stem.with_suffix(".meme")):
        meme_dto : dto.Meme
        meme_dto = dto.Meme.read(stem.with_suffix(".meme") )
        match meme_dto.header.state:
            case dto.StateType.CREATED:
                #ocr( str(stem.with_suffix(".meme")))

                if args.preforge:
                    break


            case dto.StateType.OCR:
                run_command(f'devenv.exe /edit "{str(stem.with_suffix(".meme"))}"')
                meme : dto.Meme
                meme = dto.Meme.read(str(stem.with_suffix(".meme")))
                meme.header.state = dto.StateType.OCR_QC
                meme.write(str(stem.with_suffix(".meme")), force=True)

                if args.preforge:
                    break

            case dto.StateType.OCR_QC:
                if args.preforge:
                    break

                tts(str(stem.with_suffix(".meme")), args.production)

            case dto.StateType.TTS:
                timestamp(str(stem.with_suffix(".meme")))


            case dto.StateType.TIMESTAMP:
                forge_meme(str(stem.with_suffix(".meme")))
                # all done!
                break

            case dto.StateType.TIMESTAMP_QC:
                # prompt to perform timestamp
                pass

            # draft was production
            case dto.StateType.PRODUCED:

                if args.production:
                    # revert to OCR_QC so narration will be regenerated
                    # with production voices
                    meme_dto.header.state = dto.StateType.OCR_QC
                    meme_dto.write(str(stem.with_suffix(".meme")),True)
                else:
 #                   if not os.path.exists(str(stem.with_suffix(".mp4"))):

                    # it's ok to overwrite a draft
                    forge_meme(str(stem.with_suffix(".meme")))
                    break

            # production video was produced
            case dto.StateType.PRODUCED_QC:
                if os.path.exists(str(stem.with_suffix(".mp4"))):
                    # user needs to delete the last video
                    break

                if args.production:
                    forge_meme(str(stem.with_suffix(".meme")))

                break

    elif os.path.exists( stem.with_suffix(".xml")):
        memeify(str(stem.with_suffix(".xml")))

    elif os.path.exists( stem.with_suffix(".png")):
        output += run_apollo_command("tools\labelimg\labelimg.exe", str(stem.with_suffix(".png")))

    else:
        raise ValueError(f"{args.filename} cannot be processed by Apollo")




print( output )