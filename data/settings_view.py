import arcade
import csv
import os
from pyglet.graphics import Batch
from data.beautiful_button import BeautifulButton
from data.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BACKGROUND_COLOR


SETTINGS_FILE = "settings.csv"


class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.batch = None
        self.title_text = None
        self.message_text = None

        # ===== НАСТРОЙКИ =====
        self.sounds_enabled = True
        self.brightness = 1.0

        # ===== ЭЛЕМЕНТЫ UI =====
        self.sounds_toggle_button = None
        self.brightness_slider = None
        self.brightness_text = None
        self.back_button = None

        # ===== ПОЛЗУНОК =====
        self.brightness_slider_x = 0
        self.brightness_slider_y = 0
        self.slider_width = 400
        self.slider_height = 10
        self.slider_handle_radius = 12
        self.brightness_slider_dragging = False

        # ===== РАССТОЯНИЕ МЕЖДУ КНОПКАМИ =====
        self.button_spacing = 40

    def setup(self):
        self.batch = Batch()

        # Загружаем настройки
        self.load_settings()

        # ===== ЗАГОЛОВОК =====
        self.title_text = arcade.Text(
            "НАСТРОЙКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True,
            batch=self.batch
        )

        # Центр экрана для вертикального расположения
        center_y = SCREEN_HEIGHT // 2

        # ===== КНОПКА ЗВУКОВ =====
        self.sounds_toggle_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            center_y + 70,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            f"ЗВУКИ: {'ВКЛ' if self.sounds_enabled else 'ВЫКЛ'}"
        )
        self.sounds_toggle_button.create_text_object(self.batch)
        self.buttons.append(self.sounds_toggle_button)

        # ===== ПОЛЗУНОК ЯРКОСТИ =====
        self.brightness_slider_x = SCREEN_WIDTH // 2
        self.brightness_slider_y = center_y - 30

        self.brightness_text = arcade.Text(
            f"ЯРКОСТЬ: {int(self.brightness * 100)}%",
            SCREEN_WIDTH // 2,
            self.brightness_slider_y - 40,
            arcade.color.LIGHT_GRAY,
            20,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

        # ===== КНОПКА НАЗАД =====
        self.back_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "НАЗАД"
        )
        self.back_button.create_text_object(self.batch)
        self.buttons.append(self.back_button)

        # Применяем настройки
        self.apply_all_settings()

    def load_settings(self):
        """Загрузить настройки из CSV файла (только яркость и звуки)"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if rows and len(rows[0]) >= 2:
                        # Новый формат: яркость, звуки
                        self.brightness = float(rows[0][0])
                        self.sounds_enabled = rows[0][1].lower() == 'true'
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
        else:
            # Если файла нет, создаём с параметрами по умолчанию
            self.save_settings()

        self.window.brightness = self.brightness
        self.window.sounds_enabled = self.sounds_enabled

    def save_settings(self):
        """Сохранить настройки в CSV файл (только 2 параметра)"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    self.brightness,      # яркость
                    self.sounds_enabled   # звуки
                ])
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

        self.window.brightness = self.brightness
        self.window.sounds_enabled = self.sounds_enabled

    def apply_all_settings(self):
        """Применить все настройки"""
        # Музыка не трогаем — она всегда играет
        self.window.darkness_factor = 1.0 - self.brightness

    def update_sounds_button_text(self):
        status = "ВКЛ" if self.sounds_enabled else "ВЫКЛ"
        self.sounds_toggle_button.text = f"ЗВУКИ: {status}"
        self.sounds_toggle_button.create_text_object(self.batch)

    def on_draw(self):
        self.clear()

        # Фон с учётом яркости
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # ===== ПОЛЗУНОК ЯРКОСТИ =====
        # Серый фон
        arcade.draw_lrbt_rectangle_filled(
            self.brightness_slider_x - self.slider_width // 2,
            self.brightness_slider_x + self.slider_width // 2,
            self.brightness_slider_y - self.slider_height // 2,
            self.brightness_slider_y + self.slider_height // 2,
            arcade.color.DARK_GRAY
        )

        # Заливка
        fill_width = self.slider_width * self.brightness
        arcade.draw_lrbt_rectangle_filled(
            self.brightness_slider_x - self.slider_width // 2,
            self.brightness_slider_x - self.slider_width // 2 + fill_width,
            self.brightness_slider_y - self.slider_height // 2,
            self.brightness_slider_y + self.slider_height // 2,
            arcade.color.LIGHT_BLUE
        )

        # Ручка
        handle_x = self.brightness_slider_x - self.slider_width // 2 + fill_width
        arcade.draw_circle_filled(handle_x, self.brightness_slider_y, self.slider_handle_radius, arcade.color.WHITE)
        arcade.draw_circle_outline(handle_x, self.brightness_slider_y, self.slider_handle_radius, arcade.color.BLACK, 2)

        # Кнопки и текст
        for button in self.buttons:
            button.draw()
        self.batch.draw()

        # ===== ЧЁРНЫЙ СЛОЙ ДЛЯ ЯРКОСТИ =====
        darkness = getattr(self.window, 'darkness_factor', 0)
        if darkness > 0:
            alpha = int(255 * darkness)
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH,
                0, SCREEN_HEIGHT,
                (0, 0, 0, alpha)
            )

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # ===== КНОПКА ЗВУКОВ =====
            if self.sounds_toggle_button.check_click(x, y):
                self.sounds_enabled = not self.sounds_enabled
                self.update_sounds_button_text()
                self.save_settings()
                return

            # ===== КНОПКА НАЗАД =====
            if self.back_button.check_click(x, y):
                from data.main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)
                return

            # ===== ПОЛЗУНОК ЯРКОСТИ =====
            handle_x = self.brightness_slider_x - self.slider_width // 2 + self.slider_width * self.brightness
            if (x >= handle_x - self.slider_handle_radius * 2 and x <= handle_x + self.slider_handle_radius * 2 and
                y >= self.brightness_slider_y - self.slider_handle_radius * 2 and
                y <= self.brightness_slider_y + self.slider_handle_radius * 2):
                self.brightness_slider_dragging = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.brightness_slider_dragging:
            min_x = self.brightness_slider_x - self.slider_width // 2
            max_x = self.brightness_slider_x + self.slider_width // 2
            x = max(min_x, min(max_x, x))

            self.brightness = (x - min_x) / self.slider_width
            self.brightness = max(0.25, min(1.0, self.brightness))

            self.brightness_text.text = f"ЯРКОСТЬ: {int(self.brightness * 100)}%"
            self.apply_all_settings()
            self.save_settings()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.brightness_slider_dragging = False
