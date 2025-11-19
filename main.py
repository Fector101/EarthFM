from os.path import dirname, join
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import earthfm.main

exit()

import time

from earthfm.asound import AndroidMediaPlayer
player = AndroidMediaPlayer()


# from earthfm.sound import DesktopMediaPlayer
# player = DesktopMediaPlayer()

path = dirname(__file__)


loaded = False

def set_load(*args):
    print(args)
    global loaded
    loaded = True

player.on_load = set_load


_s = time.time()
player.load("/data/data/org.tdynamos.earthfm/files/app/earthfm/../sounds/a-morning-at-sweetwater-lagoon.mp3")

while not loaded:
    time.sleep(0.1)

print(f"{time.time()-_s:.2f}s")

player.play()
player.loopon()
time.sleep(5)


player.pause()
print(player.state())

print("skeek")
player.seek(10)      # jump to 5 seconds
player.play()

print(player.state())

time.sleep(5)


player.unload()


time.sleep(10)

