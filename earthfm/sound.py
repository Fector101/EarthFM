import os
import weakref

from kivy.clock import Clock
from kivy.core.audio import SoundLoader

from earthfm.uidefs import next_frame


class KivySoundPlayer:
    _instances = weakref.WeakSet()

    def __init__(self):
        self._sound = None
        self._state = None
        self._looping = False
        self._paused_pos = 0.0
        self._loaded_path = None
        self._load_checks = 0
        self._load_check_event = None
        self._complete_check_event = None
        self.__class__._instances.add(self)

    def load(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Cannot load audio file: {path}")
        self.unload()
        self._loaded_path = path
        self._state = "stopped"
        self._load_checks = 0

        sound = SoundLoader.load(path)
        if sound is None:
            raise RuntimeError(f"Failed to load audio file: {path}")

        self._sound = sound
        self._sound.loop = self._looping
        self._load_check_event = Clock.schedule_once(self._check_loaded, 0)

    def _check_loaded(self, dt):
        if self._sound is None:
            return
        self._load_checks += 1
        if self._sound.length > 0 or self._load_checks > 50:
            self._load_check_event = None
            self._state = "stopped"
            next_frame(self.on_load)
            self._complete_check_event = Clock.schedule_interval(self._check_complete, 0.2)
        else:
            self._load_check_event = Clock.schedule_once(self._check_loaded, 0.1)

    def _check_complete(self, dt):
        if self._sound is None:
            return
        if self._state == "playing" and self._sound.state == "stop":
            self._state = "stopped"
            self._loaded_path = None
            if self._complete_check_event:
                self._complete_check_event.cancel()
                self._complete_check_event = None
            next_frame(self.on_complete)

    def play(self):
        if self._sound is None:
            return
        if self._state == "paused":
            self._sound.seek(self._paused_pos)
        self._sound.play()
        self._state = "playing"

    def pause(self):
        if self._sound is None:
            return
        if self._sound.state == "play":
            self._paused_pos = self._sound.get_pos() or 0
            self._sound.stop()
        self._state = "paused"

    def seek(self, s):
        if self._sound:
            self._sound.seek(float(s))

    def unload(self):
        if self._load_check_event:
            self._load_check_event.cancel()
            self._load_check_event = None
        if self._complete_check_event:
            self._complete_check_event.cancel()
            self._complete_check_event = None
        if self._sound:
            self._sound.stop()
            self._sound.unload()
            self._sound = None
        self._state = None
        self._loaded_path = None
        self._paused_pos = 0.0

    def loopon(self):
        self._looping = True
        if self._sound:
            self._sound.loop = True

    def loopoff(self):
        self._looping = False
        if self._sound:
            self._sound.loop = False

    @property
    def length(self):
        if self._sound:
            return self._sound.length or 0
        return 0

    def get_pos(self):
        if self._sound and self._sound.state == "play":
            return self._sound.get_pos() or 0
        if self._state == "paused":
            return self._paused_pos
        return 0

    @property
    def state(self):
        if self._sound is None:
            return None
        if self._sound.state == "play":
            return "playing"
        if self._state == "paused":
            return "paused"
        return "stopped"

    def on_load(self):
        pass

    def on_complete(self):
        pass
