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

from materialyoucolor.utils.theme_utils import custom_color
from materialyoucolor.utils.color_utils import argb_from_rgba_01
from materialyoucolor.hct import Hct


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

        self.theme_cls.primary_palette = "#025A4D"
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
        self.RecordingsUI.ids.indicator.start()
        self.thread.submit(self.fetch_recordings)

    def play(self, data):
        Animation(opacity=0, d=0.3).start(self.RecordingsUI.ids.p_img)
        f = lambda : self.thread.submit(self.backend.get_image, data, self.set_player_image, 1)

        color = custom_color(argb_from_rgba_01(get_color_from_hex(
            data["featuredImage"]["node"]["localFile"]["childImageSharp"][
                "gatsbyImageData"
            ]["backgroundColor"]
        )), source_color=argb_from_rgba_01(get_color_from_hex(self.theme_cls.primary_palette)), blend=False)
        bg = color[self.theme_cls.theme_style.lower()]["color"]
        # self.RecordingsUI.ids.pg_bar.handle_color = [_/255 for _ in bg]

        # construct main string
        title = data["title"]
        
        self.RecordingsUI.ids.a_text.text = data['recordingSettings']['recordist']['title']
        self.RecordingsUI.ids.t_text.text =  data["title"]

        next_frame(f, time=0.3)
        next_frame(self.open_mini_player, time=0.6)

    def set_player_image(self, data, image):
        if not image.endswith(".webp"):
            # webp not supported by kivy
            self.RecordingsUI.ids.p_img.source = image
            Animation(opacity=1,d=0.3).start(self.RecordingsUI.ids.p_img)

    def close_mini_player(self):
        box = self.RecordingsUI.ids.small_player
        Animation(y=-box.height - dp(10), t="easing_standard", d=0.3).start(box)

    def open_mini_player(self):
        box = self.RecordingsUI.ids.small_player
        Animation(y=0, t="easing_standard", d=0.3).start(box)


EarthFMApp().run()
