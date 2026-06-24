import turtle
import math
import random
import time
import os
import threading
import pyttsx3

tts = pyttsx3.init()
tts.setProperty('rate', 150)
tts.setProperty('volume', 0.8)

def say(text):
    def _say():
        tts.say(text)
        tts.runAndWait()
    t = threading.Thread(target=_say, daemon=True)
    t.start()

ASSETS = "/home/pi/JARVIS4"

screen = turtle.Screen()
screen.setup(1000, 750)
screen.bgcolor("#000000")
screen.title("THE ECHO FREQUENCIES")
screen.tracer(0, 0)
screen.listen()
screen.colormode(255)

t = turtle.Turtle()
t.speed(0)
t.hideturtle()

def cls():
    t.clear()

def draw_stars(count=100):
    for _ in range(count):
        x = random.randint(-490, 490)
        y = random.randint(-370, 370)
        s = random.uniform(0.5, 2)
        c = random.choice(["#ffffff", "#aaddff", "#ffddaa"])
        t.penup()
        t.goto(x, y)
        t.dot(s, c)

def code_rain(frames=30):
    chars = "01[]{}()*&^%$#@!+=/\\|;:'\",.<>~`"
    for _ in range(frames):
        cls()
        for _ in range(60):
            x = random.randint(-480, 480)
            y = random.randint(-360, 360)
            c = random.choice(chars)
            t.penup()
            t.goto(x, y)
            t.color("#00ff41")
            t.write(c, align="center", font=("Courier", int(random.uniform(6, 10)), "normal"))
        screen.update()

def glitch(frames=15):
    for _ in range(frames):
        cls()
        if random.random() > 0.5:
            t.penup()
            t.goto(0, 0)
            t.color("#ff0000")
            t.dot(2000, "#ff0000")
        for _ in range(30):
            x = random.randint(-480, 480)
            y = random.randint(-360, 360)
            c = random.choice("ERROR: SYSTEM FAILURE PORTAL DETECTED")
            t.penup()
            t.goto(x, y)
            t.color(random.choice(["#ff0000", "#00ff00", "#ffffff"]))
            t.write(c, align="center", font=("Courier", int(random.uniform(8, 14)), "bold"))
        screen.update()

def portal_pulse(frames=60):
    for frame in range(frames):
        cls()
        p = frame / frames
        r = 50 + p * 200
        for i in range(10):
            shade = max(0, 100 - i * 10)
            t.penup()
            t.goto(0, 0)
            t.dot(r + i * 15, f"#{0:02x}{212//(i+1):02x}{255//(i+1):02x}")
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(r * 0.3, r * 1.2)
            x = dist * math.cos(angle)
            y = dist * math.sin(angle)
            t.penup()
            t.goto(x, y)
            t.dot(random.uniform(1, 3), "#00d4ff")
        screen.update()

def draw_laptop():
    t.penup()
    t.goto(-80, -100)
    t.pendown()
    t.color("#444444")
    t.begin_fill()
    for _ in range(2):
        t.forward(160)
        t.right(90)
        t.forward(100)
        t.right(90)
    t.end_fill()
    t.penup()
    t.goto(-60, -80)
    t.pendown()
    t.color("#00ff41")
    for i in range(5):
        t.write(random.choice("01"), font=("Courier", 6, "normal"))
        t.penup()
        t.goto(-60 + i * 25, -80)
    t.penup()
    t.goto(-70, 20)
    t.pendown()
    t.color("#666666")
    t.begin_fill()
    t.goto(70, 20)
    t.goto(50, 0)
    t.goto(-50, 0)
    t.goto(-70, 20)
    t.end_fill()

def fade_to_black(frames=20):
    for i in range(frames):
        cls()
        t.penup()
        t.goto(0, 0)
        a = int((i / frames) * 255)
        t.dot(2000, f"#{a:02x}{a:02x}{a:02x}")
        screen.update()

# === TITLE SEQUENCE ===
draw_stars(150)
screen.update()
time.sleep(1.5)

cls()
t.penup()
t.goto(0, -50)
t.color("#00d4ff")
t.write("THE ECHO FREQUENCIES", align="center", font=("Courier", 36, "bold"))
t.penup()
t.goto(0, -90)
t.color("#ff2a6d")
t.write("A KARTHIKEYA PRODUCTION", align="center", font=("Courier", 14, "bold"))
t.penup()
t.goto(0, -130)
t.color("#aaaaaa")
t.write("Starring Mr. Python & Ms. Matplotlib", align="center", font=("Courier", 10, "normal"))
screen.update()
time.sleep(3)

fade_to_black()

cls()
for i in range(30):
    cls()
    draw_stars(60)
    a = i / 30
    t.penup()
    t.goto(0, -20)
    t.color("#ff2a6d")
    t.write("A WORMHOLE THEORY FILM", align="center", font=("Courier", int(12 + a * 8), "bold"))
    screen.update()

# === SCENE 1: THE BREAKFAST SIGNAL ===
try:
    screen.bgpic(f"{ASSETS}/code_rain.png")
except:
    pass
cls()
t.penup()
t.goto(0, 200)
t.color("#00ff41")
t.write("SCENE 1: THE BREAKFAST SIGNAL", align="center", font=("Courier", 18, "bold"))
screen.update()
time.sleep(2)

cls()
draw_laptop()
t.penup()
t.goto(-100, 120)
t.color("#888888")
t.write("KEVIN (Karthikeya) - Coding...", align="left", font=("Courier", 10, "normal"))
screen.update()
time.sleep(2)

code_rain(20)

t.penup()
t.goto(-200, 150)
t.color("#ffaa00")
t.write("MOM (O.S.): Kevin! Breakfast is ready!", align="left", font=("Courier", 12, "bold"))
screen.update()
say("Kevin! Breakfast is ready!")
time.sleep(2)

cls()
t.penup()
t.goto(-200, 150)
t.color("#00d4ff")
t.write("KEVIN: Two minutes, Mom!", align="left", font=("Courier", 12, "bold"))
t.penup()
t.goto(-200, 120)
t.color("#888888")
t.write("*still typing*", align="left", font=("Courier", 10, "normal"))
screen.update()
say("Two minutes, Mom!")
time.sleep(2)

code_rain(15)

t.penup()
t.goto(-200, 150)
t.color("#ffaa00")
t.write("MOM (O.S.): Kevin! Come eat right now!", align="left", font=("Courier", 12, "bold"))
screen.update()
say("Kevin! Come eat right now, it's getting cold!")
time.sleep(1.5)

cls()
t.penup()
t.goto(-200, 150)
t.color("#00d4ff")
t.write("KEVIN: Okay, okay, jeez!", align="left", font=("Courier", 12, "bold"))
screen.update()
say("Okay, okay, jeez!")
time.sleep(1.5)

glitch(20)

t.penup()
t.goto(0, 200)
t.color("#ff0000")
t.write("!!! SYSTEM GLITCH DETECTED !!!", align="center", font=("Courier", 16, "bold"))
screen.update()
time.sleep(2)

try:
    screen.bgpic(f"{ASSETS}/portal.png")
except:
    pass
portal_pulse(40)

t.penup()
t.goto(0, -200)
t.color("#00d4ff")
t.write("A DIMENSIONAL PORTAL IS OPENING...", align="center", font=("Courier", 14, "bold"))
screen.update()
time.sleep(3)

fade_to_black()

# === SCENE 2: THE BLUEPRINT ===
try:
    screen.bgpic(f"{ASSETS}/blueprint.png")
except:
    pass
cls()
t.penup()
t.goto(0, 200)
t.color("#00d4ff")
t.write("SCENE 2: THE BLUEPRINT", align="center", font=("Courier", 18, "bold"))
screen.update()
time.sleep(2)

cls()
t.penup()
t.goto(-450, 180)
t.color("#00d4ff")
monologue = (
    "Log entry: June 21, 2026. "
    "The portal in my bedroom is real, but it's unstable. "
    "Normal gravity is trying to crush it shut. "
    "I call it the Pulsed Casimir Array. "
    "Millions of microscopic plates, firing all at the exact same nanosecond. "
    "The repulsive gravity of the exotic matter core pushes space-time outward, "
    "holding the wormhole mouth open. "
    "All I need now... is to build it."
)
dialogue_lines = [
    "KEVIN (addressing camera):",
    "",
    "Log entry: June 21, 2026.",
    "The portal in my bedroom is real,",
    "but it's unstable.",
    "Normal gravity is trying to crush it shut.",
    "",
    "I call it the Pulsed Casimir Array.",
    "Millions of microscopic plates,",
    "firing all at the exact same nanosecond.",
    "The repulsive gravity of the exotic matter",
    "core pushes space-time outward,",
    "holding the wormhole mouth open.",
    "",
    "All I need now... is to build it.",
]
for i, line in enumerate(dialogue_lines):
    t.penup()
    t.goto(-450, 180 - i * 22)
    if i == 0:
        t.color("#00d4ff")
    elif line:
        t.color("#ffffff")
    else:
        t.color("#ffffff")
    t.write(line, align="left", font=("Courier", 10, "normal"))
screen.update()
say(monologue)
time.sleep(14)

fade_to_black()

# === WORMHOLE REVEAL ===
try:
    screen.bgpic(f"{ASSETS}/wormhole_diagram.png")
except:
    pass
cls()
for i in range(30):
    cls()
    a = i / 30
    t.penup()
    t.goto(0, 200 - a * 300)
    t.color("#ff2a6d")
    t.write("THE WORMHOLE IS READY", align="center", font=("Courier", int(12 + a * 14), "bold"))
    screen.update()

t.penup()
t.goto(0, -180)
t.color("#888888")
t.write("Earth Station to Magnetar - 13,000 Light-Years", align="center", font=("Courier", 10, "normal"))
screen.update()
time.sleep(3)

for i in range(25):
    cls()
    a = i / 25
    t.penup()
    t.goto(0, 300 - a * 200)
    t.color("#ffaa00")
    t.write("WATCH THE SKIES", align="center", font=("Courier", int(20 - a * 12), "bold"))
    t.penup()
    t.goto(0, 250 - a * 200)
    t.color("#aaaaaa")
    t.write("Karthikeya's Wormhole Theory - 2026", align="center", font=("Courier", int(10 - a * 4), "normal"))
    screen.update()

# === CREDITS ===
fade_to_black()

cls()
draw_stars(80)
t.penup()
t.goto(0, 200)
t.color("#00d4ff")
t.write("THE ECHO FREQUENCIES", align="center", font=("Courier", 24, "bold"))
t.penup()
t.goto(0, 160)
t.color("#ff2a6d")
t.write("A Karthikeya Production", align="center", font=("Courier", 12, "bold"))
t.penup()
t.goto(0, 120)
t.color("#888888")
t.write("Director: Karthikeya", align="center", font=("Courier", 10, "normal"))
t.penup()
t.goto(0, 90)
t.color("#888888")
t.write("Cast: Mr. Python & Ms. Matplotlib", align="center", font=("Courier", 10, "normal"))
t.penup()
t.goto(0, 50)
t.color("#aaaaaa")
t.write("Based on actual wormhole physics research", align="center", font=("Courier", 9, "normal"))
t.penup()
t.goto(0, 20)
t.color("#aaaaaa")
t.write("Morris-Thorne Metric | Schwinger Limit | Unified Polarity", align="center", font=("Courier", 9, "normal"))
t.penup()
t.goto(0, -20)
t.color("#666666")
t.write("Thank you for watching", align="center", font=("Courier", 14, "italic"))
t.penup()
t.goto(0, -60)
t.color("#ff2a6d")
t.write("the system falls", align="center", font=("Courier", 10, "normal"))
screen.update()
time.sleep(5)

fade_to_black()

screen.bgpic("")
cls()
t.penup()
t.goto(0, 0)
t.color("#00d4ff")
t.write("THE END", align="center", font=("Courier", 36, "bold"))
screen.update()
time.sleep(4)

print("=== MOVIE COMPLETE ===")
print("THE ECHO FREQUENCIES")
print("A Karthikeya Production")
