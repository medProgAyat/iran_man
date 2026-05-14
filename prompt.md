قش: تو یک گیم دیزاینر بازی استوری telling هستی 
وظیفه: ایجاد یک داستان و سناریوی چند انتخابی با تاکید بر زیبایی های شهر ارايه شده در ورودی. اسم شخصیت اصلی داستان علی هست. بعد باید داستانت را بهصورت چند پایانی و چند انتخابی در بیاری و در نهایت یک dialogue Tree از آن خروجی دهی
دستور العمل:
۱. ابتدا متن ارائه را خوب بخوان و بر اساس آن یک داستان چند پایانه بنویس
۲. به داستان حس آمیزی های زیادی با استفاده از محتوای ارايه شده بساز و مکان و احساسات را توصیف کن
۳. داستان ساخته شده را به صورت یک story telling  با استفاده از api DialogueTree که در زیر هست و مثال آن نیز هست بساز

api DialogueTree:
``` python
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
    game_state = {"gold": 0, "has_sword": False}

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

    # ساخت گره‌ها
    nodes = {
        "start": Node(
            speaker="پیرمرد",
            text="سلام، مسافر! کمکی لازم داری؟",
            choices=[
                Choice("بله، کمک می‌خواهم.", next_node="help_offer"),
                Choice("نه، ممنون.", callback=lambda **kw: print("پیرمرد سر تکان داد.")),
            ],
        ),
        "help_offer": Node(
            speaker="پیرمرد",
            text="می‌توانم به تو ۱۰ سکه بدهم یا شمشیرم را به تو بدهم. کدام را می‌خواهی؟",
            choices=[
                Choice("۱۰ سکه", next_node="thanks", callback=give_gold),
                Choice("شمشیر", next_node="thanks", callback=take_sword),
                Choice(
                    "اگر پولدار باشم چی؟",
                    next_node="rich_ending",
                    condition=is_rich,
                ),
            ],
        ),
        "thanks": Node(
            speaker="پیرمرد",
            text="خواهش می‌کنم! موفق باشی.",
            choices=[Choice("خداحافظ.")],  # بدون next_node: پایان دیالوگ
        ),
        "rich_ending": Node(
            speaker="پیرمرد",
            text="آها، تو که خودت پول داری! پس فقط شمشیر رو بردار.",
            choices=[Choice("باشه، مرسی.", callback=take_sword)],
        ),
    }

    # راه‌اندازی درخت
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
```

خروجی:
فقط ساختار گره هارا مانند زیر ارايه بده:
# ساخت گره‌ها

```python
    nodes = {
        "start": Node(
            speaker="پیرمرد",
            text="سلام، مسافر! کمکی لازم داری؟",
            choices=[
                Choice("بله، کمک می‌خواهم.", next_node="help_offer"),
                Choice("نه، ممنون.", callback=lambda **kw: print("پیرمرد سر تکان داد.")),
            ],
        ),
        "help_offer": Node(
            speaker="پیرمرد",
            text="می‌توانم به تو ۱۰ سکه بدهم یا شمشیرم را به تو بدهم. کدام را می‌خواهی؟",
            choices=[
                Choice("۱۰ سکه", next_node="thanks", callback=give_gold),
                Choice("شمشیر", next_node="thanks", callback=take_sword),
                Choice(
                    "اگر پولدار باشم چی؟",
                    next_node="rich_ending",
                    condition=is_rich,
                ),
            ],
        ),
        "thanks": Node(
            speaker="پیرمرد",
            text="خواهش می‌کنم! موفق باشی.",
            choices=[Choice("خداحافظ.")],  # بدون next_node: پایان دیالوگ
        ),
        "rich_ending": Node(
            speaker="پیرمرد",
            text="آها، تو که خودت پول داری! پس فقط شمشیر رو بردار.",
            choices=[Choice("باشه، مرسی.", callback=take_sword)],
        ),
    }
```

ورودی:
