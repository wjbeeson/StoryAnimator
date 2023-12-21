import logging as log
import apollo_config as config
import sys
from pathlib import Path

class FfmpegFilter(log.Filter):
    def filter(self, record):
        # Return False if the record's name starts with 'requests'
        return "ffmpeg" not in record.msg

def init_log (meme_path):

    handler =  log.FileHandler(str(meme_path.with_suffix(".log")))
    handler.addFilter(FfmpegFilter())

    log.basicConfig(
        level=config.FORGE_LOG_LEVEL,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            handler,
            log.StreamHandler(sys.stdout)
        ]
    )
init_log(Path(r"C:\Users\wjbee\Desktop\Raptor\scripts\test\test.txt"))