from kivy.app import App
from kivy.properties import ColorProperty, DictProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import AsyncImage
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.uix.behaviors import StencilBehavior
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from earthfm.util import next_frame

class RoundedImage(AsyncImage, StencilBehavior):
    pass


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class MoodSection(BoxLayout):
    data = ListProperty()


class Recording(BoxLayout):

    radius = ListProperty([dp(20)]*4)
    data = DictProperty()

    def on_kv_post(self, base_widget):
        if self.data != {}: self.on_data(self, self.data)

    def on_data(self, instance, data):
        app = App.get_running_app()
        self.canvas.get_group("color")[0].rgba = get_color_from_hex(
            data["featuredImage"]["node"]["localFile"]["childImageSharp"][
                "gatsbyImageData"
            ]["backgroundColor"]
        )
        self.canvas.get_group("img")[0].source = app.transparent_image
        app.thread.submit(app.backend.get_image, data, self.set_img, 1)
        s = data["recordingSettings"]["audio"]["mediaDetails"]["length"]

        self.ids.artist.text = data["recordingSettings"]["recordist"]["title"]
        self.ids.title.text = data["title"]
        self.ids.duration.text = f"{s // 3600}:" * (s >= 3600) + f"{(s % 3600) // 60:02d}:{s % 60:02d}"
    
    def set_img(self, data, image):
        if data is self.data and not image.endswith(".webp"):
            # webp not supported by kivy
            self.canvas.get_group("img")[0].source = image
