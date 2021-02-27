
import keyboard
import clipboard
import time


# Initialize accum. Read kana files.

def read_kana_file( name ):
    ret = {}
    with open(name) as fh:
        for line in fh:
            line = line.strip()
            if line != "":
                kana = line.split(" ")[0]
                string = line.split(" ")[1]
                ret[string] = kana
    return ret

accum = ""
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,"

hirigana = read_kana_file("hirigana.txt")
katakana = read_kana_file("katakana.txt")


# Parse a single word.

def parse_word(word):
    table = hirigana
    ret = ""

    if word[0] == ",":
        table = katakana
        word = word[1:]

    while word != "":
        changed = False

        for i in [3, 2, 1]:
            if word[:i] in table:
                ret += table[word[:i]]
                word = word[i:]
                changed = True
                break

        if not changed:
            word = word[1:]
            ret += "?"

    return ret


def handle_command(cmd):
    for i in range(len(cmd)+2):
        keyboard.send("backspace")
        time.sleep(.01)

    output = ""

    for word in cmd.split(" "):
        output += parse_word(word)

    value = clipboard.paste()
    clipboard.copy(output)
    time.sleep(.1)
    keyboard.send("ctrl+v")
    time.sleep(.1)
    clipboard.copy(value)


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

def key_event(event):
    key = event.name

    if key not in keyboard.all_modifiers:
        handle_key(key)
        print(key, "(", accum, ")")


keyboard.on_press( key_event )
keyboard.wait()
