from earthfm.uidefs import next_frame
from kivy.core.audio_output import SoundLoader
import threading

class DesktopMediaPlayer:
    def __init__(self):
        self._sound = None
        self._looping = False
        self._state = None

    def load(self, path):
        """Load sound asynchronously in a background thread."""
        thread = threading.Thread(target=self._load, args=(path,), daemon=True)
        thread.start()

    def _load(self, path):
        """Blocking load in background thread; calls on_load on main thread."""
        self.unload()
        sound = SoundLoader.load(path)
        if sound:
            sound.loop = self._looping

            # TDOD; implemetn on on_complete
            # sound.bind(on_stop=lambda *args: self._on_complete())
            
            self._sound = sound
            self._state = 'stopped'
            # Call on_load on next UI frame
            self.on_load()
            # next_frame(self.on_load)
        else:
            raise FileNotFoundError(f"Cannot load audio file: {path}")

    def play(self):
        if self._sound:
            self._sound.play()
            self._state = 'playing'

    def pause(self):
        if self._sound and self._sound.state == 'play':
            self._sound.stop()  # Kivy backends may not support pause
            self._state = 'paused'

    def seek(self, s):
        if self._sound:
            self._sound.seek(s)

    def unload(self):
        if self._sound:
            self._sound.stop()
            self._sound.unload()
            self._sound = None
            self._state = None

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
        if self._sound and hasattr(self._sound, 'length'):
            return self._sound.length or 0
        return 0

    def get_pos(self):
        if self._sound and hasattr(self._sound, 'get_pos'):
            return self._sound.get_pos() or 0
        return 0
    
    @property
    def state(self):
        if not self._sound:
            return None
        if self._sound.state == 'play':
            return 'playing'
        elif self._state == 'paused':
            return 'paused'
        else:
            return 'stopped'

    def on_load(self):
        pass
    
    def _on_complete(self):
        self.unload()
        next_frame(self.on_complete)

    def on_complete(self):
        pass
