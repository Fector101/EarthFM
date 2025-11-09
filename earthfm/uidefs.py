import math

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (ColorProperty, DictProperty, ListProperty,
                             NumericProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.behaviors import ScaleBehavior, StencilBehavior
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem

from earthfm.util import next_frame


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


# maybe we add this widget in kivymd?
class MusicProgress(BoxLayout):
    progress = NumericProperty(0.5)
    amplitude = dp(2.5)
    _other_amplitude = NumericProperty(amplitude)
    wave_speed = -dp(30)
    wavelenght = dp(27.5)

    _time = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # going all the way up to zero will inc cpu usage?
        Clock.schedule_interval(self._render_wave, 1/60)

    def on_size(self, *args):
        self.on_progress(self, self.progress)

    def on_pos(self, *args):
        self.on_progress(self, self.progress)

    def on_progress(self, inst, value):
        handle = self.canvas.get_group("handle")[0]
        handle.pos = [
            self.x + value * self.width - dp(5),
            self.y + (self.height - handle.size[1]) / 2,
        ]
        self.canvas.get_group("_line")[0].points = [
            [self.x + self.width * self.progress, self.y + self.height / 2],
            [self.x + self.width, self.y + self.height / 2],
        ]

    def _render_wave(self, dt):
        self._time += dt
        points = []
        sample_size = int((self.width * self.progress))

        # using range(0, sample_size, 2)
        # will make it more efficient and easy on cpu?
        for pt in range(0, sample_size):
            y = (
                self.amplitude
                if self._other_amplitude == self.amplitude
                else self._other_amplitude
            ) * math.sin(
                (2 * math.pi / self.wavelenght) * (pt - self.wave_speed * self._time)
            )
            points.append([self.x + pt, self.y + self.height / 2 + y])

        self.canvas.get_group("line")[0].points = points

    def collide_instr(self, instr, touch_x, touch_y):
        rx, ry = instr.pos
        rw, rh = instr.size
        padding = dp(5)
        rx -= padding
        ry -= padding
        rw += dp(10)
        rh += dp(10)
        return (rx <= touch_x <= rx + rw) and (ry <= touch_y <= ry + rh)

    def on_touch_down(self, touch):
        handle = self.canvas.get_group("handle")[0]
        if self.collide_instr(handle, touch.x, touch.y):
            touch.ud["moving_handle"] = handle
            Animation.cancel_all(self)
            Animation(_other_amplitude=0, t="easing_standard", d=0.3).start(self)
            return True
        padding = dp(5)
        bar_rx = self.x - padding
        bar_rw = self.width + dp(10)
        bar_ry = handle.pos[1] - padding
        bar_rh = handle.size[1] + dp(10)
        if (bar_rx <= touch.x <= bar_rx + bar_rw) and (bar_ry <= touch.y <= bar_ry + bar_rh):
            target_x = touch.x - handle.size[0] / 2
            max_x = (self.x + self.width) - handle.size[0]
            new_x = min(max_x, max(self.x, target_x))
            range_w = self.width - handle.size[0]
            self.progress = (new_x - self.x) / range_w if range_w > 0 else 0.0
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        handle = self.canvas.get_group("handle")[0]
        if touch.ud.get('moving_handle') == handle:
            touch.ud.pop("moving_handle")
            Animation.cancel_all(self)
            Animation(_other_amplitude=self.amplitude, t="easing_standard", d=0.3).start(self)
            return True
        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        handle = self.canvas.get_group("handle")[0]
        if touch.ud.get('moving_handle') == handle:
            max_x = (self.x + self.width) - handle.size[0]
            new_x = min(max_x, max(self.x, touch.x))
            range_w = self.width - handle.size[0]
            self.progress = (new_x - self.x) / range_w if range_w > 0 else 0.0
            return True
        return super().on_touch_move(touch)
