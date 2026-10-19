import os
import io
import webbrowser
import random
from kivy.config import Config

os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"
Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from PIL import Image as PILImage, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# تنظیمات اختصاصی و داده‌های کوییز
# ==========================================
RUBIKA_URL = "https://rubika.ir/esteghlalmusic1"
SUPPORT_URL = "https://rubika.ir/username"
FAV_FILE = "fav.txt"
QUIZ_FILE = "quiz_done.txt"

QUIZ_DATA = [
    {"q": "استقلال در چه سالی تاسیس شد؟", "options": ["۱۳۲۴", "۱۳۳۰", "۱۳۴۵", "۱۳۲۱"], "a": 0},
    {"q": "کدام بازیکن بیشترین گل را برای استقلال زده؟", "options": ["فرهاد مجیدی", "آرش برهانی", "غلامحسین مظلومی", "حسن روشن"], "a": 1},
    {"q": "اولین قهرمانی استقلال در آسیا در چه سالی بود؟", "options": ["۱۹۷۰", "۱۹۹۰", "۱۹۸۵", "۱۹۹۵"], "a": 0},
    {"q": "لقب تیم استقلال چیست؟", "options": ["قرمزها", "آبی‌ها", "طلایی‌ها", "سیاه و سفید"], "a": 1},
    {"q": "سرمربی اولین قهرمانی آسیا چه کسی بود؟", "options": ["منصور پورحیدری", "زدراکو رایکوف", "ناصر حجازی", "امیر قلعه‌نویی"], "a": 1},
    {"q": "دربی استقلال و پرسپولیس معروف به چیست؟", "options": ["ال‌کلاسیکو", "دربی پایتخت", "شهرآورد تهران", "نبرد سرخابی"], "a": 1},
    {"q": "کدام بازیکن شماره ۷ استقلال را می‌پوشید؟", "options": ["فرهاد مجیدی", "مجتبی جباری", "آرش برهانی", "سیاوش اکبرپور"], "a": 0},
    {"q": "استقلال چند بار قهرمان لیگ ایران شده؟", "options": ["۷", "۸", "۹", "۱۰"], "a": 2},
    {"q": "مکان تمرین اصلی استقلال کجاست؟", "options": ["مرغوبکار", "کمپ ناصر حجازی", "درفشی‌فر", "ورزشگاه آزادی"], "a": 1},
    {"q": "رنگ اول لباس استقلال چیست؟", "options": ["قرمز", "سفید", "آبی", "زرد"], "a": 2},
    {"q": "ناصر حجازی چه پستی در استقلال داشت؟", "options": ["مهاجم", "دروازه‌بان", "هافبک", "مدافع"], "a": 1},
    {"q": "کاپیتان پرافتخار استقلال چه کسی است؟", "options": ["فرهاد مجیدی", "امیر قلعه‌نویی", "سید مهدی رحمتی", "محمود فکری"], "a": 3},
    {"q": "تعداد ستاره‌های روی لوگوی استقلال؟", "options": ["۱", "۲", "۳", "۴"], "a": 1},
    {"q": "استقلال در ورزشگاه ... بازی می‌کند.", "options": ["آزادی", "تختی", "شیرودی", "شهید وطنی"], "a": 0},
    {"q": "لقب منصور پورحیدری چیست؟", "options": ["پدر استقلال", "اسطوره", "خان", "عقاب"], "a": 0}
]

HISTORY_TEXT = """تاریخچه باشگاه استقلال

باشگاه فرهنگی ورزشی استقلال ایران 
در سال ۱۳۲۴ تاسیس شد. 
این تیم با افتخاراتی همچون:
- ۲ قهرمانی در آسیا
- ۹ قهرمانی در لیگ ایران
پر افتخارترین تیم ایران است."""

HELP_TEXT = """به برنامه آهنگ‌های هواداری استقلال خوش آمدید!

راهنمای استفاده:
۱. برای پخش هر آهنگ، روی دکمه آبی رنگ پخش بزنید.
۲. با زدن قلب، آهنگ به لیست علاقه‌مندی‌ها می‌رود.
۳. می‌توانید از نوار جستجو در بالا، آهنگ‌ها را پیدا کنید.
۴. دکمه 🔀 آهنگ تصادفی پخش می‌کند."""

def load_favorites():
    if not os.path.exists(FAV_FILE): return []
    with open(FAV_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def toggle_favorite(name):
    favs = load_favorites()
    if name in favs: favs.remove(name)
    else: favs.append(name)
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(favs))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")
BG_IMAGE = os.path.join(BASE_DIR, "bg.jpg")
FONT_PATH = r"C:\Windows\Fonts\arial.ttf" if os.path.exists(r"C:\Windows\Fonts\arial.ttf") else None

def make_persian_texture(text, font_size=20, text_color=(255, 255, 255, 255)):
    int_color = tuple(int(c) for c in text_color)
    lines = text.split("\n")
    reshaped_lines = [get_display(arabic_reshaper.reshape(line)) for line in lines]
    bidi_text = "\n".join(reshaped_lines)
    
    try:
        font = ImageFont.truetype(FONT_PATH, font_size) if FONT_PATH else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    dummy = PILImage.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)
    bbox = d.multiline_textbbox((0, 0), bidi_text, font=font, spacing=8)
    w, h = max(20, bbox[2] - bbox[0] + 20), max(20, bbox[3] - bbox[1] + 20)
    img = PILImage.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.multiline_text((10 - bbox[0], 10 - bbox[1]), bidi_text, font=font, fill=int_color, align="center", spacing=8)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return CoreImage(buf, ext="png").texture

class PersianButton(Button):
    def __init__(self, persian_text="", font_size=16, text_color=(255, 255, 255, 255), **kwargs):
        super().__init__(**kwargs)
        self.persian_text = persian_text
        self.font_size_custom = font_size
        self.text_color_custom = text_color
        self.img_lbl = KivyImage()
        self.add_widget(self.img_lbl)
        self.bind(pos=self._update_img, size=self._update_img)
        self.update_label()

    def update_label(self):
        if self.persian_text:
            self.img_lbl.texture = make_persian_texture(self.persian_text, self.font_size_custom, self.text_color_custom)

    def _update_img(self, *args):
        self.img_lbl.pos = self.pos
        self.img_lbl.size = self.size

class ModernSongCard(BoxLayout):
    def __init__(self, song_name, play_callback, is_fav, fav_callback, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.6) 
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        self.play_btn = Button(text="▶", size_hint_x=None, width=dp(40), background_normal='', background_color=(0, 0.7, 1, 1))
        self.play_btn.bind(on_release=lambda *_: play_callback(song_name))
        self.add_widget(self.play_btn)
        
        self.title_lbl = KivyImage(size_hint_x=0.6)
        self.title_lbl.texture = make_persian_texture(song_name, font_size=16)
        self.add_widget(self.title_lbl)
        
        self.fav_btn = Button(text="♥" if is_fav else "♡", size_hint_x=None, width=dp(40), background_normal='', background_color=(0.8, 0, 0, 0.8))
        self.fav_btn.bind(on_release=lambda *_: fav_callback(song_name))
        self.add_widget(self.fav_btn)

    def update_canvas(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class MainScreen(Screen): pass
class SettingsScreen(Screen): pass
class HelpScreen(Screen): pass
class HistoryScreen(Screen): pass
class FavoritesScreen(Screen): pass

# ==========================================
# صفحه کوییز با نمایش امتیاز لحظه‌ای
# ==========================================
class QuizScreen(Screen):
    def on_enter(self):
        if os.path.exists(QUIZ_FILE):
            self.show_already_done()
            return
        self.score = 0
        self.idx = 0
        self.show_question()

    def show_already_done(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15))
        with layout.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *_: setattr(self.bg_rect, 'pos', layout.pos), size=lambda *_: setattr(self.bg_rect, 'size', layout.size))
        
        layout.add_widget(KivyImage(texture=make_persian_texture("شما قبلاً در کوییز شرکت کرده‌اید!\nهر کاربر فقط یک بار می‌تواند شرکت کند.", font_size=18)))
        
        back_btn = PersianButton(persian_text="بازگشت به تنظیمات", size_hint_y=None, height=dp(50), background_normal='', background_color=(0, 0.55, 0.9, 1))
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'settings'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def show_question(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        with layout.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *_: setattr(self.bg_rect, 'pos', layout.pos), size=lambda *_: setattr(self.bg_rect, 'size', layout.size))
        
        # هدر نمایش امتیاز (بالا سمت چپ)
        header_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        score_tex = make_persian_texture(f"امتیاز: {self.score}", font_size=16, text_color=(255, 255, 0, 255))
        header_box.add_widget(KivyImage(texture=score_tex, size_hint_x=0.4))
        header_box.add_widget(BoxLayout()) # فضای خالی
        layout.add_widget(header_box)
        
        q_data = QUIZ_DATA[self.idx]
        layout.add_widget(KivyImage(size_hint_y=0.25, texture=make_persian_texture(f"سوال {self.idx+1} از {len(QUIZ_DATA)}\n\n{q_data['q']}", font_size=18, text_color=(0, 204, 255, 255))))
        
        self.option_buttons = []
        for i, opt in enumerate(q_data["options"]):
            btn = PersianButton(persian_text=opt, font_size=16, size_hint_y=None, height=dp(50), background_normal='', background_color=(0.2, 0.2, 0.2, 1))
            btn.bind(on_release=lambda *_, choice=i, b=btn: self.check_answer(choice, b))
            self.option_buttons.append((i, btn))
            layout.add_widget(btn)
            
        self.feedback_lbl = KivyImage(size_hint_y=0.15, texture=make_persian_texture("", font_size=16))
        layout.add_widget(self.feedback_lbl)
        self.add_widget(layout)

    def check_answer(self, choice, clicked_btn):
        correct = QUIZ_DATA[self.idx]['a']
        for i, btn in self.option_buttons:
            btn.unbind(on_release=btn.setter('on_release'))
            if i == correct: btn.background_color = (0, 0.7, 0.3, 1)
            elif i == choice and choice != correct: btn.background_color = (0.9, 0.1, 0.1, 1)

        if choice == correct:
            self.score += 10
            msg = random.choice(["آفرین! درست بود.", "عالی بود! ادامه بده.", "درسته! کاملاً حرفه‌ای بودی."])
            self.feedback_lbl.texture = make_persian_texture(msg, font_size=16, text_color=(0, 255, 100, 255))
        else:
            msg = random.choice(["اشتباه کردی! باختی.", "ای بابا، این یکی رو اشتباه زدی!", "متاسفم، جواب درست سبز شد."])
            self.feedback_lbl.texture = make_persian_texture(msg, font_size=16, text_color=(255, 50, 50, 255))

        self.idx += 1
        if self.idx < len(QUIZ_DATA):
            Clock.schedule_once(lambda dt: self.show_question(), 1.8)
        else:
            with open(QUIZ_FILE, "w", encoding="utf-8") as f: f.write(str(self.score))
            Clock.schedule_once(lambda dt: self.show_result(), 1.8)

    def show_result(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(20))
        with layout.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *_: setattr(self.bg_rect, 'pos', layout.pos), size=lambda *_: setattr(self.bg_rect, 'size', layout.size))
        
        layout.add_widget(KivyImage(texture=make_persian_texture(f"کوییز تمام شد!\n\nامتیاز نهایی: {self.score}", font_size=22, text_color=(0, 204, 255, 255))))
        back_btn = PersianButton(persian_text="بازگشت به خانه", size_hint_y=None, height=dp(50), background_normal='', background_color=(0, 0.55, 0.9, 1))
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class EsteghlalApp(App):
    def build(self):
        self.current_sound = None
        self.sm = ScreenManager()
        self.all_songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav'))] if os.path.exists(MUSIC_DIR) else []
        
        self.main_screen = MainScreen(name="main")
        self.main_layout = BoxLayout(orientation="vertical")
        with self.main_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source=BG_IMAGE if os.path.exists(BG_IMAGE) else "", pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(140), padding=dp(10), spacing=dp(5))
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        top_bar.add_widget(KivyImage(texture=make_persian_texture("استقلال | MUSIC", font_size=24, text_color=(0, 204, 255, 255))))
        settings_btn = Button(text="⚙", font_size=dp(22), size_hint=(None, None), size=(dp(40), dp(40)), background_normal='', background_color=(0, 0.7, 1, 0.9))
        settings_btn.bind(on_release=lambda *_: self.open_settings())
        top_bar.add_widget(settings_btn)
        header.add_widget(top_bar)
        self.search_bar = TextInput(hint_text="جستجوی آهنگ...", multiline=False, size_hint_y=None, height=dp(40))
        self.search_bar.bind(text=self.filter_songs)
        header.add_widget(self.search_bar)
        self.main_layout.add_widget(header)
        
        self.scroll = ScrollView()
        self.songs_box = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.songs_box.bind(minimum_height=self.songs_box.setter('height'))
        self.render_songs(self.all_songs)
        self.scroll.add_widget(self.songs_box)
        self.main_layout.add_widget(self.scroll)
        
        self.player_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(70), padding=[dp(10), dp(5)])
        with self.player_bar.canvas.before:
            Color(0.1, 0.1, 0.1, 0.92)
            self.p_rect = RoundedRectangle(pos=self.player_bar.pos, size=self.player_bar.size, radius=[dp(15), dp(15), 0, 0])
        self.player_bar.bind(pos=self.update_player_bg, size=self.update_player_bg)
        
        self.now_playing_lbl = KivyImage(size_hint_x=0.6)
        self.now_playing_lbl.texture = make_persian_texture("آماده پخش...", font_size=14)
        self.player_bar.add_widget(self.now_playing_lbl)
        
        shuffle_btn = Button(text="🔀", size_hint_x=None, width=dp(50), background_color=(0, 0.7, 0.3, 1))
        shuffle_btn.bind(on_release=self.shuffle_music)
        self.player_bar.add_widget(shuffle_btn)
        
        self.stop_btn = Button(text="⏹", size_hint_x=None, width=dp(50), background_color=(1, 0.2, 0.2, 1))
        self.stop_btn.bind(on_release=self.stop_music)
        self.player_bar.add_widget(self.stop_btn)
        self.main_layout.add_widget(self.player_bar)
        self.main_screen.add_widget(self.main_layout)
        
        self.settings_screen = SettingsScreen(name="settings")
        self.settings_layout = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(10))
        with self.settings_layout.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.settings_bg = Rectangle(pos=self.settings_layout.pos, size=self.settings_layout.size)
        self.settings_layout.bind(pos=self.update_settings_bg, size=self.update_settings_bg)
        self.settings_layout.add_widget(KivyImage(size_hint_y=None, height=dp(60), texture=make_persian_texture("تنظیمات", font_size=24, text_color=(0, 204, 255, 255))))
        
        btns = [
            ("صفحه اصلی", self.go_home), 
            ("کوییز هواداری استقلال ⭐", lambda: setattr(self.sm, 'current', 'quiz')),
            ("آهنگ‌های مورد علاقه", self.open_favorites), 
            ("تاریخچه باشگاه", lambda: setattr(self.sm, 'current', 'history')), 
            ("کانال روبیکا", self.open_rubika), 
            ("پشتیبانی", self.open_support), 
            ("راهنما", self.open_help)
        ]
        for text, func in btns:
            b = PersianButton(persian_text=text, font_size=17, size_hint_y=None, height=dp(45), background_normal='', background_color=(0, 0.55, 0.9, 1))
            b.bind(on_release=lambda *_, f=func: f())
            self.settings_layout.add_widget(b)
            
        self.settings_layout.add_widget(KivyImage(size_hint_y=None, height=dp(50), texture=make_persian_texture("ساخته شده توسط رضا عدالت محب", font_size=14, text_color=(200, 200, 200, 255))))
        self.settings_screen.add_widget(self.settings_layout)
        
        self.history_screen = HistoryScreen(name="history")
        self.history_layout = BoxLayout(orientation="vertical", padding=dp(25))
        self.history_layout.add_widget(KivyImage(size_hint_y=None, height=dp(60), texture=make_persian_texture("تاریخچه باشگاه", font_size=24)))
        self.history_layout.add_widget(KivyImage(texture=make_persian_texture(HISTORY_TEXT, font_size=16)))
        back_hist = PersianButton(persian_text="بازگشت", size_hint_y=None, height=dp(50), background_color=(0.5, 0.5, 0.5, 1))
        back_hist.bind(on_release=lambda *_: self.open_settings())
        self.history_layout.add_widget(back_hist)
        self.history_screen.add_widget(self.history_layout)
        
        self.favs_screen = FavoritesScreen(name="favorites")
        self.favs_layout = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(10))
        self.favs_layout.add_widget(KivyImage(size_hint_y=None, height=dp(60), texture=make_persian_texture("علاقه‌مندی‌ها", font_size=24)))
        self.favs_box = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.favs_box.bind(minimum_height=self.favs_box.setter('height'))
        fav_scroll = ScrollView()
        fav_scroll.add_widget(self.favs_box)
        self.favs_layout.add_widget(fav_scroll)
        back_fav = PersianButton(persian_text="بازگشت", size_hint_y=None, height=dp(50), background_color=(0.5, 0.5, 0.5, 1))
        back_fav.bind(on_release=lambda *_: self.open_settings())
        self.favs_layout.add_widget(back_fav)
        self.favs_screen.add_widget(self.favs_layout)
        
        self.help_screen = HelpScreen(name="help")
        self.help_layout = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15))
        with self.help_layout.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.help_bg = Rectangle(pos=self.help_layout.pos, size=self.help_layout.size)
        self.help_layout.bind(pos=self.update_help_bg, size=self.update_help_bg)
        self.help_layout.add_widget(KivyImage(size_hint_y=None, height=dp(60), texture=make_persian_texture("راهنما", font_size=24)))
        help_lbl = KivyImage(texture=make_persian_texture(HELP_TEXT, font_size=16))
        self.help_layout.add_widget(help_lbl)
        back_help = PersianButton(persian_text="بازگشت", size_hint_y=None, height=dp(50), background_color=(0.5, 0.5, 0.5, 1))
        back_help.bind(on_release=lambda *_: self.go_home())
        self.help_layout.add_widget(back_help)
        self.help_screen.add_widget(self.help_layout)
        
        self.quiz_screen = QuizScreen(name="quiz")
        
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.settings_screen)
        self.sm.add_widget(self.history_screen)
        self.sm.add_widget(self.favs_screen)
        self.sm.add_widget(self.help_screen)
        self.sm.add_widget(self.quiz_screen)
        
        return self.sm

    def filter_songs(self, instance, value):
        filtered = [s for s in self.all_songs if value.lower() in s.lower()]
        self.render_songs(filtered)

    def render_songs(self, songs_list):
        self.songs_box.clear_widgets()
        favs = load_favorites()
        for s in songs_list:
            song_name = os.path.splitext(s)[0]
            is_fav = song_name in favs
            self.songs_box.add_widget(ModernSongCard(song_name, self.play_song, is_fav, self.toggle_fav))
        self.songs_box.add_widget(KivyImage(size_hint_y=None, height=dp(50), texture=make_persian_texture("ساخته شده توسط رضا عدالت محب", font_size=14, text_color=(200, 200, 200, 255))))

    def toggle_fav(self, name):
        toggle_favorite(name)
        self.filter_songs(None, self.search_bar.text)
        self.render_favs()

    def render_favs(self):
        self.favs_box.clear_widgets()
        favs = load_favorites()
        for s in favs:
            self.favs_box.add_widget(ModernSongCard(s, self.play_song, True, self.toggle_fav))

    def open_favorites(self):
        self.render_favs()
        self.sm.current = "favorites"

    def shuffle_music(self, *args):
        if self.all_songs:
            self.play_song(os.path.splitext(random.choice(self.all_songs))[0])

    def update_bg(self, *args):
        self.bg_rect.pos = self.main_layout.pos
        self.bg_rect.size = self.main_layout.size

    def update_player_bg(self, *args):
        self.p_rect.pos = self.player_bar.pos
        self.p_rect.size = self.player_bar.size

    def update_settings_bg(self, *args):
        self.settings_bg.pos = self.settings_layout.pos
        self.settings_bg.size = self.settings_layout.size

    def update_help_bg(self, *args):
        self.help_bg.pos = self.help_layout.pos
        self.help_bg.size = self.help_layout.size

    def open_settings(self): self.sm.current = "settings"
    def go_home(self): self.sm.current = "main"
    def open_help(self): self.sm.current = "help"
    def open_rubika(self): webbrowser.open(RUBIKA_URL)
    def open_support(self): webbrowser.open(SUPPORT_URL)

    def play_song(self, name):
        path = os.path.join(MUSIC_DIR, name + ".mp3")
        if not os.path.exists(path): path = os.path.join(MUSIC_DIR, name + ".wav")
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound.unload()
        self.current_sound = SoundLoader.load(path)
        if self.current_sound:
            self.current_sound.play()
            self.now_playing_lbl.texture = make_persian_texture(f"در حال پخش: {name[:12]}...", font_size=14)

    def stop_music(self, *args):
        if self.current_sound:
            self.current_sound.stop()
            self.now_playing_lbl.texture = make_persian_texture("متوقف شد", font_size=14)

if __name__ == "__main__":
    EsteghlalApp().run()
