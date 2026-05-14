import pyttsx3

engine = pyttsx3.init()
# تنظیم صدا روی فارسی (با جستجو در لیست voices)
voices = engine.getProperty('voices')
for voice in voices:
    if 'persian' in voice.name.lower() or 'fa' in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break
engine.say("سلام جهان بی نهایت")
engine.runAndWait()