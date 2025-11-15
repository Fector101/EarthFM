import math

from kivy.animation import Animation
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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import CoreLabel
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex

from kivymd.uix.behaviors import ScaleBehavior, StencilBehavior
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.transition.transition import MDTransitionBase

from earthfm.goverlay import GradientOverlay
from earthfm.util import next_frame
from earthfm.wi import WaveProgressIndicator


class MarqueeLabel(FloatLayout):
    overlay_color = ColorProperty()
    font_name = StringProperty()
    font_size = NumericProperty()

    spl = NumericProperty(0.2)
    text = StringProperty(" ")

    _text = ""
    _main_label = None
    empty_str = "\u2003•\u2003"
    empty_str_width = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        next_frame(self._compute_separator_width)

    def _compute_separator_width(self, *args):
        temp = CoreLabel(
            text=self.empty_str,
            font_size=self.ids.label.font_size,
            font_name=self.ids.label.font_name,
        )
        temp.refresh()
        self.empty_str_width = temp.texture.size[0]

    def on_overlay_color(self, instance, color):
        if self._text != self.ids.label.text:
            self.ids.overlay.color = color

    # a very simple label scroll using 2 labels
    # from x = 0 x -> label.width then shift x to label.width/2
    # then label.width/2 - > label.width
    # then shfit label.width/2 then continue the loop
    def on_text(self, instance, data, fail=False):
        if not fail:
            self.ids.label.text = data
            self._text = data
        else:
            self.ids.label.text = data + self.empty_str + data

    def on_label_width(self):
        if self.ids.label.text == self._text:
            if self.ids.label.width > self.width:
                self.ids.overlay.color = self.overlay_color
                self.on_text(self, self._text, fail=True)
            else:
                Animation.cancel_all(self.ids.label)
                self.ids.label.x = self.x
                self.ids.overlay.color = [0, 0, 0, 0]

        elif self._text.strip() != "":
            self.loop_start()

    def loop_start(self):
        Animation.cancel_all(self.ids.label)
        self.ids.label.x = self.x
        anim = Animation(
            x=self.x - self.ids.label.width + self.width, d=len(self._text) * 2 * self.spl
        )
        anim.bind(on_complete=self.loop_continue)
        anim.start(self.ids.label)

    # offset is to fix that jerk
    def loop_continue(self, *args):
        self.ids.label.x = (
            self.x - (self.ids.label.width - self.empty_str_width) / 2 + self.width
        )
        anim = Animation(
            x=self.x - self.ids.label.width + self.width, d=len(self._text) * self.spl
        )
        anim.bind(on_complete=self.loop_continue)
        anim.start(self.ids.label)


class BottomPlayer(ButtonBehavior, BoxLayout):
    radius = ListProperty([dp(20), dp(20), 0, 0])
    is_open = False

    def open(self):
        self.is_open = True
        Animation.cancel_all(self)
        Animation(y=0, t="easing_standard", d=0.3).start(self)

    def close(self):
        self.is_open = False
        Animation.cancel_all(self)
        Animation(y=-self.height - dp(10), t="easing_standard", d=0.3).start(self)

    def expand(self, on_complete=None):
        op_duration = 0.2
        anim = Animation(opacity=0, d=op_duration)
        for child in self.children:
            anim.start(child)

        next_frame(
            Animation(
                height=self.parent.height,
                y=0,
                d=0.3,
                radius=[0] * 4,
                t="easing_standard",
            ).start,
            self,
            time=op_duration,
        )

        if on_complete is not None:
            next_frame(on_complete, time=op_duration + 0.4)

    def contract(self):
        Animation(
            height=dp(80),
            y=0,
            d=0.3,
            radius=[dp(20), dp(20), 0, 0] * 4,
            t="easing_standard",
        ).start(self)

        op_duration = 0.2
        anim = Animation(opacity=1, d=op_duration)

        for child in self.children:
            next_frame(anim.start, child, time=0.2 + op_duration)

        next_frame(
            self.parent.ids.t_text.on_text,
            self.parent.ids.t_text,
            self.parent.ids.t_text.text,
            time=0.2 + op_duration,
        )


class MDFadeTransition(MDTransitionBase):
    pass


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
