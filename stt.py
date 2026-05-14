import speech_recognition as sr

# یک شیء شناساگر بساز
r = sr.Recognizer()

# از میکروفون پیش‌فرض استفاده کن
with sr.Microphone() as source:
    print("صحبت کن...")
    # تنظیم برای نویز محیط (یک ثانیه گوش می‌دهد تا نویز پس‌زمینه را بسنجد)
    r.adjust_for_ambient_noise(source)
    # گوش دادن به صدای کاربر تا وقتی سکوت کند
    audio = r.listen(source)

# حالا صدای ضبط شده را با گوگل به متن تبدیل کن (فارسی)
try:
    text = r.recognize_google(audio, language="fa-IR")
    print("تو گفتی: " + text)
except sr.UnknownValueError:
    print("متوجه نشدم")
except sr.RequestError as e:
    print("خطا در اتصال به سرویس گوگل: {0}".format(e))