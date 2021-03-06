
import keyboard
import clipboard
import time


# Initialize accum. Read kana files.

def read_translation_file( name ):
    ret = {}
    with open(name) as fh:
        for line in fh:
            line = line.strip()
            if line != "":
                kana = line.split(" ")[1]
                string = line.split(" ")[0]
                ret[string] = kana
    return ret

accum = ""
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,\\"

hirigana = read_translation_file("hirigana.txt")
katakana = read_translation_file("katakana.txt")
special  = read_translation_file("special.txt")

modes = [hirigana, katakana]

modifiers_down = {}


# Grab the next token off the front of the command. Return its output
# and the tail of the command.

def next_token(cmd, table):
    for i in [3, 2, 1]:
        candidate = cmd[:i]
        if candidate in table:
            return (table[candidate], cmd[i:])

    return (cmd[0], cmd[1:])


# Handle a full command from the initial ; to the final ;.

def handle_command(cmd):
    global modes

    cmdlen = len(cmd)
    mode = 0
    output = ""

    while cmd != "":

        # \ marks the beginning of a special command (like $ for ￥)

        if cmd[0] == "\\":
            token, cmd = next_token( cmd[1:], special )
            output += token

        # , switches between hirigana mode and katakana mode.

        elif cmd[0] == ",":
            mode = (mode + 1) % len(modes)
            cmd = cmd[1:]

        # Anything else is parsed as kana:

        else:
            token, cmd = next_token( cmd, modes[mode] )
            output += token

    # Backspace over the whole command string (including both ;'s).

    for i in range(cmdlen + 2):
        keyboard.send("backspace")
        time.sleep(.02)

    # Insert the output via the clipboard.

    value = clipboard.paste()
    clipboard.copy(output)
    time.sleep(.1)
    keyboard.send("shift+insert")
    time.sleep(.1)
    clipboard.copy(value)


# Handle a single key.

def handle_key(key):
    global accum, chars 

    if accum == "":
        if key == ";":
            accum = ";"

    else:
        if accum == ";" and key not in chars:
            accum = ""
            return

        if key == ";":
            handle_command(accum[1:])
            accum = ""
        elif len(key) == 1:
            accum += key
        elif key == "space":
            accum += " "
        elif key == "backspace":
            accum = accum[:-1]


# Key event listener (passes important keys on to handle_key()).

def key_event(event):
    key = event.name

    if key not in keyboard.all_modifiers:
        if "ctrl" not in event.modifiers:
            handle_key(key)
            print(key, "(", accum, ")")


keyboard.on_press( key_event )
keyboard.wait()
