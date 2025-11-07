import os
from concurrent.futures import ThreadPoolExecutor

from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp

from earthfm.api import EarthFMBackend
from earthfm.uidefs import *
from earthfm.util import next_frame


class EarthFMApp(MDApp):
    # fonts
    bold_font = ""

    thread = ThreadPoolExecutor(max_workers=4)
    backend = EarthFMBackend()

    # root ui
    rootui = None
    screen_manager = None

    # screens
    RecordingsUI = None

    def build(self):

        # theme

        self.theme_cls.primary_palette = "#025A4D"

        # font def
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        self.bold_font = os.path.join(font_dir, "bold.ttf")

        screen_dir = os.path.join(os.path.dirname(__file__), "screens")

        self.rootui = Builder.load_file(os.path.join(screen_dir, "rootui.kv"))
        self.screen_manager = self.rootui.ids.screen_manager

        self.RecordingsUI = Builder.load_file(os.path.join(screen_dir, "recordings.kv"))
        self.screen_manager.add_widget(self.RecordingsUI)

        return self.rootui

    def fetch_recordings(self):
        data = self.backend.recordings
        next_frame(self.on_fetch_recordings, data)

    def on_fetch_recordings(self, data):
        mood_names, mood_recordings, all_recordings = data
        print("recordingg fetcche!")

    def on_start(self):
        self.thread.submit(self.fetch_recordings)


EarthFMApp().run()
