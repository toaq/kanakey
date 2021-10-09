
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
    time.sleep(.3)
    keyboard.send("shift+insert")
    time.sleep(.3)
    clipboard.copy(value)


# Grab the next token off the front of the command. Return its output
# and the tail (unusued portion) of the command.

def next_token(cmd, table):
    for i in [3, 2, 1]:
        candidate = cmd[:i]
        if candidate in table:
            return (table[candidate], cmd[i:])

    return (cmd[0], cmd[1:])


# Convert a kana command into kana.

def interpret_kana_command(cmd):
    ret = ""

    while cmd != "":

        # \ marks a literal character.

        if cmd[0] == "\\":
            token, cmd = cmd[1], cmd[2:]
            ret += token

        # Anything else is parsed as kana (for now).

        else:
            token, cmd = next_token( cmd, items )
            ret += token

    return ret


# Add a tone to a single Toaq word.

def tonify_word(word, tone):
    marks = {
        "a": "aaáäaâàãaǎ",
        "e": "eeéëeêèẽeě",
        "i": "iıíïıîìĩıǐ",
        "o": "ooóöoôòõoǒ",
        "u": "uuúüuûùũuǔ",
        "y": "yyýÿyŷỳỹyy̌",
        "m": "mm̄ḿm̈m̉m̂m̀m̃mm̌",
        "M": "MM̄ḾM̈M̉M̂M̀M̃MM̌",

        #"a": "aāáäảâàãaǎ",
        #"e": "eēéëẻêèẽeě",
        #"i": "iīíïỉîìĩıǐ",
        #"o": "oōóöỏôòõoǒ",
        #"u": "uūúüủûùũuǔ",
        #"y": "yȳýÿỷŷỳỹyy̌",
        #"m": "mm̄ḿm̈m̉m̂m̀m̃mm̌",
        #"M": "MM̄ḾM̈M̉M̂M̀M̃MM̌",
    }

    next_vowel_tone = tone
    ret = ""

    for letter in word:
        if letter in "aeiouy":
            ret += marks[letter][next_vowel_tone]
            next_vowel_tone = 0

        else:
            ret += letter
            if next_vowel_tone == 0:
                next_vowel_tone = 1

    return ret.replace("i", "ı")


# Interpret a Toaq command.

def interpret_toaq_command(cmd):
    ret = ""
    word = ""

    for c in cmd + ".":
        if c in "abcdefghijklmnopqrstuyz123456789":
            word += c
        else:
            if word != "":
                if word[-1] in "123456789":
                    tone = int(word[-1])
                    word = word[:-1]
                else:
                    tone = 8

                ret += tonify_word(word, tone)
                word = ""

            ret += c

    ret = ret.replace("<<", "«")
    ret = ret.replace(">>", "»")
    return ret[:-1]


# Handle a full command.

def handle_command(cmd):
    global states, state, items

    print("Handling command: " + cmd)
    sys.stdout.flush()

    # Determine which command is being run and get the ouput of it.

    #if cmd[0] == "j":
        #output = interpret_kana_command(cmd[1:])
    #elif cmd[0] == "t":
        #output = interpret_toaq_command(cmd[1:])
    #else:
        #output = "[kanakey: unknown command type]"

    output = interpret_toaq_command(cmd)

    # Backspace over the whole command string.

    time.sleep(.1)

    for i in range(len(cmd) + 1):
        keyboard.send("backspace")
        time.sleep(.02)

        if state == states.inactive:
            return

    # Insert the output.

    print("Result: " + output)
    sys.stdout.flush()

    write_text(output)
    state = states.inactive


# Turn the trayicon indicator on.

def indicator_on():
    print("activate")
    sys.stdout.flush()


# Turn the trayicon indicator off.

def indicator_off():
    print("deactivate")
    sys.stdout.flush()


# Key event listener.

shifter = {"1": "!",
           "2": "@",
           "3": "#",
           "4": "$",
           "5": "%",
           "6": "^",
           "7": "&",
           "8": "*",
           "9": "(",
           "0": ")",
           "-": "_",
           "−": "_",
           "=": "+",
           "[": "{",
           "]": "}",
           "\\": "|",
           ";": ":",
           "'": "\"",
           ",": "<",
           ".": ">",
           "/": "?"}

def key_event(event):
    global states, state, accum

    key = event.name
    mods = event.modifiers

    if capslock() and len(key) == 1:
        key = key.swapcase()

    if "shift" in mods:
        if len(key) == 1:
            if key.isalpha():
                key = key.swapcase()
            else:
                key = shifter[key]

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
            if len(key) == 1:
                accum += key
            elif key == "space":
                accum += " "
            elif key == "backspace":
                accum = accum[:-1]

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

