import arcade
import math
import random
import time

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Игра с меню"
BUTTON_WIDTH = 325
BUTTON_HEIGHT = 60
BUTTON_SPACING = 15
SQUARE_SIZE = 400
DOT_RADIUS = 15
DOT_SPEED = 5

# Цвета
BACKGROUND_COLOR = arcade.color.BLACK
BUTTON_COLOR = (40, 40, 60)  # Темно-синий
BUTTON_HOVER_COLOR = (60, 60, 90)  # Светлее при наведении
BUTTON_TEXT_COLOR = arcade.color.WHITE
BUTTON_SHADOW_COLOR = (20, 20, 40)  # Цвет тени кнопки
DOT_COLOR = arcade.color.RED
DOT_OUTLINE_COLOR = arcade.color.DARK_RED
PAUSE_OVERLAY_COLOR = (0, 0, 0, 180)  # Полупрозрачный черный
SQUARE_COLOR = arcade.color.WHITE


class BeautifulButton:
    """Класс для создания красивых кнопок с эффектами"""

    def __init__(self, center_x, center_y, width, height, text, font_size=26):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.hover_animation = 0

    def draw(self):
        # Основной цвет кнопки с плавным переходом
        if self.is_hovered:
            self.hover_animation = min(1.0, self.hover_animation + 0.1)
        else:
            self.hover_animation = max(0.0, self.hover_animation - 0.1)

        # Смешивание цветов для плавного перехода
        mix_amount = self.hover_animation
        r = int(BUTTON_COLOR[0] * (1 - mix_amount) + BUTTON_HOVER_COLOR[0] * mix_amount)
        g = int(BUTTON_COLOR[1] * (1 - mix_amount) + BUTTON_HOVER_COLOR[1] * mix_amount)
        b = int(BUTTON_COLOR[2] * (1 - mix_amount) + BUTTON_HOVER_COLOR[2] * mix_amount)
        current_color = (r, g, b)

        # Рисуем основную кнопку
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, current_color)

        # Рисуем обводку
        border_color = (180, 180, 220, 100 + int(100 * self.hover_animation))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, border_color, 2)

        # Рисуем текст
        text_color = BUTTON_TEXT_COLOR
        if self.is_hovered:
            text_color = (255, 255, 200)  # Светло-желтый при наведении

        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            text_color,
            self.font_size,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

    def check_hover(self, x, y):
        """Проверяет, находится ли курсор над кнопкой"""
        self.is_hovered = (
                self.center_x - self.width / 2 < x < self.center_x + self.width / 2 and
                self.center_y - self.height / 2 < y < self.center_y + self.height / 2
        )
        return self.is_hovered

    def check_click(self, x, y):
        """Проверяет, была ли нажата кнопка"""
        return self.check_hover(x, y)


class MainMenuView(arcade.View):
    """Главное меню игры"""

    def __init__(self):
        super().__init__()
        self.buttons = []

    def setup(self):
        """Настройка главного меню"""
        # Создаем кнопки
        button_y = SCREEN_HEIGHT // 2 + BUTTON_HEIGHT

        # Кнопка "Играть"
        self.play_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ИГРАТЬ"
        )
        self.buttons.append(self.play_button)

        # Кнопка "Настройки"
        self.settings_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - (BUTTON_HEIGHT + BUTTON_SPACING),
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "НАСТРОЙКИ"
        )
        self.buttons.append(self.settings_button)

        # Кнопка "Выйти"
        self.exit_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - 2 * (BUTTON_HEIGHT + BUTTON_SPACING),
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ"
        )
        self.buttons.append(self.exit_button)

    def on_draw(self):
        """Отрисовка меню"""
        self.clear()

        # Черный фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Рисуем заголовок
        arcade.draw_text(
            "ГЛАВНОЕ МЕНЮ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

        # Подзаголовок
        arcade.draw_text(
            "Управляйте точкой стрелками, ESC - пауза",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 160,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

        # Рисуем кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Проверяем нажатие на кнопки
            if self.play_button.check_click(x, y):
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)

            elif self.settings_button.check_click(x, y):
                settings_view = SettingsView()
                settings_view.setup()
                self.window.show_view(settings_view)

            elif self.exit_button.check_click(x, y):
                arcade.exit()


class SettingsView(arcade.View):
    """Окно настроек"""

    def __init__(self):
        super().__init__()
        self.buttons = []

    def setup(self):
        """Настройка окна настроек"""
        # Кнопка "Назад"
        self.back_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "НАЗАД"
        )
        self.buttons.append(self.back_button)

    def on_draw(self):
        """Отрисовка окна настроек"""
        self.clear()

        # Черный фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Заголовок
        arcade.draw_text(
            "НАСТРОЙКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

        # Сообщение (пока настроек нет)
        arcade.draw_text(
            "сун",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.LIGHT_GRAY,
            32,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

        # Кнопка назад
        self.back_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.back_button.check_click(x, y):
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)


class GameView(arcade.View):
    """Игровое окно"""

    def __init__(self):
        super().__init__()
        self.dot_x = SCREEN_WIDTH // 2
        self.dot_y = SCREEN_HEIGHT // 2
        self.paused = False
        self.pause_buttons = []
        self.keys_pressed = set()
        self.start_time = None
        self.elapsed_time = 0
        self.game_active = True
        self.pause_start_time = None  # Дополнительная переменная для паузы

        # Границы белого квадрата
        self.square_left = SCREEN_WIDTH // 2 - SQUARE_SIZE // 2
        self.square_right = SCREEN_WIDTH // 2 + SQUARE_SIZE // 2
        self.square_bottom = SCREEN_HEIGHT // 2 - SQUARE_SIZE // 2
        self.square_top = SCREEN_HEIGHT // 2 + SQUARE_SIZE // 2

    def setup(self):
        """Настройка игры"""
        # Создаем кнопки для меню паузы
        button_y = SCREEN_HEIGHT // 2 - 25

        # Кнопка "Продолжить"
        self.resume_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y + BUTTON_HEIGHT // 2 + BUTTON_SPACING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ПРОДОЛЖИТЬ"
        )
        self.pause_buttons.append(self.resume_button)

        # Кнопка "Завершить игру"
        self.finish_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - BUTTON_HEIGHT // 2 - BUTTON_SPACING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ЗАВЕРШИТЬ ИГРУ"
        )
        self.pause_buttons.append(self.finish_button)

        # Сброс времени
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_active = True
        self.pause_start_time = None

    def on_draw(self):
        """Отрисовка игрового поля"""
        self.clear()

        # Черный фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Белый квадрат (незаполненный)
        left = SCREEN_WIDTH // 2 - SQUARE_SIZE // 2
        right = SCREEN_WIDTH // 2 + SQUARE_SIZE // 2
        bottom = SCREEN_HEIGHT // 2 - SQUARE_SIZE // 2
        top = SCREEN_HEIGHT // 2 + SQUARE_SIZE // 2
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, SQUARE_COLOR, 3)

        # Красный шарик
        arcade.draw_circle_filled(self.dot_x, self.dot_y, DOT_RADIUS, DOT_COLOR)
        arcade.draw_circle_outline(self.dot_x, self.dot_y, DOT_RADIUS, DOT_OUTLINE_COLOR, 2)

        # Таймер
        if self.start_time and self.game_active and not self.paused:
            self.elapsed_time = time.time() - self.start_time

        # Отображаем время
        time_text = f"Время: {self.elapsed_time:.1f} сек"
        arcade.draw_text(
            time_text,
            SCREEN_WIDTH - 150,
            SCREEN_HEIGHT - 30,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="left"
        )

        # Рисуем инструкцию
        arcade.draw_text(
            "ESC - пауза",
            10, SCREEN_HEIGHT - 30,
            arcade.color.LIGHT_GRAY,
            16
        )

        # Если игра на паузе, рисуем меню паузы
        if self.paused:
            # Полупрозрачный оверлей
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, PAUSE_OVERLAY_COLOR)

            # Заголовок паузы
            arcade.draw_text(
                "ПАУЗА",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 100,
                arcade.color.WHITE,
                48,
                anchor_x="center",
                anchor_y="center",
                font_name="Arial",
                bold=True
            )

            # Рисуем кнопки меню паузы
            for button in self.pause_buttons:
                button.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        if self.game_active and not self.paused:
            # Обновляем позицию точки в зависимости от зажатых клавиш
            if arcade.key.UP in self.keys_pressed:
                self.dot_y += DOT_SPEED
            if arcade.key.DOWN in self.keys_pressed:
                self.dot_y -= DOT_SPEED
            if arcade.key.LEFT in self.keys_pressed:
                self.dot_x -= DOT_SPEED
            if arcade.key.RIGHT in self.keys_pressed:
                self.dot_x += DOT_SPEED

            # Ограничение движения в пределах белого квадрата
            self.dot_x = max(self.square_left + DOT_RADIUS, min(self.square_right - DOT_RADIUS, self.dot_x))
            self.dot_y = max(self.square_bottom + DOT_RADIUS, min(self.square_top - DOT_RADIUS, self.dot_y))

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.ESCAPE:
            if not self.paused:
                # Начало паузы
                self.paused = True
                self.pause_start_time = time.time()
            else:
                # Конец паузы
                self.paused = False
                # Вычитаем время, проведенное в паузе
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                    self.pause_start_time = None

        # Добавляем клавиши в множество зажатых
        if key in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        # Убираем клавиши из множества зажатых
        if key in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.keys_pressed.discard(key)

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши в меню паузы"""
        if self.paused:
            for button in self.pause_buttons:
                button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши в меню паузы"""
        if self.paused and button == arcade.MOUSE_BUTTON_LEFT:
            if self.resume_button.check_click(x, y):
                # Конец паузы при нажатии кнопки "Продолжить"
                self.paused = False
                # Вычитаем время, проведенное в паузе
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                    self.pause_start_time = None
            elif self.finish_button.check_click(x, y):
                # Завершаем игру и показываем результаты
                self.game_active = False
                # Если была пауза, нужно учесть время паузы перед завершением
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                result_view = ResultView(self.elapsed_time)
                result_view.setup()
                self.window.show_view(result_view)


class ResultView(arcade.View):
    """Окно результатов игры"""

    def __init__(self, elapsed_time):
        super().__init__()
        self.elapsed_time = elapsed_time
        self.menu_button = None

    def setup(self):
        """Настройка окна результатов"""
        # Кнопка "Выйти в меню"
        self.menu_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ В МЕНЮ"
        )

    def on_draw(self):
        """Отрисовка окна результатов"""
        self.clear()

        # Черный фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Заголовок
        arcade.draw_text(
            "РЕЗУЛЬТАТ ПОПЫТКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

        # Надпись о времени
        arcade.draw_text(
            "Сессия длилась",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 30,
            arcade.color.LIGHT_GRAY,
            32,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )

        # Время
        arcade.draw_text(
            f"{self.elapsed_time:.1f} секунд",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 30,
            arcade.color.WHITE,
            40,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

        # Кнопка
        self.menu_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        if self.menu_button:
            self.menu_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.menu_button:
            if self.menu_button.check_click(x, y):
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)


def main():
    """Главная функция"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenuView()
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
