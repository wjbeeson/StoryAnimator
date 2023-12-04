import sys
import argparse
from pathlib import Path
from apollo_memeify import memeify

parser = argparse.ArgumentParser(description="Create .meme from a Visual Object Challenge (VOC) XML file containing bounding boxes for a raw PNG")
parser.add_argument("text_filename")
parser.add_argument("-overwrite", "-f", action="store_true")
args = parser.parse_args()

print(f"Memeifying {args.text_filename}")
memeify(args.text_filename, args.overwrite)


