from pathlib import Path

from apollo_tts import tts
from apollo_log import init_log
import logging as log

#
# process command line args
#
import argparse

# C:\Users\fjbee\Desktop\Apollo\meme\doordash.meme -p

parser = argparse.ArgumentParser(description="Reads the specified .meme file and performs text to speech on each line.")
parser.add_argument("meme_filename")
parser.add_argument("-production", "-p", action="store_true")

args = parser.parse_args()

# collect sequential blocks of dialog by speaker

init_log(Path(args.meme_filename))
tts(args.meme_filename, args.production)