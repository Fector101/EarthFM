import json
import os
import time
from os.path import dirname, exists, getsize, join

import requests

from earthfm.util import next_frame


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

    def parse_images(self, data):
        img_data = data["featuredImage"]["node"]["localFile"]["childImageSharp"][
            "gatsbyImageData"
        ]["images"]

        def parse_srcset(srcset_string):
            sources = []
            for item in srcset_string.split(","):
                parts = item.strip().split()
                if len(parts) == 2:
                    url, width_str = parts
                    sources.append(
                        {"url": url.strip(), "width": int(width_str.replace("w", ""))}
                    )
            return sources

        fallback_images = parse_srcset(img_data["fallback"]["srcSet"])

        webp_images = []
        if len(img_data["sources"]) > 0:
            webp_images = parse_srcset(img_data["sources"][0]["srcSet"])

        return fallback_images, webp_images

    # download only 4 images at a time
    downloaders = 0

    def get_image(self, recording_data, on_complete, quality=0):
        # quality can be 0,1,2,3

        # 0 -> 128px
        # 1 -> 256px
        # 2 -> 512px
        # 3 -> 1024px

        while self.downloaders > 3:
            time.sleep(0.3)

        jpg, webp = self.parse_images(recording_data)
        selected_image = jpg[quality]["url"]

        file = join(self.cache_dir, selected_image[1:])
        if not exists(dirname(file)):
            os.makedirs(dirname(file))
        if exists(file) and getsize(file) <= 10:
            os.remove(file)

        if not exists(file):
            # download it
            self.downloaders += 1
            with open(file, "wb") as file_ctx:
                try:
                    file_ctx.write(
                        self.session.get(self.base_url + selected_image).content
                    )
                except Exception as e:
                    os.remove(file)
                    self.downloaders -= 1
                    raise e
            self.downloaders -= 1

        next_frame(on_complete, recording_data, file)

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
        mood_names["featured"] = "Featured"

        for mood in moods:
            mood_names[mood["id"]] = mood["name"]

        mood_names["other"] = "Other"

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

        # for mood in mood_recordings.keys():
        #    print(mood_names[mood], len(mood_recordings[mood]))

        return (
            mood_names,
            mood_recordings,
            all_recordings,
        )
