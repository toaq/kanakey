
import sys
import threading
import pystray
from PIL import Image, ImageDraw, ImageFont


def loop():
    global icon, active_png, inactive_png

    while True:
        line = sys.stdin.readline().strip()

        if line == "activate":
            icon.icon = active_png
        elif line == "deactivate":
            icon.icon = inactive_png
        else:
            print( line )

    print("tray icon daemon: stdin was closed (??)")
    sys.exit(0)


# Set up trayicon.

active_png   = Image.open("icon/active.png")
inactive_png = Image.open("icon/inactive.png")

active = False
accum = ""
icon = pystray.Icon("JPN input", inactive_png)


# Set up looping thread.

loop_thread = threading.Thread( target=loop )
loop_thread.start()


# Run icon.

icon.run()

