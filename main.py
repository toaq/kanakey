
import keyboard
import time

accum = ""
alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
         "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
         "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
         "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

hiri = {}
hiri["a"] = "あ";  hiri["i"] = "い";   hiri["u"] = "う";   hiri["e"] = "え";  hiri["o"] = "お"
hiri["ka"] = "か"; hiri["ki"] = "き";  hiri["ku"] = "く";  hiri["ke"] = "け"; hiri["ko"] = "こ"
hiri["sa"] = "さ"; hiri["shi"] = "し"; hiri["su"] = "す";  hiri["se"] = "せ"; hiri["so"] = "そ"
hiri["ta"] = "た"; hiri["chi"] = "ち"; hiri["tsu"] = "つ"; hiri["te"] = "て"; hiri["to"] = "と"
hiri["na"] = "な"; hiri["ni"] = "に";  hiri["nu"] = "ぬ";  hiri["ne"] = "ね"; hiri["no"] = "の"
hiri["ha"] = "は"; hiri["hi"] = "ひ";  hiri["fu"] = "ふ";  hiri["he"] = "へ"; hiri["ho"] = "ほ"
hiri["ma"] = "ま"; hiri["mi"] = "み";  hiri["mu"] = "む";  hiri["me"] = "め"; hiri["mo"] = "も"
hiri["ya"] = "や";                     hiri["yu"] = "ゆ";                     hiri["yo"] = "よ"
hiri["ra"] = "ら"; hiri["ri"] = "り";  hiri["ru"] = "る";  hiri["re"] = "れ"; hiri["ro"] = "ろ"
hiri["ya"] = "わ";                                                            hiri["yo"] = "を"
hiri["n."] = "ん"

def handle_command(cmd):
    for i in range(len(cmd)+2):
        keyboard.send("backspace")

    while cmd != "":
        for i in [3, 2, 1]:
            if cmd[:i] in hiri:
                print(hiri[cmd[:i]], end="")
                cmd = cmd[i:]
                break

    print()

def handle_key(key):
    global accum, alpha 

    if accum == "":
        if key == ";":
            accum = ";"

    else:
        if accum == ";" and key not in alpha:
            accum = ""
            return

        if key in alpha:
            accum += key
        elif key == "backspace":
            accum = accum[:-1]
        elif key == ";":
            handle_command(accum[1:])
            accum = ""

def key_event(event):
    key = event.name

    if key not in keyboard.all_modifiers:
        handle_key(key)
        print(key, "(", accum, ")")


keyboard.on_press( key_event )
keyboard.wait()
