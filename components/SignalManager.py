class SignalManager:
    """
    مدیریت سیگنال‌های سفارشی در pygame.
    با این کلاس می‌توانید سیگنال جدید تعریف کنید، به آن تابع متصل کنید و آن را فراخوانی (emit) کنید.
    """
    def __init__(self):
        # نگاشت نام سیگنال به شناسه‌ی رویداد pygame
        self._signals = {}
        # نگاشت نام سیگنال به لیست توابع متصل شده
        self._callbacks = {}
        # شمارنده برای شناسه‌های رویداد سفارشی
        self._next_event_id = pygame.USEREVENT

    def addSignal(self, name: str) -> int:
        """
        یک سیگنال جدید با نام مشخص تعریف می‌کند.
        اگر سیگنال از قبل وجود داشته باشد، همان شناسه را برمی‌گرداند.

        :param name: نام یکتای سیگنال
        :return: شناسه‌ی عددی رویداد pygame که به این سیگنال اختصاص یافته است.
        """
        if name not in self._signals:
            event_id = self._next_event_id
            self._signals[name] = event_id
            self._callbacks[name] = []
            self._next_event_id += 1
        return self._signals[name]

    def registerSignal(self, name: str, callback: callable):
        """
        یک تابع (callback) را به سیگنالی که قبلاً با addSignal تعریف شده وصل می‌کند.
        اگر سیگنال وجود نداشته باشد، خطا ایجاد می‌شود.

        :param name: نام سیگنال
        :param callback: تابعی که هنگام رویداد صدا زده می‌شود.
                         این تابع یک دیکشنری از داده‌های رویداد را دریافت می‌کند.
        """
        if name not in self._signals:
            raise ValueError(f"Signal '{name}' not found. Use addSignal first.")
        self._callbacks[name].append(callback)

    def emit(self, name: str, **data):
        """
        سیگنال را با داده‌های دلخواه ارسال (post) می‌کند.
        یک رویداد سفارشی در صف رویدادهای pygame قرار می‌دهد.

        :param name: نام سیگنال
        :param data: آرگومان‌های کلیدی که به رویداد اضافه می‌شوند.
                     بعداً توسط callback دریافت می‌شوند.
        """
        if name not in self._signals:
            raise ValueError(f"Signal '{name}' not found. Use addSignal first.")
        event_id = self._signals[name]
        event = pygame.event.Event(event_id, **data)
        pygame.event.post(event)

    def process(self):
        """
        باید در هر دور از حلقه‌ی اصلی بازی فراخوانی شود.
        تمام رویدادهای موجود در صف pygame را بررسی می‌کند و
        در صورت تطابق با سیگنال‌های ثبت‌شده، callback‌های مربوطه را صدا می‌زند.

        توجه: این تابع فقط رویدادهای مربوط به سیگنال‌های سفارشی را پردازش می‌کند.
        برای رویدادهای استاندارد (مانند QUIT) باید جداگانه بررسی کنید.
        """
        for event in pygame.event.get():
            # بررسی رویدادهای سفارشی
            for name, event_id in self._signals.items():
                if event.type == event_id:
                    # استخراج دیکشنری داده‌ها به جز 'type' که مربوط به pygame است
                    data = {k: v for k, v in event.dict.items() if k != 'type'}
                    for callback in self._callbacks[name]:
                        callback(data)
                    # پس از فراخوانی callbackها، رویداد مصرف می‌شود
                    # اما در این پیاده‌سازی رویداد از صف حذف نمی‌شود چون pygame.event.get()
                    # همه رویدادها را بیرون می‌کشد. اگر نیاز به نگه‌داشتن دیگر رویدادها دارید،
                    # می‌توانید آن‌ها را دوباره post کنید.
            # اگر می‌خواهید رویدادهای استاندارد (مانند QUIT) نیز بررسی شوند،
            # باید اینجا کد اضافی بنویسید. برای انعطاف‌پذیری،
            # می‌توانید process فقط رویدادهای سیگنال را مصرف کند و بقیه را نادیده بگیرد،
            # یا همه رویدادها را برگرداند. اینجا روش ساده‌تر ارائه شده.