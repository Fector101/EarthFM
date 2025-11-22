import atexit
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import weakref

from earthfm.uidefs import next_frame


class DesktopMediaPlayer:
    _instances = weakref.WeakSet()

    def __init__(self):
        self._proc = None
        self._sock = None
        self._sock_path = None
        self._state = None
        self._looping = False
        self._loaded_path = None
        self._lock = threading.Lock()
        self._manual_unload = False
        self._loaded_event = threading.Event()
        self.__class__._instances.add(self)

    def _terminate_process(self):
        with self._lock:
            proc = self._proc
            self._proc = None
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self._safe_close_socket()
        self._remove_socket_file()
        self._state = None
        self._loaded_path = None
        self._loaded_event.clear()

    @classmethod
    def _terminate_all(cls):
        for inst in tuple(cls._instances):
            inst._terminate_process()
            cls._instances.discard(inst)

    def load(self, path):
        thread = threading.Thread(target=self._load, args=(path,), daemon=True)
        thread.start()

    def _load(self, path):
        self.unload()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Cannot load audio file: {path}")
        if shutil.which("mpv") is None:
            raise RuntimeError("mpv was not found in PATH")

        self._sock_path = os.path.join(
            tempfile.gettempdir(),
            f"earthfm-mpv-{os.getpid()}-{int(time.time() * 1000)}.sock",
        )
        loop_flag = "inf" if self._looping else "no"
        cmd = [
            "mpv",
            "--no-terminal",
            "--force-window=no",
            "--audio-display=no",
            "--idle=no",
            f"--input-ipc-server={self._sock_path}",
            f"--loop-file={loop_flag}",
            "--pause",
            path,
        ]

        with self._lock:
            self._manual_unload = False
            self._loaded_event.clear()
            self._loaded_path = path
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if not self._connect_socket():
            self.unload()
            raise RuntimeError("Failed to initialize mpv IPC")

        self._state = "stopped"
        self._loaded_event.set()
        next_frame(self.on_load)

        watcher = threading.Thread(target=self._watch_process, daemon=True)
        watcher.start()

    def _connect_socket(self, timeout=4):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._proc is None or self._proc.poll() is not None:
                return False
            if os.path.exists(self._sock_path):
                try:
                    self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self._sock.connect(self._sock_path)
                    return True
                except OSError:
                    self._safe_close_socket()
            time.sleep(0.05)
        return False

    def _send_cmd(self, command):
        with self._lock:
            if self._proc is None or self._sock is None:
                return None
            try:
                self._sock.sendall((json.dumps({"command": command}) + "\n").encode())
                response = b""
                while not response.endswith(b"\n"):
                    chunk = self._sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                if not response:
                    return None
                line, _, _ = response.partition(b"\n")
                return json.loads(line.decode(errors="ignore"))
            except OSError:
                return None

    def _get_property(self, name):
        resp = self._send_cmd(["get_property", name])
        if not resp or resp.get("error") != "success":
            return None
        return resp.get("data")

    def play(self):
        if self._send_cmd(["set_property", "pause", False]) is not None:
            self._state = "playing"

    def pause(self):
        if self._send_cmd(["set_property", "pause", True]) is not None:
            self._state = "paused"

    def seek(self, s):
        self._send_cmd(["seek", float(s), "absolute"])

    def unload(self):
        with self._lock:
            self._manual_unload = True
            proc = self._proc
            self._proc = None

        try:
            self._send_cmd(["quit"])
        except Exception:
            pass

        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

        self._safe_close_socket()
        self._remove_socket_file()
        self._state = None
        self._loaded_path = None
        self._loaded_event.clear()

    def _safe_close_socket(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _remove_socket_file(self):
        if self._sock_path and os.path.exists(self._sock_path):
            try:
                os.remove(self._sock_path)
            except OSError:
                pass
        self._sock_path = None

    def loopon(self):
        self._looping = True
        self._send_cmd(["set_property", "loop-file", "inf"])

    def loopoff(self):
        self._looping = False
        self._send_cmd(["set_property", "loop-file", "no"])

    @property
    def length(self):
        length = self._get_property("duration")
        return float(length or 0)

    def get_pos(self):
        pos = self._get_property("time-pos")
        return float(pos or 0)

    @property
    def state(self):
        if self._proc is None:
            return None
        paused = self._get_property("pause")
        if paused is None:
            return self._state
        return "paused" if paused else "playing"

    def _watch_process(self):
        with self._lock:
            proc = self._proc
        if proc is None:
            return
        proc.wait()
        manual = self._manual_unload
        self._safe_close_socket()
        self._remove_socket_file()
        with self._lock:
            if self._proc is proc:
                self._proc = None
        self._state = None
        self._loaded_path = None
        self._loaded_event.clear()
        if not manual:
            next_frame(self.on_complete)

    def on_load(self):
        pass

    def on_complete(self):
        pass


atexit.register(DesktopMediaPlayer._terminate_all)
