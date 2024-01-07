import shutil
import time
import os
from pathlib import Path
from apollo_utils import get_paragraph_list
import argparse


class OBSManager:
    def __init__(self, obs_out_directory, raw_filename):
        self.obs_out_directory = obs_out_directory
        self.raw_filename = raw_filename

        self.paragraphs = get_paragraph_list(open(raw_filename).read())
        self.current_paragraph = 0

    def get_narration_filename(self):
        return str(Path(self.raw_filename).parent) + "\\" + str(Path(self.raw_filename).stem) + "_" + str(
            self.current_paragraph) + "_raw.wav"

    def transfer_file(self):
        # get list of files in directory reverse sorted by date
        files = [self.obs_out_directory + "\\" + x for x in os.listdir(self.obs_out_directory)]
        sorted_files = sorted(files, key=os.path.getctime, reverse=True)
        final_narration = sorted_files[0]
        narration_filename = self.get_narration_filename()
        shutil.copyfile(final_narration, narration_filename)
        for file in sorted_files:
            os.remove(file)

    def check_if_recorded(self):
        narration_filename = self.get_narration_filename()
        files = [str(Path(self.raw_filename).parent) + "\\" + x for x in
                 os.listdir(str(Path(self.raw_filename).parent))]
        if narration_filename in files:
            return "[WARNING: ALREADY RECORDED] "
        else:
            return ""

    def wait_for_files(self):
        while True:
            print(
                f"{self.check_if_recorded()}Paragraph {self.current_paragraph}: {self.paragraphs[self.current_paragraph]}")
            pressed_key = \
                input("Press [T] to transfer file, [S] to skip to paragraph, or [Q] to quit: ").lower().strip()[0]
            match pressed_key:
                case "t":
                    files = os.listdir(self.obs_out_directory)
                    if files is None or len(files) == 0:
                        print("No files found.")
                    else:
                        self.transfer_file()
                        self.current_paragraph += 1
                        if self.current_paragraph > len(self.paragraphs) - 1:
                            print("Reached end of script.")
                            self.current_paragraph = self.current_paragraph - 1
                case "s":
                    while True:
                        for i, para in enumerate(self.paragraphs):
                            print(f"{i}: {para}")
                        self.current_paragraph = input("Enter paragraph number to skip to: ")
                        try:
                            self.current_paragraph = int(self.current_paragraph)
                            if self.current_paragraph > len(self.paragraphs) - 1 or self.current_paragraph < 0:
                                print("Invalid paragraph number.")
                                continue
                        except Exception:
                            print("Invalid paragraph number.")
                            continue
                        break
                case "q":
                    exit()
                case _:
                    print("Invalid input.")
            print()


parser = argparse.ArgumentParser(description="Creates a video from a .meme file")
parser.add_argument("raw_filename")
parser.add_argument("obs_out_directory", default=r"C:\Users\wjbee\Desktop\Raptor\obs_temp", nargs="?")
# parser.add_argument("-production", "-p", action="store_true")
# parser.add_argument("-use_cache", "-c", action="store_true")

args = parser.parse_args()


manager = OBSManager(obs_out_directory=args.obs_out_directory, raw_filename=args.raw_filename)
manager.wait_for_files()
