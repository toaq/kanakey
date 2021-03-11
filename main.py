
import sys
import time
import keyboard
import clipboard


# Get a dictionary of the strings and results from a file.

def read_translation_file( name ):
    ret = {}
    with open(name) as fh:
        for line in fh:
            line = line.strip()
            if line != "":
                string = line.split(" ")[0]
                result = line.split(" ")[1]
                ret[string] = result

    return ret


# Paste a value using the clipboard. Restore original clipboard contents
# afterwards.

def write_text(text):
    value = clipboard.paste()
    clipboard.copy(text)
    time.sleep(.1)
    keyboard.send("shift+insert")
    time.sleep(.1)
    clipboard.copy(value)


# Grab the next token off the front of the command. Return its output
# and the tail (unusued portion) of the command.

def next_token(cmd, table):
    for i in [3, 2, 1]:
        candidate = cmd[:i]
        if candidate in table:
            return (table[candidate], cmd[i:])

    return (cmd[0], cmd[1:])


# Handle a full command.

def handle_command(cmd):
    global items

    cmdlen = len(cmd)
    output = ""

    while cmd != "":

        # \ marks a literal character.

        if cmd[0] == "\\":
            token, cmd = cmd[1], cmd[2:]
            output += token

        # Anything else is parsed as kana (for now).

        else:
            token, cmd = next_token( cmd, items )
            output += token

    # Backspace over the whole command string.

    for i in range(cmdlen + 1):
        keyboard.send("backspace")
        time.sleep(.02)

    # Insert the output.

    write_text(output)


# Handle a single key.

def handle_key(key):
    global accum

    if key == ";":
        deactivate()
        handle_command(accum)
    elif len(key) == 1:
        accum += key
    elif key == "space":
        accum += " "
    elif key == "backspace":
        accum = accum[:-1]


# Become active.

def activate():
    global active, accum

    active = True
    accum = ""
    print("activate")
    sys.stdout.flush()


# Become inactive.

def deactivate():
    global active

    active = False
    print("deactivate")
    sys.stdout.flush()


# Key event listener (passes important keys on to handle_key()).

def key_event(event):
    global active, accum

    key = event.name
    mods = event.modifiers

    if key == ";" and mods == ("alt",):
        if active:
            deactivate()
        else:
            activate()
        return

    if active and mods in [(), ("shift",)]:
        handle_key(key)


# Set up keyboard stuff.

items       = read_translation_file("items/hirigana.txt")
items.update( read_translation_file("items/katakana.txt") )
items.update( read_translation_file("items/special.txt") )

active = False
accum = ""

keyboard.on_press( key_event )
keyboard.wait()

