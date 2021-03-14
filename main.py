
import sys
import time
import keyboard
import clipboard
import subprocess
import threading
from enum import Enum


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


# Determine whether capslock is on (code taken from: https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status)

def capslock():
    output = subprocess.check_output('xset q | grep LED', shell=True)[65]

    if output == 48:
        return False
    if output == 49:
        return True

    raise Exception("JPN input: capslock() has gone off the rails (" + str(output) + ")")


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
    global states, state, items

    print("Handling command: " + cmd)
    sys.stdout.flush()

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

        if state == states.inactive:
            return

    # Insert the output.

    print("Result: " + output)
    sys.stdout.flush()

    write_text(output)
    state = states.inactive


# Handle a single key.

def accum_key(key):
    global accum

    if len(key) == 1:
        accum += key
    elif key == "space":
        accum += " "
    elif key == "backspace":
        accum = accum[:-1]


# Turn the trayicon indicator on.

def indicator_on():
    print("activate")
    sys.stdout.flush()


# Turn the trayicon indicator off.

def indicator_off():
    print("deactivate")
    sys.stdout.flush()


# Key event listener.

def key_event(event):
    global states, state, accum

    key = event.name
    mods = event.modifiers

    if capslock() and len(key) == 1:
        key = key.swapcase()

    # Print report of what just happened.

    log = "[" + state.name
    
    if state == states.listening:
        log += ", "
        log += accum

    log += "] " + key + " " + str(mods)
    print(log)
    sys.stdout.flush()

    # Handle key depending on states.

    if state == states.inactive:
        if key == ";" and mods == ("alt",):
            accum = ""
            state = states.listening
            indicator_on()

    elif state == states.listening:
        if key == ";" and mods == ():
            state = states.working
            indicator_off()

            work_thread = threading.Thread( target=handle_command, args=(accum,) )
            work_thread.start()

        if key == ";" and mods == ("alt",):
            state = states.inactive
            indicator_off()

        elif mods == () or mods == ("shift",):
            accum_key( key )

    elif state == states.working:
        if key == "esc":
            state = states.inactive


# Load translation items.

items       = read_translation_file("items/hirigana.txt")
items.update( read_translation_file("items/katakana.txt") )
items.update( read_translation_file("items/special.txt") )

# Set up global state.

states = Enum( "states", "inactive listening working" )
state = states.inactive
accum = ""

# Register keyboard hook and wait indefinitely.

keyboard.on_press( key_event )
keyboard.wait()

