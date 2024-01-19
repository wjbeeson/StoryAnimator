import json
import shutil
from pathlib import Path

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import urllib.request
import random
import os
from tkinter import filedialog

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ffmpeg

import apollo_utils


def concatenate_audio(meme_filename):
    input_filenames = {}
    for file in os.listdir(str(Path(meme_filename).parent)):
        if file.endswith(".wav") and not file.__contains__("raw") and file.__contains__("_"):
            filename = str(Path(meme_filename).parent) + "\\" + file
            input_filenames[int(file.split("_")[len(file.split("_")) - 1].replace(".wav",""))] = filename
    sorted_values = sorted(input_filenames.keys())
    base_filename = list(input_filenames.values())[0].replace("_0.wav", ".wav")
    audio_inputs = []
    for i in sorted_values:
        audio_inputs.append(ffmpeg.input(input_filenames[i]))
    (
        ffmpeg
        .concat(*audio_inputs, v=0, a=1)
        .output(base_filename, loglevel="quiet")
        .run(overwrite_output=True, quiet=True)
    )
class SpeechAPIManager:

    def __init__(self, url):

        self.driver = webdriver.Chrome(options=Options())
        self.driver.get(url)

    def perform_login(self):
        input("Please complete the captcha and press enter to continue.")
        self.driver.find_elements(By.CSS_SELECTOR, "button[class='flex items-center  btn btn-secondary btn-lg btn-normal w-full']")[0].click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[autocomplete='email']")))
        self.driver.find_elements(By.CSS_SELECTOR, "[autocomplete='email']")[0].send_keys("redditlifestyle@gmail.com")
        self.driver.find_elements(By.CSS_SELECTOR, "[autocomplete='current-password']")[0].send_keys("55SharedPass6^")
        self.driver.find_elements(By.CSS_SELECTOR, "[type='submit']")[0].click()
    def generate_speech(self, voice, raw_filename):
        print("Selecting speech-to-speech option")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class='border-gray-300 hover:border-gray-900 relative flex cursor-pointer rounded-lg border bg-white py-2 px-3 gap-1.5 shadow-sm focus:outline-none max-w-xs']")))
        self.driver.find_elements(By.CSS_SELECTOR, "[class='border-gray-300 hover:border-gray-900 relative flex cursor-pointer rounded-lg border bg-white py-2 px-3 gap-1.5 shadow-sm focus:outline-none max-w-xs']")[0].click()

        print("Sending voice to voice selection box")
        actions = ActionChains(self.driver)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[autocomplete='off']")))
        time.sleep(1)
        self.driver.find_elements(By.CSS_SELECTOR, "[autocomplete='off']")[0].clear()
        time.sleep(1)
        self.driver.find_elements(By.CSS_SELECTOR, "[autocomplete='off']")[0].send_keys(voice)
        time.sleep(1)

        print("Clicking appropriate voice")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[role='option']")))
        voice_option = self.driver.find_elements(By.CSS_SELECTOR, "li[role='option']")[0]
        actions.move_to_element(voice_option).perform()
        time.sleep(1)
        voice_option.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[class='sr-only']")))
        self.driver.find_elements(By.CSS_SELECTOR, "input[class='sr-only']")[0].send_keys(raw_filename)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='flex items-center  btn btn-primary btn-lg btn-normal w-full mt-4 mb-4']")))
        generate_button = self.driver.find_elements(By.CSS_SELECTOR, "button[class='flex items-center  btn btn-primary btn-lg btn-normal w-full mt-4 mb-4']")[0]
        actions.move_to_element(generate_button).perform()
        time.sleep(1)
        generate_button.click()

        WebDriverWait(self.driver, 999999999).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Download Audio']")))
        download_button = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Download Audio']")[0]
        actions.move_to_element(download_button).perform()
        time.sleep(1)
        download_button.click()

        download_dir = r"C:\Users\wjbee\Downloads"
        searching_for_file = True
        filename = f"{Path(raw_filename).parent}\\{str(Path(raw_filename).stem).replace('_raw','')}.wav"
        while searching_for_file:
            for file in os.listdir(download_dir):
                if file.endswith(".mp3") and file.__contains__("ElevenLabs"):
                    shutil.copyfile(download_dir + "\\" + file, filename)
                    os.remove(download_dir + "\\" + file)
                    searching_for_file = False
            if searching_for_file:
                print("Waiting for file to download")
                time.sleep(5)
        self.driver.refresh()
        pass

def generate_speech_to_speech(meme_filename):
    url = r"https://elevenlabs.io/sign-up"
    d = SpeechAPIManager(url)
    d.perform_login()
    meme = json.load(open(str(meme_filename)))
    for i in range(len(meme["dialogue"])):
        dialogue = meme["dialogue"][str(i)]
        final_filename = apollo_utils.get_narration_filename(meme_filename, i)
        if os.path.exists(final_filename):
            print(f"Skipping existing narration file {str(Path(final_filename).name)}")
            continue
        raw_filename = final_filename.replace(".wav", "_raw.wav")
        d.generate_speech(dialogue["speakerID"], raw_filename)
    concatenate_audio(meme_filename)
    meme["state"] = "TTS"
    meme["narrationFilename"] = str(Path(meme_filename).with_suffix(".wav").name)
    meme["duration"] = apollo_utils.probe_audio(str(Path(meme_filename).with_suffix(".wav"))) + 2
    with open(str(meme_filename), "w") as f:
        f.write(json.dumps(meme))


generate_speech_to_speech(r"C:\Users\wjbee\Desktop\wife_thief\wife_thief.json")
