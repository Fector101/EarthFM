import os

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.loader import Loader

from kivy.core.window import Window

from kivymd.app import MDApp

from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import argb_from_rgba_01, rgba_from_argb
from materialyoucolor.utils.platform_utils import open_wallpaper_file
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score

from earthfm.api import EarthFMBackend
from earthfm.thread import EarthFMThreadExecutor
from earthfm.uidefs import *
from earthfm.util import next_frame


is_android = "ANDROID_ENTRYPOINT" in os.environ.keys()

if is_android:
    from earthfm.asound import AndroidMediaPlayer
    Player = AndroidMediaPlayer
else:
    from earthfm.sound import DesktopMediaPlayer
    Player = DesktopMediaPlayer

class EarthFMApp(MDApp):
    
    # for kv files
    next_frame = lambda self, *arg, **kwargs: next_frame(*arg, **kwargs)
    

    currently_playing = DictProperty({})

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
    backend.cache_dir = get_file(None, backend.cache_dir)
    backend.sound_dir = get_file(None, backend.sound_dir)

    if not is_android:
        player : DesktopMediaPlayer = None
    

    # root ui
    rootui = None
    screen_manager = None

    # screens
    RecordingsUI = None

    def build(self):

        # load player
        self.player = Player()

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
        self.screen_manager.transition = MDFadeTransition()

        self.RecordingsUI = Builder.load_file(os.path.join(screen_dir, "recordings.kv"))
        self.screen_manager.add_widget(self.RecordingsUI)

        self.PlayerUI = Builder.load_file(os.path.join(screen_dir, "player.kv"))
        self.screen_manager.add_widget(self.PlayerUI)

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

    def set_window_color(self, color):
        Window.clearcolor = color
    
    def on_start(self):
        self.RecordingsUI.ids.indicator.start()
        self.PlayerUI.ids.windicator.on_seek = self.seek_music
        self.thread.submit(self.fetch_recordings)
        Clock.schedule_interval(self.update_sound, 0.1)
        # Clock.schedule_interval(self._print_fps, 0.5)

    def _print_fps(self, *largs):
        print("FPS: %2.4f (real draw: %d)" % (Clock.get_fps(), Clock.get_rfps()))

    def get_dominant_color(self, image):
        image = open_wallpaper_file(image)
        pixel_len = image.width * image.height
        image_data = image.getdata()
        pixel_array = [
            image_data[_]
            for _ in range(
                0, pixel_len, 5
            )
        ]
        colors = QuantizeCelebi(pixel_array, 128)
        selected_color = Score.score(colors)[0]
        return selected_color    

    def seek_music(self):
        if self.player.state in ["playing" or "paused"]:
            self.player.seek(self.PlayerUI.ids.windicator.progress * self.player.length)

    def set_player_image(self, data, image):
        if not image.endswith(".webp"):
            # webp not supported by kivy
            self.RecordingsUI.ids.p_img.source = image
            Animation(opacity=1, d=0.3).start(self.RecordingsUI.ids.p_img)
            self.set_theme_from_image(image)

    def set_theme_from_image(self, image):
        color = [_/255 for _ in rgba_from_argb(self.get_dominant_color(image))]
        next_frame(setattr, self.theme_cls, "primary_palette", color)

    def on_currently_playing(self, instance, data):
        
        # stop if already playing
        self.stop_sound()

        # update player image with animation
        Animation(opacity=0, d=0.3).start(self.RecordingsUI.ids.p_img)
        f = lambda: self.thread.submit(
            self.backend.get_image, data, self.set_player_image, 1
        )
        next_frame(f, time=0.3)
        
        # set title and artist
        self.RecordingsUI.ids.a_text.text = data["recordingSettings"]["recordist"][
            "title"
        ]
        self.RecordingsUI.ids.t_text.text = data["title"]

        # open player
        if not self.RecordingsUI.ids.btm_player.is_open:
            next_frame(self.RecordingsUI.ids.btm_player.open, time=0.6)

        
        # set music for loading
        
        self.RecordingsUI.ids.pg_indicator.type = "indeterminate"
        self.RecordingsUI.ids.pg_indicator.value = 100
        self.RecordingsUI.ids.pg_indicator.start()
        
        # get music and load into soundloader object
        self.thread.submit(self.backend.get_sound, data, self.play_sound)

    def update_sound(self, *args):
        if not self.player.state in ["playing" or "paused"]:
            return
        
        self.RecordingsUI.ids.play_btn.icon = "play" if self.player.state == 'paused' else "pause" 
        self.RecordingsUI.ids.pg_indicator.value = (self.player.get_pos() / self.player.length) * 100
        self.PlayerUI.ids.lenght.lenght = int(self.player.length)

        if not self.PlayerUI.ids.windicator._touch_held:
            self.PlayerUI.ids.windicator.progress = self.RecordingsUI.ids.pg_indicator.value/100

    def pause_play_icon(self, widget):
        if self.player.state in ["playing" or "paused"]:
            if widget.icon == "play":
                seek_value = (self.RecordingsUI.ids.pg_indicator.value/100) * self.player.length
                self.player.play()
                next_frame(self.player.seek, seek_value)
            else:
                self.player.stop()

    def stop_sound(self):
        self.player.unload()

    def play_sound(self, file, data):
        if data is self.currently_playing:
            self.player.load(self.get_file(file))
            self.player.on_load = self.on_load
            
    def on_load(self):
        self.player.play()
        self.RecordingsUI.ids.pg_indicator.stop()
        self.RecordingsUI.ids.pg_indicator.value = 0

    # color = custom_color(
    #     argb_from_rgba_01(
    #         get_color_from_hex(
    #             data["featuredImage"]["node"]["localFile"]["childImageSharp"][
    #                 "gatsbyImageData"
    #             ]["backgroundColor"]
    #         )
    #     ),
    #     source_color=argb_from_rgba_01(
    #         get_color_from_hex(self.theme_cls.primary_palette)
    #     ),
    #     blend=False,
    # )
    # bg = color[self.theme_cls.theme_style.lower()]["color"]


EarthFMApp().run()
