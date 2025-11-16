import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_string("""
<WaveProgressIndicator>:
    canvas:
        Color:
            rgba:root.handle_color 
        SmoothLine: 
            group:"line"
            cap:"round"
            joint:"round"
            width:dp(2)
        Color:
            rgba:root.handle_color
        RoundedRectangle:
            size:[dp(8), dp(20)]
            radius:[dp(2.5)] * 4
            group:"handle"
            pos:[0, self.height/2]
        Color:
            rgba:root.handle_color[:-1] + [0.5]
        SmoothLine: 
            group:"_line"
            cap:"round"
            joint:"round"
            width:dp(2)
""")


# maybe we add this widget in kivymd?
class WaveProgressIndicator(BoxLayout):
    progress = NumericProperty(0.5)
    amplitude = dp(3)
    _other_amplitude = NumericProperty(amplitude)
    wave_speed = -dp(30)
    wavelenght = dp(40)
    handle_color = ColorProperty([0, 0, 0, 0])
    playing = True
    on_seek = lambda *args : None

    _time = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # going all the way up to zero will inc cpu usage?
        Clock.schedule_interval(self._render_wave, 1 / 60.0)

    def on_size(self, *args):
        self.on_progress(self, self.progress)

    def on_pos(self, *args):
        self.on_progress(self, self.progress)

    @property
    def handle(self):
        return self.canvas.get_group("handle")[0]

    def on_progress(self, inst, value):
        self.handle.pos = [
            self.x + value * (self.width - self.handle.size[0]),
            self.y + (self.height - self.handle.size[1]) / 2,
        ]
        self.canvas.get_group("_line")[0].points = [
            [
                self.handle.pos[0] + self.handle.size[0] / 2,
                self.y + self.height / 2,
            ],
            [self.x + self.width - dp(1), self.y + self.height / 2],
        ]

    def _render_wave(self, dt):
        self._time += dt
        points = []
        sample_size = int(self.handle.pos[0] + self.handle.size[0] / 2)

        line = self.canvas.get_group("line")[0]

        _h = self.y + self.height / 2 - line.width / 2

        if not self.playing:
            self.canvas.get_group("line")[0].points = [
                [self.x + dp(1), _h],
                [sample_size, _h],
            ]
            return

        # using range(0, sample_size, 2)
        # will make it more efficient and easy on cpu?
        for pt in range(int(self.x + dp(1)), sample_size):
            y = (
                self.amplitude
                if self._other_amplitude == self.amplitude
                else self._other_amplitude
            ) * math.sin(
                (2 * math.pi / self.wavelenght) * (pt - self.wave_speed * self._time)
            )
            points.append([pt, _h + y])

        self.canvas.get_group("line")[0].points = points

    def set_progress(self, touch):
        w = self.width - self.handle.size[0]
        self.progress = (
            0 if w <= 0 else (min(max(touch.x, self.x), self.x + w) - self.x) / w
        )

    def collide_bar(self, touch_x, touch_y):
        bar_rx = self.x
        bar_rw = self.width
        bar_ry = self.handle.pos[1]
        bar_rh = self.handle.size[1]
        return (bar_rx <= touch_x <= bar_rx + bar_rw) and (
            bar_ry <= touch_y <= bar_ry + bar_rh
        )

    _touch_held = False
    def on_touch_down(self, touch):
        if self.collide_bar(*touch.pos):
            self._touch_held = True
            touch.ud["moving_handle"] = self
            Animation.cancel_all(self)
            Animation(_other_amplitude=0, t="easing_standard", d=0.3).start(self)
            self.set_progress(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.ud.get("moving_handle") == self:
            touch.ud.pop("moving_handle")
            Animation.cancel_all(self)
            Animation(
                _other_amplitude=self.amplitude, t="easing_standard", d=0.3
            ).start(self)
            Clock.schedule_once(lambda *arg: setattr(self, "_touch_held", False), 0.2)
            self.on_seek()
            return True
        return super().on_touch_up(touch)

    def on_touch_move(self, touch):
        if touch.ud.get("moving_handle") == self:
            self.set_progress(touch)
            return True
        return super().on_touch_move(touch)
