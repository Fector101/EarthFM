from earthfm.uidefs import next_frame
from jnius import autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from android import mActivity

MediaPlayer = autoclass('android.media.MediaPlayer')
Uri = autoclass('android.net.Uri')


class CompletionListener(PythonJavaClass):
    __javainterfaces__ = ['android/media/MediaPlayer$OnCompletionListener']

    def __init__(self, player):
        super().__init__()
        self._player_ref = player

    @java_method('(Landroid/media/MediaPlayer;)V')
    def onCompletion(self, mp):
        # Unload the player and call on_complete
        self._player_ref.unload()
        next_frame(self._player_ref.on_complete)


class PreparedListener(PythonJavaClass):
    __javainterfaces__ = ['android/media/MediaPlayer$OnPreparedListener']
    __javacontext__ = "app"

    def __init__(self, player):
        super().__init__()
        self._player_ref = player

    @java_method('(Landroid/media/MediaPlayer;)V')
    def onPrepared(self, mp):
        next_frame(self._player_ref.on_load)


class AndroidMediaPlayer:

    def __init__(self):
        self._player = MediaPlayer()
        self._completion_listener = CompletionListener(self)
        self._prepared_listener = PreparedListener(self)
        self._player.setOnCompletionListener(self._completion_listener)
        self._player.setOnPreparedListener(self._prepared_listener)
        self._state = None
        self._current_path = None
        self._looping = False

    @run_on_ui_thread
    def load(self, path):
        """Load a sound file asynchronously. on_load will be called when ready."""
        self.unload()
        self._player.reset()
        self._player.setDataSource(path)
        self._player.setLooping(self._looping)
        self._player.prepareAsync()
        self._current_path = path
        self._state = "stopped"

    @run_on_ui_thread
    def play(self):
        if self._player:
            self._player.start()
            self._state = "playing"

    @run_on_ui_thread
    def pause(self):
        if self._pla/yer and self._player.isPlaying():
            self._player.pause()
            self._state = "paused"
    
    @property
    def state(self):
        if not self._player:
            return None
        if self._player.isPlaying():
            return "playing"
        elif self._state == "paused":
            return "paused"
        else:
            return "stopped"

    @run_on_ui_thread
    def seek(self, s):
        if self._player:
            self._player.seekTo(s*1000)

    @run_on_ui_thread
    def unload(self):
        if self._player:
            self._player.reset()
            self._state = None
            self._current_path = None

    @run_on_ui_thread
    def loopon(self):
        self._looping = True
        if self._player:
            self._player.setLooping(True)

    @run_on_ui_thread
    def loopoff(self):
        self._looping = False
        if self._player:
            self._player.setLooping(False)

    @property
    def length(self):
        if self._player and self._current_path:
            return self._player.getDuration() / 1000 
        return 0

    def get_pos(self):
        if self._player and self._current_path:
            return self._player.getCurrentPosition() / 1000
        return 0

    def on_load(self, *args):
        """Called when the MediaPlayer finishes preparing the track."""
        pass

    def on_complete(self, *args):
        """Called when the MediaPlayer finishes playback."""
        pass
