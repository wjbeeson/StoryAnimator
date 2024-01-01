import os
import json
json_file = "timestamp_test\\timestamp_test.json"
meme = json.load(open(json_file))
assert len(meme["captions"]) == len(meme["timestamps"])
pass