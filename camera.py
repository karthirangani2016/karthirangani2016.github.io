import subprocess
import io
import struct
from PIL import Image

WIDTH = 640
HEIGHT = 480

def capture_raw():
    result = subprocess.run(
        ["v4l2-ctl", "--set-fmt-video=width=640,height=480",
         "--stream-mmap", "--stream-count=1", "--stream-to=/tmp/__cam.raw",
         "-d", "/dev/video0"],
        capture_output=True, timeout=5
    )
    with open("/tmp/__cam.raw", "rb") as f:
        data = f.read()
    return data

def yuyv_to_rgb(data, w, h):
    rgb = bytearray(w * h * 3)
    for i in range(0, w * h * 2, 4):
        y0 = data[i]
        u  = data[i + 1] - 128
        y1 = data[i + 2]
        v  = data[i + 3] - 128
        for j, (y, idx) in enumerate([(y0, i // 2 * 3), (y1, i // 2 * 3 + 3)]):
            r = max(0, min(255, int(y + 1.402 * v)))
            g = max(0, min(255, int(y - 0.344 * u - 0.714 * v)))
            b = max(0, min(255, int(y + 1.772 * u)))
            rgb[idx:idx+3] = [r, g, b]
    return bytes(rgb)

def get_jpeg():
    raw = capture_raw()
    rgb = yuyv_to_rgb(raw, WIDTH, HEIGHT)
    img = Image.frombytes("RGB", (WIDTH, HEIGHT), rgb)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    return buf.getvalue()
