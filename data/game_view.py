import arcade
import math
import random
import time
import os
from collections import namedtuple
from pyglet.graphics import Batch
from data.beautiful_button import BeautifulButton
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT,
    BUTTON_SPACING, BACKGROUND_COLOR, SQUARE_COLOR,
    PAUSE_OVERLAY_COLOR
)

# Определяем тип Rect для draw_texture_rect
Rect = namedtuple('Rect', ['x', 'y', 'width', 'height'])


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.particles = []
        self.particle_colors = [
            (255, 50, 50),  # красный
            (255, 100, 100),  # светло-красный
            (255, 150, 150),  # розовый
        ]
        self.shoot_sound = None
        self.hit_sound = None
        self.win_sound = None
        self.lose_sound = None
        self.background_music = None
        self.sound_enabled = True
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
        self.heart_size = 25  # Размер хитбокса
        self.heart_speed = 200  # Скорость движения
        self.heart_texture = None  # Будет загружена в setup()

        # Анимация сердца (менее заметная пульсация)
        self.heart_pulse = 0.0
        self.heart_pulse_speed = 2.5
        self.heart_pulse_min = 0.92  # Минимальный масштаб (было 0.9)
        self.heart_pulse_max = 1.08  # Максимальный масштаб (было 1.1)

        # Система пуль
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_spawn_rate = 0.3  # секунды между пулями
        self.bullets_dodged = 0
        self.total_bullets = 0
        self.bullet_radius = 35  # УВЕЛИЧИЛИ размер пуль (было 25)

        # Спрайты для улучшенной коллизии
        self.heart_sprite = None
        self.bullet_sprites = arcade.SpriteList()

        # Декоративный элемент (звезда в углу) - БЕЗ СПРАЙТА, рисуем вручную
        self.decor_exists = True
        self.decor_x = 50
        self.decor_y = SCREEN_HEIGHT - 50
        self.decor_radius = 15
        self.decor_color = arcade.color.GOLD
        self.decor_angle = 0

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

        # Загрузка звуков
        try:
            self.shoot_sound = arcade.load_sound("materials/shoot.wav")
            self.hit_sound = arcade.load_sound("materials/hit.wav")
            self.win_sound = arcade.load_sound("materials/win.wav")
            self.lose_sound = arcade.load_sound("materials/lose.wav")
            self.background_music = arcade.load_sound("materials/music.wav")
        except Exception as e:
            print(f"Ошибка при загрузке звуков: {e}")
            print("Звуки не найдены. Создайте папку sounds/ с файлами:")
            print("- shoot.wav (звук выстрела)")
            print("- hit.wav (звук попадания)")
            print("- win.wav (победа)")
            print("- lose.wav (поражение)")
            print("- music.wav (фоновая музыка)")
            self.sound_enabled = False

        # Создание спрайта сердца для улучшенной коллизии (если текстура загружена)
        if self.heart_texture:
            try:
                self.heart_sprite = arcade.Sprite()
                self.heart_sprite.texture = self.heart_texture
                self.heart_sprite.width = self.heart_size * 2
                self.heart_sprite.height = self.heart_size * 2
                self.heart_sprite.center_x = self.heart_x
                self.heart_sprite.center_y = self.heart_y
                print("Спрайт сердца создан успешно")
            except Exception as e:
                print(f"Не удалось создать спрайт сердца: {e}")
                self.heart_sprite = None

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
        self.bullet_sprites.clear()
        self.bullet_timer = 0
        self.bullets_dodged = 0
        self.total_bullets = 0
        self.player_hp = self.max_hp
        self.last_damage_time = 0
        self.start_time = time.time()
        self.game_active = True
        self.victory = False
        self.keys_pressed.clear()
        self.heart_pulse = 0.0
        self.decor_angle = 0

        if self.heart_sprite:
            self.heart_sprite.center_x = self.heart_x
            self.heart_sprite.center_y = self.heart_y

        self.timer_text.text = f"Время: 30.0 сек"
        self.stats_text.text = f"Уклонений: 0"
        self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

    def on_draw(self):
        self.clear()

        # Фон
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        # Декоративный элемент (звезда в углу) - рисуем вручную
        if self.decor_exists:
            # Рисуем вращающуюся звезду
            for i in range(5):
                angle = self.decor_angle + i * 72  # 72 градуса между лучами (5 лучей)
                dx = math.cos(math.radians(angle)) * self.decor_radius * 1.5
                dy = math.sin(math.radians(angle)) * self.decor_radius * 1.5

                # Луч звезды
                arcade.draw_line(
                    self.decor_x, self.decor_y,
                    self.decor_x + dx, self.decor_y + dy,
                    self.decor_color, 3
                )

            # Центр звезды
            arcade.draw_circle_filled(
                self.decor_x, self.decor_y,
                self.decor_radius,
                self.decor_color
            )

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

        # Сердце (игрок) с пульсацией ОТНОСИТЕЛЬНО ЦЕНТРА и менее заметной
        if self.heart_texture:
            # Менее заметная пульсация
            pulse_progress = (math.sin(self.heart_pulse) + 1) / 2  # от 0 до 1
            pulse_scale = self.heart_pulse_min + (self.heart_pulse_max - self.heart_pulse_min) * pulse_progress

            # Визуальный размер сердца (центрируется относительно heart_x, heart_y)
            visual_width = self.heart_size * 1.8 * pulse_scale
            visual_height = self.heart_size * 1.8 * pulse_scale

            # Центрирование относительно координат сердца
            x = self.heart_x - visual_width / 2
            y = self.heart_y - visual_height / 2

            # Создаем объект Rect для draw_texture_rect
            rect = Rect(x=x, y=y, width=visual_width, height=visual_height)

            # Рисуем текстуру
            arcade.draw_texture_rect(self.heart_texture, rect)

            # Отладка: хитбокс (можно включить для тестирования)
            # arcade.draw_circle_outline(self.heart_x, self.heart_y, self.heart_size, arcade.color.RED, 1)
        else:
            # Запасной вариант: красный круг с пульсацией
            pulse_progress = (math.sin(self.heart_pulse) + 1) / 2
            pulse_scale = self.heart_pulse_min + (self.heart_pulse_max - self.heart_pulse_min) * pulse_progress
            radius = self.heart_size * 0.8 * pulse_scale
            arcade.draw_circle_filled(self.heart_x, self.heart_y, radius, arcade.color.RED)
            arcade.draw_circle_outline(self.heart_x, self.heart_y, radius, arcade.color.WHITE, 1)

        # Частицы
        for p in self.particles:
            alpha = int(255 * (p["lifetime"] / p["max_lifetime"]))
            color_with_alpha = (p["color"][0], p["color"][1], p["color"][2], alpha)
            arcade.draw_circle_filled(p["x"], p["y"], p["size"], color_with_alpha)

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

        # Пульсация сердца (менее заметная)
        self.heart_pulse += delta_time * self.heart_pulse_speed

        # Вращение декоративной звезды
        self.decor_angle += delta_time * 45  # 45 градусов в секунду

        # Обновление спрайта сердца (если он существует)
        if self.heart_sprite:
            self.heart_sprite.center_x = self.heart_x
            self.heart_sprite.center_y = self.heart_y

        # Обновление частиц
        particles_to_remove = []
        for i, p in enumerate(self.particles):
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["lifetime"] -= delta_time
            p["dy"] -= 0.1  # гравитация

            if p["lifetime"] <= 0:
                particles_to_remove.append(i)

        for i in sorted(particles_to_remove, reverse=True):
            self.particles.pop(i)

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

        # Движение сердца с границами
        speed = self.heart_speed * delta_time

        # Улучшенные границы (без сложных смещений)
        left_boundary = self.arena_left + self.heart_size
        right_boundary = self.arena_right - self.heart_size
        bottom_boundary = self.arena_bottom + self.heart_size
        top_boundary = self.arena_top - self.heart_size

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

        # УЛУЧШЕННАЯ ПРОВЕРКА СТОЛКНОВЕНИЙ
        collision_detected = False

        # Метод 1: Расстояние между центрами (основной)
        for bullet in self.bullets:
            distance = math.sqrt((bullet["x"] - self.heart_x) ** 2 + (bullet["y"] - self.heart_y) ** 2)
            # Учитываем пульсацию в хитбоксе
            current_heart_radius = self.heart_size * self.heart_pulse_max
            if distance < current_heart_radius + self.bullet_radius:
                collision_detected = True
                break

        # Метод 2: Если есть спрайт сердца, проверяем коллизию с пулями-спрайтами
        if self.heart_sprite and not collision_detected:
            # Создаём временный спрайт для пули для проверки коллизии
            for bullet in self.bullets:
                try:
                    bullet_sprite = arcade.SpriteCircle(self.bullet_radius, arcade.color.YELLOW)
                    bullet_sprite.center_x = bullet["x"]
                    bullet_sprite.center_y = bullet["y"]
                    if arcade.check_for_collision(self.heart_sprite, bullet_sprite):
                        collision_detected = True
                        break
                except:
                    # Если не удалось создать спрайт, используем только метод 1
                    pass

        # Нанесение урона при столкновении
        if collision_detected:
            if current_time - self.last_damage_time >= self.damage_interval:
                self.player_hp -= 1
                self.last_damage_time = current_time
                self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

                # Звук попадания
                if self.sound_enabled and self.hit_sound:
                    arcade.play_sound(self.hit_sound, volume=0.5)

                # Частицы при попадании
                self.create_hit_particles(self.heart_x, self.heart_y)

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

    def create_hit_particles(self, x, y):
        """Создать частицы крови при попадании"""
        for _ in range(8):  # 8 частиц за раз
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(3, 8)
            lifetime = random.uniform(0.5, 1.5)  # секунды
            color = random.choice(self.particle_colors)

            self.particles.append({
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "size": size,
                "lifetime": lifetime,
                "max_lifetime": lifetime,
                "color": color
            })

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

        # Звук выстрела
        if self.sound_enabled and self.shoot_sound:
            arcade.play_sound(self.shoot_sound, volume=0.3)

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

        # Звук победы/поражения
        if self.sound_enabled:
            if self.victory and self.win_sound:
                arcade.play_sound(self.win_sound)
            elif not self.victory and self.lose_sound:
                arcade.play_sound(self.lose_sound)

        arcade.schedule(self.show_results, 2.0)

    def show_results(self, delta_time):
        """Показать результаты игры"""
        arcade.unschedule(self.show_results)
        from data.result_view import ResultView

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
                from data.main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)
