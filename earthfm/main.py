import os

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.loader import Loader
from kivymd.app import MDApp

from earthfm.api import EarthFMBackend
from earthfm.thread import EarthFMThreadExecutor
from earthfm.uidefs import *
from earthfm.util import next_frame


class EarthFMApp(MDApp):
    white_color = get_color_from_hex("#E9EFEC")
    get_file = lambda self, file_name: os.path.join(
        os.path.dirname(__file__),
        file_name,
    )

    # transparent image
    transparent_image = get_file(None, "assets/transparent.png")

    # fonts
    main_font = "main.ttf"
    bold_font = "PlusJakartaSans-Bold.ttf"
    medium_font = "PlusJakartaSans-Medium.ttf"
    regular_font = "PlusJakartaSans-Regular.ttf"

    thread = EarthFMThreadExecutor()
    backend = EarthFMBackend()

    # root ui
    rootui = None
    screen_manager = None

    # screens
    RecordingsUI = None

    def build(self):
        # theme

        self.theme_cls.primary_palette = [0, 0, 1, 1]  # "#025A4D"
        # original color
        # "#025A4D"
        self.theme_cls.theme_style = "Dark"

        # loading image transparent
        Loader.loading_image = self.transparent_image
        # font def
        font_dir = self.get_file("fonts")

        for font in {"main", "regular", "medium", "bold"}:
            setattr(
                self,
                f"{font}_font",
                os.path.join(font_dir, getattr(self, f"{font}_font")),
            )

        screen_dir = self.get_file("screens")

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

        box = self.RecordingsUI.ids.container
        widgets = []

        for mood_name in mood_names.keys():
            widget = MoodSection()
            widget.mood = mood_names[mood_name]
            widget.opacity = 0

            data = []

            for recording in mood_recordings[mood_name][:10]:
                data.append({"viewclass": "Recording", "data": recording})

            widget.data = data

            widgets.append(widget)
            box.add_widget(widget)

        next_frame(self.show_widgets, widgets, time=0.5)

    def show_widgets(self, widgets):
        self.RecordingsUI.ids.indicator.stop()
        next_frame(
            Animation(opacity=0, d=0.3).start, self.RecordingsUI.ids.indicator, time=0.7
        )
        anim = Animation(opacity=1, d=0.3)
        for widget in widgets:
            next_frame(anim.start, widget, time=1)

    def on_start(self):
        self.RecordingsUI.ids.pg_bar.progress = 0.5
        next_frame(self.open_mini_player, time=2)
        return
        self.RecordingsUI.ids.indicator.start()
        self.thread.submit(self.fetch_recordings)

    def open_mini_player(self):
        box = self.RecordingsUI.ids.small_player
        Animation(y=dp(10), t="easing_standard", d=0.3).start(box)


EarthFMApp().run()
