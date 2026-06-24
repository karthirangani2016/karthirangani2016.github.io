import subprocess
import sys
import os

# Store log in a more accessible place if the local dir is locked
LOG_FILE = "/tmp/sea_voice_debug.log"

def log(message):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{message}\n")
    except:
        pass # Silently fail if we can't log

def speak(text):
    log(f"Attempting to speak via direct pipe: {text}")
    try:
        # We pipe espeak-ng to aplay and target Card 1 (the AUX jack)
        # Using plughw:1,0 ensures sample rate compatibility
        cmd = f'espeak-ng "{text}" --stdout | aplay -D plughw:1,0'
        subprocess.run(cmd, shell=True, check=True)
        log("Speech finished successfully via pipe.")
    except Exception as e:
        log(f"VOICE ERROR: {str(e)}")
        # Fallback to standard pyttsx3 just in case
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e2:
            log(f"FALLBACK ERROR: {str(e2)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        speak(text)
    else:
        log("No text provided to voice.py")
