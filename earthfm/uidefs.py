from kivy.properties import StringProperty
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
