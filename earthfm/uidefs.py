import math

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    ColorProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.behaviors import ScaleBehavior, StencilBehavior
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem

from earthfm.util import next_frame
from earthfm.wi import WaveProgressIndicator


class RoundedImage(AsyncImage, StencilBehavior):
    pass


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class MoodSection(BoxLayout):
    data = ListProperty()


class Recording(ButtonBehavior, ScaleBehavior, BoxLayout):
    radius = ListProperty([dp(20)] * 4)
    data = DictProperty()

    def on_kv_post(self, base_widget):
        if self.data != {}:
            self.on_data(self, self.data)

    def on_data(self, instance, data):
        app = App.get_running_app()

        # bg color of widget
        self.canvas.get_group("color")[0].rgba = get_color_from_hex(
            data["featuredImage"]["node"]["localFile"]["childImageSharp"][
                "gatsbyImageData"
            ]["backgroundColor"]
        )

        # set image to transparent_image until loaded
        self.canvas.get_group("img")[0].source = app.transparent_image

        # load image in bg thread
        app.thread.submit(app.backend.get_image, data, self.set_img, 1)

        # duration in seconds
        s = data["recordingSettings"]["audio"]["mediaDetails"]["length"]
        # convert to suitable format
        # 03:47 also remove hour if less than 60 mins
        duration = (
            f"{s // 3600}:" * (s >= 3600) + f"{(s % 3600) // 60:02d}:{s % 60:02d}"
        )

        # construct main string
        title = data["title"]
        mw = 27
        ellipsis = "…" if len(title) > mw else ""

        self.ids.rtext.text = (
            f"[font={app.bold_font}]"
            f"{title[:mw]}{ellipsis}"
            "[/font]"
            f"[size=14sp][font={app.regular_font}]\n"
            f"{data['recordingSettings']['recordist']['title'][:16]}"
            f"\n{duration}"
            "[/font][/size]"
        )

    def set_img(self, data, image):
        if data is self.data and not image.endswith(".webp"):
            # webp not supported by kivy
            self.canvas.get_group("img")[0].source = image
