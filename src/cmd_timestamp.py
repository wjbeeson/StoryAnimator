from pathlib import Path
import logging as log

from apollo_timestamp import timestamp
import dto
from apollo_log import init_log
#
# process command line args
#
import argparse

#-a C:\Users\fjbee\Desktop\Apollo\meme -m C:\Users\fjbee\Desktop\Apollo\meme\doordash.meme

parser = argparse.ArgumentParser(description="Performs voice recognition on narration files associated with specified .meme, records word timestamps.")
parser.add_argument("meme_filename")
args = parser.parse_args()

init_log(Path(args.meme_filename))
log.info(f"Performing word timestamp detection on {args.meme_filename}")

timestamp(args.meme_filename)

