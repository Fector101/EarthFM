import json
import os
from os.path import dirname, exists, join

import requests


class EarthFMBackend:
    base_url = "https://earth.fm/"
    cache_dir = ".cache"
    session = None

    def __init__(self):
        self.session = requests.session()

    def burl(self, url):
        return self.base_url + url

    def get_json(self, url):
        file = join(self.cache_dir, url)
        data = None

        if exists(file):
            with open(file, "r") as file_ctx:
                data = json.load(file_ctx)
            return data

        if not exists(dirname(file)):
            os.makedirs(dirname(file))

        data = self.session.get(self.burl(url)).json()

        with open(file, "w") as file_ctx:
            json.dump(data, file_ctx, indent=4)

        return data

    @property
    def home_page(self):
        page_data = self.get_json("page-data/index/page-data.json")
        static_hashes = page_data["staticQueryHashes"]

        for hash in static_hashes:
            self.get_json(f"page-data/sq/d/{hash}.json")

    @property
    def recordings(self):
        data = self.get_json("page-data/recordings/page-data.json")["result"]["data"]

        # all raw recordings
        all_recordings = data["allWpRecording"]["nodes"]

        # classify all recordings into moods:
        # Featured, Calm, Dreamy, Eerie, Intense, Joyful, Moody
        # Mysterious, Rural, Uplifting and Other

        moods = data["allWpMood"]["nodes"]

        # mood id -> mood name
        mood_names = {}

        for mood in moods:
            mood_names[mood["id"]] = mood["name"]

        mood_names["other"] = "Other"
        mood_names["featured"] = "Featured"

        # empty dict -> {moodid: [recordings...] }
        mood_recordings = dict.fromkeys(
            ["featured"] + [mood["id"] for mood in moods] + ["other"]
        )

        # new list for each recording
        for __ in mood_recordings:
            mood_recordings[__] = list()

        # map each recording to mood
        for recording in all_recordings:
            r_mood = recording["recordingSettings"]["mood"]
            if r_mood is not None:
                mood_recordings[r_mood["id"]].append(recording)
            else:
                mood_recordings["other"].append(recording)

        # featured
        mood_recordings["featured"] = data["wp"]["themeGeneralSettings"][
            "themeOptions"
        ]["featuredItems"]["featuredRecordings"]

        # for mood in mood_recordings.keys(): print(mood_names[mood], len(mood_recordings[mood]))

        return (
            mood_names,
            mood_recordings,
            all_recordings,
        )
