"""
A simple, extensible dialogue tree library for Python.
Supports nodes with text, choices with optional callbacks and conditions.
"""

from typing import Callable, Optional, Dict, Any


class Choice:
    """یک انتخاب در درخت دیالوگ."""

    def __init__(
        self,
        text: str,
        next_node: Optional[str] = None,
        callback: Optional[Callable[..., Any]] = None,
        condition: Optional[Callable[..., bool]] = None,
    ):
        """
        Args:
            text: متن نمایشی انتخاب.
            next_node: شناسهٔ گره‌ای که پس از این انتخاب فعال می‌شود (یا None).
            callback: تابعی که هنگام انتخاب اجرا می‌شود (می‌تواند None باشد).
            condition: تابعی که True/False برمی‌گرداند؛ اگر False باشد انتخاب نشان داده نمی‌شود.
        """
        self.text = text
        self.next_node = next_node
        self.callback = callback
        self.condition = condition

    def is_available(self, **kwargs) -> bool:
        """بررسی می‌کند که آیا انتخاب در شرایط فعلی مجاز است یا خیر."""
        if self.condition is None:
            return True
        return self.condition(**kwargs)


class Node:
    """یک گره در درخت دیالوگ (جمله‌ای که یک شخصیت می‌گوید)."""

    def __init__(self, speaker: str, text: str, choices: Optional[list[Choice]] = None):
        """
        Args:
            speaker: نام گوینده.
            text: متن دیالوگ.
            choices: لیست انتخاب‌های ممکن پس از این دیالوگ.
        """
        self.speaker = speaker
        self.text = text
        self.choices = choices if choices is not None else []


class DialogueTree:
    """مدیریت و پیمایش درخت دیالوگ."""

    def __init__(self, nodes: Optional[Dict[str, Node]] = None, start_node: str = "start"):
        """
        Args:
            nodes: دیکشنری از شناسهٔ گره به شیء Node.
            start_node: شناسهٔ گرهٔ آغازین.
        """
        self.nodes = nodes if nodes is not None else {}
        self.start_node = start_node
        self.current_node_id: Optional[str] = None
        self.is_active = False

    def add_node(self, node_id: str, node: Node) -> None:
        """افزودن یک گره به درخت."""
        self.nodes[node_id] = node

    def start(self) -> None:
        """شروع (یا بازنشانی) درخت دیالوگ از گرهٔ آغازین."""
        if self.start_node not in self.nodes:
            raise KeyError(f"Start node '{self.start_node}' not found.")
        self.current_node_id = self.start_node
        self.is_active = True

    def get_current_node(self) -> Node:
        """گرهٔ فعلی را برمی‌گرداند (اگر فعال باشد)."""
        if not self.is_active or self.current_node_id is None:
            raise RuntimeError("Dialogue tree is not active.")
        return self.nodes[self.current_node_id]

    def get_available_choices(self, **kwargs) -> list[Choice]:
        """لیست انتخاب‌های مجاز گرهٔ فعلی را برمی‌گرداند."""
        node = self.get_current_node()
        return [ch for ch in node.choices if ch.is_available(**kwargs)]

    def select_choice(self, choice_index: int, **kwargs) -> Optional[str]:
        """
        یک انتخاب را بر اساس اندیس آن در لیست انتخاب‌های مجاز اعمال می‌کند.
        ابتدا callback (در صورت وجود) اجرا می‌شود، سپس در صورت وجود next_node
        به آن گره منتقل می‌شویم. اگر next_node نداشته باشد، درخت پایان می‌یابد.

        Returns:
            شناسهٔ گرهٔ جدید (در صورت وجود) یا None اگر دیالوگ تمام شده باشد.
        """
        available = self.get_available_choices(**kwargs)
        if choice_index < 0 or choice_index >= len(available):
            raise IndexError("Invalid choice index.")

        chosen = available[choice_index]

        # اجرای callback در صورت وجود
        if chosen.callback is not None:
            chosen.callback(**kwargs)

        # انتقال به گرهٔ بعدی یا پایان دیالوگ
        if chosen.next_node is not None:
            if chosen.next_node not in self.nodes:
                raise KeyError(f"Node '{chosen.next_node}' not found.")
            self.current_node_id = chosen.next_node
            return chosen.next_node
        else:
            self.is_active = False
            self.current_node_id = None
            return None

    def is_finished(self) -> bool:
        """True اگر دیالوگ تمام شده باشد."""
        return not self.is_active


# ------------------- مثال استفاده -------------------
if __name__ == "__main__":
    # وضعیت بازی (برای شرط‌ها و callbackها)
    game_state = {
        "gold": 0, 
        "has_sword": False,
        "has_carpet": False,
        "tasted_sweet": False,
        "heard_music": False,
        "visited_mosque": False,
        "visited_arg": False,
        "has_tasted_noghl": False,
        "has_kilim": False
    }

    def touch_kilim_cb(**kwargs):
        print("👋 حس می‌کنی بافت زبر و گرم گلیم کردی زیر انگشتانت. برجستگی نخ‌ها تو را به یاد دستان زنان عشایر می‌اندازد که ساعت‌ها پای دار قالی نشسته‌اند.")

    def taste_noghl_cb(**kwargs):
        game_state["has_tasted_noghl"] = True
        print("🍬 نقل کوچک و سفید در دهانت می‌شکند. عطر هل و گلاب آرام‌آرام پخش می‌شود، شیرینی‌اش با طعم گلاب نوازش می‌کند.")

    def buy_kilim_cb(**kwargs):
        game_state["has_kilim"] = True
        print("🧶 یک گلیم کردی زیبا انتخاب می‌کنی و بوی پشم و خاک کوهستان را با خود همراه می‌سازی.")

    def qara_sound_cb(**kwargs):
        print("🔊 صدای در چوبی قدیمی که آرام باز می‌شود، باد سردی از لای درز سنگ‌ها می‌وزد و خنکای سنگ‌های چندصدساله را روی کف دستت حس می‌کنی.")

    def takht_sound_cb(**kwargs):
        print("🍃 سوت آرام باد کوهستان در میان ویرانه‌های سنگی می‌پیچد. موج‌های ملایم دریاچه، ریتمی آرامش‌بخش می‌نوازند.")

    def stay_sunset_cb(**kwargs):
        print("🌄 علی تا غروب می‌ماند. آسمان به رنگ‌های نارنجی و بنفش درمی‌آید و سکوت کوه‌ها، داستانی بی‌کلام از تاریخ را زمزمه می‌کند.")

    def return_home_cb(**kwargs):
        items = []
        if game_state["has_kilim"]:
            items.append("گلیم کردی")
        if game_state["has_tasted_noghl"]:
            items.append("نقل ارومیه")
        souvenir_str = " و ".join(items) if items else "دل پر از خاطره"
        print(f"🏠 علی با {souvenir_str} به خانه برمی‌گردد و هر بار که چشمانش را می‌بندد، بوی سنگ و باد کوهستان را حس می‌کند.")

    def legend_end_cb(**kwargs):
        print("🔥 در میان زمزمهٔ باد، علی صدایی باستانی می‌شنود؛ شاید بازتاب آتش مقدس، شاید تنها خیال. اما قلبش سرشار از آرامش می‌شود.")

    def poetic_end_cb(**kwargs):
        print("🌸 طعم نقل و افسانهٔ آتش، در هم می‌آمیزند. علی با چشمان بسته، شعری کهن را زیر لب زمزمه می‌کند و حس می‌کند که روح این سرزمین، در جانش جاری است.")

    def has_tasted_noghl_condition(**kwargs):
        return game_state["has_tasted_noghl"]

    # گره‌ها

    # callback نمونه
    def give_gold(amount=10, **kwargs):
        game_state["gold"] += amount
        print(f"💰 {amount} سکه دریافت کردید! (موجودی: {game_state['gold']})")

    def take_sword(**kwargs):
        game_state["has_sword"] = True
        print("🗡️ یک شمشیر برداشتید!")

    # شرط نمونه
    def is_rich(**kwargs):
        return game_state["gold"] >= 20

    # ---------- callbacks ----------
    def take_carpet(**kwargs):
        game_state["has_carpet"] = True
        print("🧶 یک قالیچه نفیس تبریز به دست آوردی!")

    def taste_qurabiya(**kwargs):
        game_state["tasted_sweet"] = True
        print("🍪 طعم شیرین قرابیه تا آخر سفر زیر زبانت ماند.")

    def listen_music(**kwargs):
        game_state["heard_music"] = True
        print("🎵 نغمهٔ قوپوز مثل نسیم کوهستانی در گوشت پیچید.")

    # ---------- conditions (در صورت نیاز) ----------
    def owns_carpet(**kwargs):
        return game_state["has_carpet"]

    # ---------- ساخت گره‌ها ----------
    azarbaijan_sharghi_nodes = {
        "start": Node(
            speaker="راهنما",
            text="علی جان، به دیار سرسبز و باستانی آذربایجان غربی خوش آمدی! اینجا روی سرِ گربهٔ نقشهٔ ایرانه، غربِ کشور. آب‌وهوایش سرد و کوهستانی‌ست، پر از باغ‌های سیب و چغندرقند. حالا بگو اول دلت می‌خواد بریم بازار ارومیه یا مستقیم سراغ جاهای تاریخی مثل قره‌کلیسا و تخت سلیمان؟",
            choices=[
                Choice("بازار ارومیه", next_node="bazaar"),
                Choice("جاهای تاریخی", next_node="historical_intro"),
            ],
        ),
        "bazaar": Node(
            speaker="راهنما",
            text="اینجا بازار قدیمی ارومیه‌ست. نگاه کن، این گلیم‌های کردی رو می‌بینی؟ پشمشون از گوسفندهای همین کوه‌هاست. می‌خوای دست بکشی روش؟",
            choices=[
                Choice("آره، دست می‌کشم", next_node="touch_kilim"),
                Choice("نه، بریم سراغ نقل", next_node="noghl_offer"),
            ],
        ),
        "touch_kilim": Node(
            speaker="علی",
            text="وای، چه بافت گرم و زبری! برجستگی نخ‌ها رو زیر انگشتام حس می‌کنم. انگار هر گره داستانی از این سرزمین داره.",
            choices=[Choice("حالا نقل رو امتحان کنم", next_node="noghl_offer")
                     ,Choice("(حس لمس گلیم)", callback=touch_kilim_cb, next_node="noghl_offer")],
        ),
        # اصلاح: callbackها تنها روی Choiceها قرار می‌گیرند. گره‌ها فقط speaker, text, choices دارند.
        # پس callback را به انتخاب‌های مناسب منتقل می‌کنیم.
        # برای touch_kilim: بعد از نمایش متن، با یک انتخاب callback را اجرا کنیم.
        "touch_kilim": Node(
            speaker="علی",
            text="وای، چه بافت گرم و زبری! برجستگی نخ‌ها رو زیر انگشتام حس می‌کنم. انگار هر گره داستانی از این سرزمین داره.",
            choices=[
                Choice("(حس لمس گلیم)", callback=touch_kilim_cb, next_node="noghl_offer"),
            ],
        ),
        "noghl_offer": Node(
            speaker="راهنما",
            text="اینم نقل ارومیه. دونه‌های کوچیک سفید که توی دهنت آب می‌شن. بفرما، یکی بردار.",
            choices=[
                Choice("می‌چشم", next_node="taste_noghl"),
                Choice("نه ممنون، ادامه بدیم", next_node="skip_noghl"),
            ],
        ),
        "taste_noghl": Node(
            speaker="علی",
            text="چه طعمی! شیرینی ملایمش با عطر گلاب و هل قاطی شده. تازه، حس می‌کنم هوای خنک کوهستان رو هم می‌شه توی این نقل پیدا کرد.",
            choices=[
                Choice("(نقل را بچش)", callback=taste_noghl_cb, next_node="after_tasting"),
            ],
        ),
        "after_tasting": Node(
            speaker="راهنما",
            text="نوش جونت! حالا می‌خوای یکی از این گلیم‌ها رو هم بخری یا بریم سراغ قره‌کلیسا؟",
            choices=[
                Choice("گلیم رو می‌خرم", next_node="buy_kilim"),
                Choice("بریم قره‌کلیسا", next_node="qara_kelisa_intro"),
            ],
        ),
        "skip_noghl": Node(
            speaker="راهنما",
            text="حیف شد، نقل ارومیه رو از دست دادی. خب، گلیم می‌خوای یا مستقیم بریم جاهای تاریخی؟",
            choices=[
                Choice("گلیم رو می‌خرم", next_node="buy_kilim"),
                Choice("بریم قره‌کلیسا", next_node="qara_kelisa_intro"),
            ],
        ),
        "buy_kilim": Node(
            speaker="راهنما",
            text="این گلیم مال تو. بوی پشم طبیعی و کوهستان همرات باشه. حالا آماده‌ای بریم قره‌کلیسا؟",
            choices=[
                Choice("بریم", callback=buy_kilim_cb, next_node="qara_kelisa_intro"),
            ],
        ),
        "historical_intro": Node(
            speaker="راهنما",
            text="پس یکراست می‌ریم به قره‌کلیسا، کلیسای باستانی‌ای که به «کلیسای سیاه» معروفه. سنگ‌های خنکش منتظر دستای توئن.",
            choices=[
                Choice("همین حالا بریم", next_node="qara_kelisa_intro"),
            ],
        ),
        "qara_kelisa_intro": Node(
            speaker="راهنما",
            text="اینجا قره‌کلیساست. دستت رو بذار روی دیوار سنگی. سرد و ناهمواره، نه؟ هر ترکش قصه‌ای داره.",
            choices=[
                Choice("دست می‌کشم روی سنگ‌ها", next_node="qara_touch"),
                Choice("بعداً، بریم تخت سلیمان", next_node="takht_intro"),
            ],
        ),
        "qara_touch": Node(
            speaker="علی",
            text="سطح خنک و ناهموار سنگ‌ها رو حس می‌کنم. انگار صدها سال باد و باران از اینجا رد شده. وای، گوش کن...",
            choices=[
                Choice("(صدای در و باد)", callback=qara_sound_cb, next_node="after_qara"),
            ],
        ),
        "after_qara": Node(
            speaker="راهنما",
            text="صدای در چوبی بود که باد تکونی‌اش داد. بیا بریم تخت سلیمان، کنار دریاچه‌ای میان کوه‌ها.",
            choices=[
                Choice("بریم تخت سلیمان", next_node="takht_intro"),
            ],
        ),
        "takht_intro": Node(
            speaker="راهنما",
            text="به تخت سلیمان رسیدیم. بقایای ساختمان‌های سنگی کنار این دریاچهٔ آروم. باد کوهستان رو حس می‌کنی؟ خب، می‌خوای چیکار کنی؟",
            choices=[
                Choice("سکوت کنم و به باد و موج گوش بدم", next_node="takht_experience"),
                Choice("برم بالای تپه", next_node="climb_hill"),
            ],
        ),
        "takht_experience": Node(
            speaker="علی",
            text="سوت آرام باد لای سنگ‌ها می‌پیچه، موج‌های ملایم دریاچه رو می‌شمرم. اینجا زمان متوقف شده.",
            choices=[
                Choice("(باد و موج)", callback=takht_sound_cb, next_node="ending_choice"),
            ],
        ),
        "climb_hill": Node(
            speaker="علی",
            text="از تپه بالا می‌رم. نفس‌گیره! کل دشت و دریاچه زیر پامه. باد سرد کوهستان صورت رو نوازش می‌ده.",
            choices=[
                Choice("(منظره را ببین)", callback=lambda **kw: print("⛰️ علی چشم‌انداز را نگاه می‌کند."), next_node="ending_choice"),
            ],
        ),
        "ending_choice": Node(
            speaker="راهنما",
            text="علی جان، تصمیم آخر رو بگیر. می‌خوای همین‌جا بمونی تا غروب، برگردیم شهر، یا افسانهٔ اینجا رو بشنوی؟",
            choices=[
                Choice("همین‌جا می‌مانم و غروب را می‌بینم", next_node="stay_sunset"),
                Choice("برگردیم شهر", next_node="return_home"),
                Choice("افسانهٔ تخت سلیمان رو بگو", next_node="legend_telling"),
                Choice(
                    "نقل خوردم... شاید حس متفاوتی دارم، افسانه رو با طعم نقل بشنوم",
                    next_node="poetic_ending",
                    condition=has_tasted_noghl_condition,
                ),
            ],
        ),
        "stay_sunset": Node(
            speaker="علی",
            text="می‌مانم. آسمان کم‌کم نارنجی می‌شه و سکوت کوه‌ها بغل می‌کنه. حس می‌کنم خود این سرزمین داره قصه‌اش رو تعریف می‌کنه.",
            choices=[
                Choice("(پایان)", callback=stay_sunset_cb),
            ],
        ),
        "return_home": Node(
            speaker="علی",
            text="باشه، برگردیم. ولی این بوها و صداها رو با خودم می‌برم.",
            choices=[
                Choice("(پایان)", callback=return_home_cb),
            ],
        ),
        "legend_telling": Node(
            speaker="راهنما",
            text="می‌گن اینجا زمانی آتشکده‌ای بزرگ بوده، آتش مقدس توش روشن. این دریاچه هم پر از رازه. می‌گن هرکی با دل پاک بیاد، زمزمه‌های باستانی رو می‌شنوه.",
            choices=[
                Choice("من چیزی حس می‌کنم...", next_node="legend_end"),
            ],
        ),
        "legend_end": Node(
            speaker="علی",
            text="در میان باد، صدایی کهن می‌شنوم. شاید آتش مقدس، شاید خیال. اما آرامش عمیقی وجودم رو پر می‌کنه.",
            choices=[
                Choice("(پایان)", callback=legend_end_cb),
            ],
        ),
        "poetic_ending": Node(
            speaker="علی",
            text="طعم نقل توی دهانم با افسانهٔ آتش می‌آمیزه. چشم‌ها رو می‌بندم و شعری کهن از یادم می‌گذره. روح این سرزمین توی جانم جاری شده.",
            choices=[
                Choice("(پایان)", callback=poetic_end_cb),
            ],
        ),
    }

    azarbaijan_gharbi_nodes = {
        "start": Node(
            speaker="راوی",
            text="علی از میان هوای سرد و کوهستانی تبریز قدم به محله‌ی قدیمی می‌گذارد. بوی بابونه و سیب از باغچه‌های کنار خیابان بلند می‌شود. پیرمردی رهگذر با لهجه‌ای گرم می‌گوید: «سلام سنیز ندی؟» علی لبخند می‌زند. شهر در برابرش گسترده است؛ کدام سو را برگزیند؟",
            choices=[
                Choice("وارد بازار بزرگ تبریز بشود.", next_node="bazaar"),
                Choice("به مسجد کبود برود.", next_node="blue_mosque"),
                Choice("به سوی ارگ علیشاه روانه شود.", next_node="arg_alishah"),
            ],
        ),
        # --- بازار ---
        "bazaar": Node(
            speaker="راوی",
            text="بازار بزرگ تبریز با طاق‌های آجری و صدای همهمهٔ بازرگانان زنده است. عطر ادویه و چرم تازه با هوای خنک در هم آمیخته. علی در دالان‌های تو در تو، دکان فرش‌فروشی و شیرینی‌فروشی را کنار هم می‌بیند. صدای قوپوز هم از کوچ‌های نزدیک می‌آید.",
            choices=[
                Choice("به دکان فرش نزدیک شود.", next_node="carpet_shop"),
                Choice("سراغ شیرینی‌فروش برود.", next_node="sweet_shop"),
                Choice("دنبال صدای قوپوز برود.", next_node="music_alley"),
            ],
        ),
        # --- فرش ---
        "carpet_shop": Node(
            speaker="راوی",
            text="علی وارد دکان می‌شود. قالی‌های تبریز چون باغی از رنگ و نقش پیش چشمش گسترده‌اند. دستش را روی یکی از آنها می‌کشد: تار و پودهای ضخیم و نرم زیر انگشتانش جان می‌گیرند و گره‌های ریز مثل برجستگی‌های منظم ردیف شده‌اند. فروشنده نگاهش می‌کند: «هر گره‌اش یک نفس هنرمند است.»",
            choices=[
                Choice("قالی را بخرد و با خود ببرد.", next_node="ending_carpet", callback=take_carpet),
                Choice("تشکر کند و از دکان بیرون برود.", next_node="bazaar"),
            ],
        ),
        # --- شیرینی ---
        "sweet_shop": Node(
            speaker="راوی",
            text="در دکان شیرینی‌فروشی، سینی‌های بزرگ قرابیه با خلال‌های بادام پیش چشم علی ردیف شده‌اند. یک تکه را گاز می‌زند: رویش پُر از خلال بادام، نرم و کمی ترد؛ بوی شیرین بادام و شکر در دهانش می‌پیچد. انگار طعم تاریخ را می‌چشد.",
            choices=[
                Choice("بسته‌ای قرابیه بخرد.", next_node="ending_sweet", callback=taste_qurabiya),
                Choice("به گشت خود در بازار ادامه بدهد.", next_node="bazaar"),
            ],
        ),
        # --- موسیقی ---
        "music_alley": Node(
            speaker="راوی",
            text="علی به کوچه‌ای باریک می‌رسد. نوازنده‌ای دوره‌گرد، قوپوز را به سینه فشرده و موتیف عاشیقی ۵ ثانیه‌ای را چنان می‌نوازد که گویی باد کوهستان از لای سیم‌ها می‌گذرد. تمام تنش غرق در آن نغمه می‌شود.",
            choices=[
                Choice("بماند و تا پایان قطعه گوش کند.", next_node="ending_music", callback=listen_music),
                Choice("سکه‌ای در کاسه‌اش بیندازد و برود.", next_node="bazaar"),
            ],
        ),
        # --- مسجد کبود ---
        "blue_mosque": Node(
            speaker="راوی",
            text="علی به مسجد کبود می‌رسد. از درگاه که وارد می‌شود، زیر گنبدی می‌ایستد که دیوارهایش با کاشی‌های آبی تیره پوشیده شده. دستش را روی دیوار می‌کشد: سطح سرد و صاف کاشی‌ها را حس می‌کند. صدای قدم‌هایش آرام در فضای بزرگ می‌پیچد و پژواکی خفیف می‌سازد.",
            choices=[
                Choice("زیر گنبد بایستد و گوش بسپارد.", next_node="ending_mosque"),
                Choice("نماز بخواند و بیرون بیاید.", next_node="ending_mosque"),
            ],
        ),
        # --- ارگ علیشاه ---
        "arg_alishah": Node(
            speaker="راوی",
            text="ارگ علیشاه چون کوهی از آجر در برابر علی قد برافراشته. نزدیک دیوار عظیم و ضخیمش که می‌ایستد، عظمتش را با تمام وجود حس می‌کند. باد سردی به دیوار می‌خورد و پژواکی کوتاه از میان آجرهای کهنه می‌پیچد. صدای علی کنار این غول خشتی گم می‌شود.",
            choices=[
                Choice("از پله‌ها بالا برود.", next_node="ending_arg"),
                Choice("همان پایین، اطراف ارگ قدم بزند.", next_node="ending_arg"),
            ],
        ),
        # ---------- پایان‌ها ----------
        "ending_carpet": Node(
            speaker="راوی",
            text="علی قالی‌چه‌ای را با خود دارد که هر گره‌اش بوی تاریخ و هنر تبریز را می‌دهد. انگشتانش هنوز لطافت تار و پود را به خاطر دارند. او با گنجی از فرهنگ این سرزمین به راهش ادامه می‌دهد.",
            choices=[Choice("پایان", callback=lambda **kw: print("🧵 پایان: گره‌های ماندگار"))],
        ),
        "ending_sweet": Node(
            speaker="راوی",
            text="طعم شیرین قرابیه و بوی بادام، سفر علی را شیرین‌تر از هر مقصدی کرده است. تبریز را با مزه‌ای فراموش‌نشدنی ترک می‌کند.",
            choices=[Choice("پایان", callback=lambda **kw: print("🍬 پایان: طعم سفر"))],
        ),
        "ending_music": Node(
            speaker="راوی",
            text="ملودی قوپوز در گوش علی می‌ماند، انگار رشته‌ای نامرئی او را به جان این دیار گره زده است. با خود فکر می‌کند تبریز فقط یک شهر نیست، یک نغمه است.",
            choices=[Choice("پایان", callback=lambda **kw: print("🎶 پایان: آوای تبریز"))],
        ),
        "ending_mosque": Node(
            speaker="راوی",
            text="زیر گنبد کبود، سکوت چنان سنگین است که تنها صدای قدم‌ها و نفس‌ها به گوش می‌رسد. علی احساس می‌کند در آغوش آرامش ابدی شهر قرار گرفته است. از مسجد که بیرون می‌آید، نگاهش به آسمان آذربایجان روشن‌تر است.",
            choices=[Choice("پایان", callback=lambda **kw: print("🕌 پایان: زیر گنبد نیلگون"))],
        ),
        "ending_arg": Node(
            speaker="راوی",
            text="در برابر شکوه ارگ، علی به کوچکی خود پی می‌برد. بادی که از میان آجرهای کهنه می‌وزد، زمزمه‌ی قرن‌ها تاریخ را در گوشش زنده می‌کند. او سکوت می‌کند و به عظمت تبریز سر تعظیم فرود می‌آورد.",
            choices=[Choice("پایان", callback=lambda **kw: print("🏰 پایان: دیوار جاودان"))],
        ),
    }    # راه‌اندازی درخت
    
    def azarbaijan_gharbi():
        tree = DialogueTree(azarbaijan_gharbi_nodes, start_node="start")
        tree.start()
        # شبیه‌سازی یک تعامل ساده در کنسول (اختیاری)
        while not tree.is_finished():
            node = tree.get_current_node()
            print(f"\n🗣️ {node.speaker}: {node.text}")
            available = tree.get_available_choices()
            if not available:
                print("(هیچ انتخابی موجود نیست، دیالوگ پایان می‌یابد.)")
                break
            for i, ch in enumerate(available):
                print(f"  [{i}] {ch.text}")
            try:
                idx = int(input("انتخاب شما: "))
                tree.select_choice(idx)
            except (ValueError, IndexError):
                print("انتخاب نامعتبر.")
    def azarbaijan_shargi():
        tree = DialogueTree(azarbaijan_sharghi_nodes, start_node="start")
        tree.start()
        # شبیه‌سازی یک تعامل ساده در کنسول (اختیاری)
        while not tree.is_finished():
            node = tree.get_current_node()
            print(f"\n🗣️ {node.speaker}: {node.text}")
            available = tree.get_available_choices()
            if not available:
                print("(هیچ انتخابی موجود نیست، دیالوگ پایان می‌یابد.)")
                break
            for i, ch in enumerate(available):
                print(f"  [{i}] {ch.text}")
            try:
                idx = int(input("انتخاب شما: "))
                tree.select_choice(idx)
            except (ValueError, IndexError):
                print("انتخاب نامعتبر.")
    
    nodes = {
        "start": Node(
            speaker="سیستم",
            text="کدام یک از شهر ها را ابتدا می بینید",
            choices=[
                Choice("آذربایجان شرقی",callback=azarbaijan_shargi),
                Choice("آذربایجان",callback=azarbaijan_gharbi)
            ]
        )
    }
    tree = DialogueTree(nodes, start_node="start")
    tree.start()

    # شبیه‌سازی یک تعامل ساده در کنسول (اختیاری)
    while not tree.is_finished():
        node = tree.get_current_node()
        print(f"\n🗣️ {node.speaker}: {node.text}")
        available = tree.get_available_choices()
        if not available:
            print("(هیچ انتخابی موجود نیست، دیالوگ پایان می‌یابد.)")
            break
        for i, ch in enumerate(available):
            print(f"  [{i}] {ch.text}")
        try:
            idx = int(input("انتخاب شما: "))
            tree.select_choice(idx)
        except (ValueError, IndexError):
            print("انتخاب نامعتبر.")