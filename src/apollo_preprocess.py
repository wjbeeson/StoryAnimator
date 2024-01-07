import logging as log
import shutil
from pathlib import Path

from dominate import document
from dominate.tags import *

import apollo_config as config
from apollo_utils import get_paragraph_list

common_abbreviations = {
    "MIL": "Mother in law",
    "FIL": "Father in law",
    "BIL": "Brother in law",
    "SIL": "Sister in law",
    "tl;dr": "Too long; didn't read",
    "Tl;dr": "Too long; didn't read",
    "TL;DR": "Too long; didn't read",
    "AP ": "Affair Partner ",
    "SO ": "Significant Other ",
}


def preprocess(raw_filename):
    log.info(f"Preprocessing {raw_filename}")
    css_filename = str(Path(raw_filename).with_suffix(".css"))
    shutil.copyfile(f"{config.APOLLO_PATH}/config/editing_style.css", css_filename)
    with open(raw_filename, "r", encoding="utf-8") as f:
        text = get_paragraph_list(f.read())
    with document(title=f'Preprocess {str(Path(raw_filename).name)}') as doc:
        with doc.head:
            link(rel='stylesheet', href=Path(css_filename).name)
        for para in text:
            p(para, _class='UNDEFINED')
    with open(str(Path(raw_filename).with_suffix(".html")), 'w') as f:
        f.write(doc.render())
