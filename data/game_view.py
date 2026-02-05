import arcade
import math
import random
import time
import os
from collections import namedtuple
from pyglet.graphics import Batch
from .beautiful_button import BeautifulButton
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT,
    BUTTON_SPACING, BACKGROUND_COLOR, SQUARE_COLOR,
    PAUSE_OVERLAY_COLOR
)

# Определяем тип Rect для draw_texture_rect
Rect = namedtuple('Rect', ['x', 'y', 'width', 'height'])


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.game_active = True
        self.game_time = 30.0  # 30 секунд игры
        self.start_time = None
        self.paused = False
        self.pause_start_time = None
        self.victory = False

        # Здоровье игрока
        self.player_hp = 92
        self.max_hp = 92
        self.last_damage_time = 0
        self.damage_interval = 0.05  # УМЕНЬШИЛИ до 50 мс (было 300 мс)

        # Размеры арены (прямоугольник)
        self.arena_width = 600  # Ширина арены
        self.arena_height = 250  # Высота арены
        self.arena_left = SCREEN_WIDTH // 2 - self.arena_width // 2
        self.arena_right = SCREEN_WIDTH // 2 + self.arena_width // 2
        self.arena_bottom = SCREEN_HEIGHT // 2 - self.arena_height // 2
        self.arena_top = SCREEN_HEIGHT // 2 + self.arena_height // 2

        # Позиция сердца (игрока) - загружаем текстуру
        self.heart_x = SCREEN_WIDTH // 2
        self.heart_y = SCREEN_HEIGHT // 2
        self.heart_size = 15  # УМЕНЬШИЛИ размер сердца (было 30)
        self.heart_speed = 200  # Скорость движения (меньше)
        self.heart_texture = None

        # Система пуль
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_spawn_rate = 0.3  # секунды между пулями
        self.bullets_dodged = 0
        self.total_bullets = 0
        self.bullet_radius = 35  # УВЕЛИЧИЛИ размер пуль (было 25)

        # Управление
        self.keys_pressed = set()

        # Интерфейс
        self.batch = None
        self.timer_text = None
        self.instruction_text = None
        self.pause_title_text = None
        self.pause_batch = None
        self.pause_buttons = []

        # Статистика
        self.stats_text = None
        self.hp_text = None

    def setup(self):
        # Загрузка текстуры сердца
        try:
            # Пытаемся найти файл heart.png в разных местах
            possible_paths = [
                "materials/heart.png",
                "../materials/heart.png",
                os.path.join(os.path.dirname(__file__), "../materials/heart.png")
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.heart_texture = arcade.load_texture(path)
                    print(f"Текстура сердца загружена из: {path}")
                    break

            if self.heart_texture is None:
                print("Файл heart.png не найден. Используется запасной вариант.")

        except Exception as e:
            print(f"Ошибка при загрузке текстуры: {e}")
            self.heart_texture = None

        self.batch = Batch()

        # Текст таймера
        self.timer_text = arcade.Text(
            f"Время: 30.0 сек",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            arcade.color.WHITE,
            32,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Текст инструкции
        self.instruction_text = arcade.Text(
            "Уклоняйтесь от пуль! ESC - пауза",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Статистика
        self.stats_text = arcade.Text(
            f"Уклонений: 0",
            20,
            80,
            arcade.color.LIGHT_GREEN,
            20,
            batch=self.batch
        )

        # Текст HP
        self.hp_text = arcade.Text(
            f"HP: {self.player_hp}/{self.max_hp}",
            20,
            50,
            arcade.color.WHITE,
            20,
            batch=self.batch
        )

        # Текст паузы
        self.pause_title_text = arcade.Text(
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

        # Кнопки паузы
        button_y = SCREEN_HEIGHT // 2 - 25
        self.pause_batch = Batch()

        self.resume_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y + BUTTON_HEIGHT // 2 + BUTTON_SPACING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ПРОДОЛЖИТЬ"
        )
        self.resume_button.create_text_object(self.pause_batch)
        self.pause_buttons.append(self.resume_button)

        self.menu_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - BUTTON_HEIGHT // 2 - BUTTON_SPACING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ В МЕНЮ"
        )
        self.menu_button.create_text_object(self.pause_batch)
        self.pause_buttons.append(self.menu_button)

        # Сброс состояния
        self.reset_game()

    def reset_game(self):
        """Сброс игры в начальное состояние"""
        self.heart_x = SCREEN_WIDTH // 2
        self.heart_y = SCREEN_HEIGHT // 2
        self.bullets = []
        self.bullet_timer = 0
        self.bullets_dodged = 0
        self.total_bullets = 0
        self.player_hp = self.max_hp
        self.last_damage_time = 0
        self.start_time = time.time()
        self.game_active = True
        self.victory = False
        self.keys_pressed.clear()
        self.timer_text.text = f"Время: 30.0 сек"
        self.stats_text.text = f"Уклонений: 0"
        self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

    def on_draw(self):
        self.clear()

        # Фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Арена (прямоугольник)
        arcade.draw_lrbt_rectangle_outline(
            self.arena_left, self.arena_right,
            self.arena_bottom, self.arena_top,
            SQUARE_COLOR, 3
        )

        # Пули (увеличенные)
        for bullet in self.bullets:
            arcade.draw_circle_filled(bullet["x"], bullet["y"], self.bullet_radius, arcade.color.YELLOW)
            arcade.draw_circle_outline(bullet["x"], bullet["y"], self.bullet_radius, arcade.color.ORANGE, 3)

        # Сердце (игрок) - ПРАВИЛЬНОЕ использование draw_texture_rect
        # ИСПРАВЛЕНО: текстура съезжала вниз и влево
        if self.heart_texture:
            # Визуальный размер сердца (может отличаться от hitbox)
            # Увеличиваем визуальный размер для лучшего отображения
            visual_width = self.heart_size * 1.8 # Больше hitbox для визуала
            visual_height = self.heart_size * 1.8

            # ИСПРАВЛЕНИЕ: текстура съезжала вниз и влево
            # Центрируем текстуру относительно hitbox
            # Если текстура съезжает вниз, нужно поднять Y
            # Если текстура съезжает влево, нужно сдвинуть X вправо
            x = self.heart_x - visual_width / 2 + self.heart_size * 0.3  # Сдвиг вправо
            y = self.heart_y - visual_height / 2 + self.heart_size * 0.5  # Сдвиг вверх

            # Создаем объект Rect для draw_texture_rect
            rect = Rect(x=x, y=y, width=visual_width, height=visual_height)

            # Рисуем текстуру
            arcade.draw_texture_rect(self.heart_texture, rect)

            # Отладочная отрисовка hitbox (красный круг) - можно включить для тестирования
            # arcade.draw_circle_outline(self.heart_x, self.heart_y, self.heart_size, arcade.color.RED, 2)
            # arcade.draw_circle_filled(self.heart_x, self.heart_y, 3, arcade.color.BLUE)  # Центр

        # Полоса HP под ареной
        hp_bar_y = self.arena_bottom - 40
        hp_bar_width = 400
        hp_bar_height = 20
        hp_bar_x = SCREEN_WIDTH // 2 - hp_bar_width // 2

        # Фон полосы HP
        arcade.draw_lrbt_rectangle_filled(
            hp_bar_x, hp_bar_x + hp_bar_width,
            hp_bar_y, hp_bar_y + hp_bar_height,
            (60, 60, 60)
        )

        # Заливка HP
        hp_percentage = self.player_hp / self.max_hp
        hp_fill_width = hp_bar_width * hp_percentage

        # Цвет полосы HP (меняется от зеленого к красному)
        if hp_percentage > 0.6:
            hp_color = arcade.color.GREEN
        elif hp_percentage > 0.3:
            hp_color = arcade.color.YELLOW
        else:
            hp_color = arcade.color.RED

        arcade.draw_lrbt_rectangle_filled(
            hp_bar_x, hp_bar_x + hp_fill_width,
            hp_bar_y, hp_bar_y + hp_bar_height,
            hp_color
        )

        # Контур полосы HP
        arcade.draw_lrbt_rectangle_outline(
            hp_bar_x, hp_bar_x + hp_bar_width,
            hp_bar_y, hp_bar_y + hp_bar_height,
            arcade.color.WHITE, 2
        )

        # Прогресс-бар времени
        if self.start_time and self.game_active and not self.paused:
            elapsed = time.time() - self.start_time
            time_left = max(0, 30.0 - elapsed)
            progress = time_left / 30.0

            time_bar_width = 300
            time_bar_x = SCREEN_WIDTH // 2 - time_bar_width // 2
            time_bar_y = SCREEN_HEIGHT - 30
            time_bar_height = 10

            bar_fill_width = time_bar_width * progress
            bar_color = arcade.color.GREEN if progress > 0.3 else arcade.color.RED

            arcade.draw_lrbt_rectangle_filled(
                time_bar_x, time_bar_x + bar_fill_width,
                time_bar_y, time_bar_y + time_bar_height,
                bar_color
            )
            arcade.draw_lrbt_rectangle_outline(
                time_bar_x, time_bar_x + time_bar_width,
                time_bar_y, time_bar_y + time_bar_height,
                arcade.color.WHITE, 2
            )

        # Текст
        self.batch.draw()

        # Пауза
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, PAUSE_OVERLAY_COLOR)
            self.pause_title_text.draw()
            for button in self.pause_buttons:
                button.draw()
            self.pause_batch.draw()

    def on_update(self, delta_time):
        if not self.game_active or self.paused:
            return

        current_time = time.time()

        # Обновление таймера
        if self.start_time:
            elapsed = current_time - self.start_time
            time_left = max(0, 30.0 - elapsed)
            self.timer_text.text = f"Время: {time_left:.1f} сек"

            # Проверка окончания игры по времени
            if time_left <= 0:
                self.victory = True
                self.game_active = False
                self.end_game()
                return

        # Движение сердца с ПРАВИЛЬНЫМИ границами
        # ИСПРАВЛЕНО: границы движения должны учитывать смещение текстуры
        speed = self.heart_speed * delta_time

        # Если текстура съезжает, нужно компенсировать это в границах движения
        # Эмпирически подобраны смещения
        horizontal_offset = self.heart_size * 0.3  # Компенсация для левой/правой границы
        vertical_offset = self.heart_size * 0.5  # Компенсация для верхней/нижней границы

        # Рассчитываем границы с учетом размера сердца и смещений
        left_boundary = self.arena_left + self.heart_size + horizontal_offset + 4
        right_boundary = self.arena_right - self.heart_size + horizontal_offset + 3.7
        bottom_boundary = self.arena_bottom + self.heart_size + vertical_offset - 1.5
        top_boundary = self.arena_top - self.heart_size + vertical_offset - 2.3

        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            self.heart_x = max(left_boundary, self.heart_x - speed)
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            self.heart_x = min(right_boundary, self.heart_x + speed)
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            self.heart_y = min(top_boundary, self.heart_y + speed)
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            self.heart_y = max(bottom_boundary, self.heart_y - speed)

        # Генерация пуль
        self.bullet_timer += delta_time
        if self.bullet_timer >= self.bullet_spawn_rate:
            self.create_bullet()
            self.bullet_timer = 0
            self.total_bullets += 1

        # Проверка столкновений и нанесение урона
        collision_detected = False
        for bullet in self.bullets:
            # Проверка столкновения с сердцем (используем центр hitbox)
            distance = math.sqrt((bullet["x"] - self.heart_x) ** 2 + (bullet["y"] - self.heart_y) ** 2)
            if distance < self.heart_size + self.bullet_radius:
                collision_detected = True
                break

        # Нанесение урона при столкновении (каждые 50 мс - УМЕНЬШИЛИ)
        if collision_detected:
            if current_time - self.last_damage_time >= self.damage_interval:
                self.player_hp -= 1
                self.last_damage_time = current_time
                self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

                # Проверка поражения
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_active = False
                    self.victory = False
                    self.end_game()
                    return

        # Обновление пуль
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            bullet["x"] += bullet["dx"] * bullet["speed"] * delta_time
            bullet["y"] += bullet["dy"] * bullet["speed"] * delta_time

            # Удаление пуль за пределами экрана
            if (bullet["x"] < -100 or bullet["x"] > SCREEN_WIDTH + 100 or
                    bullet["y"] < -100 or bullet["y"] > SCREEN_HEIGHT + 100):
                bullets_to_remove.append(i)
                self.bullets_dodged += 1
                self.stats_text.text = f"Уклонений: {self.bullets_dodged}"

        # Удаление отработанных пуль
        for i in sorted(bullets_to_remove, reverse=True):
            self.bullets.pop(i)

    def create_bullet(self):
        """Создание новой пули"""
        side = random.randint(0, 3)

        if side == 0:  # Сверху
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            start_y = SCREEN_HEIGHT + 50
        elif side == 1:  # Справа
            start_x = SCREEN_WIDTH + 50
            start_y = random.randint(50, SCREEN_HEIGHT - 50)
        elif side == 2:  # Снизу
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            start_y = -50
        else:  # Слева
            start_x = -50
            start_y = random.randint(50, SCREEN_HEIGHT - 50)

        # Цель - случайная точка внутри арены
        target_x = random.randint(
            int(self.arena_left + 30),
            int(self.arena_right - 30)
        )
        target_y = random.randint(
            int(self.arena_bottom + 30),
            int(self.arena_top - 30)
        )

        dx = target_x - start_x
        dy = target_y - start_y
        length = math.sqrt(dx * dx + dy * dy)

        if length > 0:
            dx /= length
            dy /= length

        # Добавление случайности в траекторию
        dx += random.uniform(-0.15, 0.15)
        dy += random.uniform(-0.15, 0.15)

        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        self.bullets.append({
            "x": start_x,
            "y": start_y,
            "dx": dx,
            "dy": dy,
            "speed": random.uniform(180, 220)
        })

    def end_game(self):
        """Завершение игры"""
        elapsed = time.time() - self.start_time if self.start_time else 0

        # Сохраняем статистику для передачи в ResultView
        self.game_stats = {
            "victory": self.victory,
            "time_survived": min(elapsed, 30.0),
            "bullets_dodged": self.bullets_dodged,
            "total_bullets": self.total_bullets,
            "hp_remaining": self.player_hp
        }

        arcade.schedule(self.show_results, 2.0)

    def show_results(self, delta_time):
        """Показать результаты игры"""
        arcade.unschedule(self.show_results)
        from .result_view import ResultView

        stats = self.game_stats
        result_view = ResultView(
            elapsed_time=stats["time_survived"],
            victory=stats["victory"],
            bullets_dodged=stats["bullets_dodged"],
            total_bullets=stats["total_bullets"],
            hp_remaining=stats["hp_remaining"]
        )
        result_view.setup()
        self.window.show_view(result_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if not self.paused:
                self.paused = True
                self.pause_start_time = time.time()
            else:
                self.paused = False
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                    self.pause_start_time = None
            return

        if not self.paused and self.game_active:
            if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D,
                       arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S]:
                self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D,
                   arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S]:
            self.keys_pressed.discard(key)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.paused:
            for button in self.pause_buttons:
                button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.paused and button == arcade.MOUSE_BUTTON_LEFT:
            if self.resume_button.check_click(x, y):
                self.paused = False
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                    self.pause_start_time = None
            elif self.menu_button.check_click(x, y):
                self.game_active = False
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                from .main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)