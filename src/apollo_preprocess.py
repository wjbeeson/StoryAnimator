import string

from cssutils import CSSParser

from apollo_utils import split_keep_spaces
import apollo_config as config
import logging as log
from pathlib import Path
import json
import re
import cssutils
from pprint import pprint
from calculate_metadata import characters_per_line


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
def remove_tags(text):
    loop = True
    while loop:
        if text.find("<") != -1 and text.find(">") != -1:
            start = text.find("<")
            end = text.find(">")
            text = text[:start] + text[end + 1:]
        elif text.find("<") != -1 or text.find(">") != -1:
            raise Exception(f"Invalid tag: {text}")
        else:
            loop = False
    return text

def log_abbreviations(text):
    error = False
    for abbreviation in common_abbreviations:
        if text.find(abbreviation) != -1:
            log.warning(f"Found abbreviation {abbreviation} in {text}")
            error = True
    return error

def preprocess(raw_filename):
    log.info(f"Preprocessing {raw_filename}")
    with open(raw_filename, "r", encoding="utf-8") as f:
        # split into paragraphs, dropping repeated linefeeds e.g. \n\n \n\n\n etc
        text = [para.replace('\n', ' ') for para in f.read().split('\n\n') if para != '']
    error = False
    for para in text:
        para = remove_tags(para)
        error = log_abbreviations(para)
        tokens = split_keep_spaces(para)
        if len(tokens) > 5000:
            log.error(f"Paragraph exceeds 5000 tokens: {para}")
            error = True
        for token in tokens:
            if len(token) > characters_per_line:
                log.error(f"Token exceeds {characters_per_line} characters: {token}")
                error = True
    if error:
        raise Exception("Found errors in raw text")
