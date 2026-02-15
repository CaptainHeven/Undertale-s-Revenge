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

Rect = namedtuple('Rect', ['x', 'y', 'width', 'height'])


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        # --- БАЛАНС ИГРЫ (Настраивай здесь) ---
        self.DEFAULT_WAVE_SPEED = 2.1  # Скорость волны палок (было 1.5, просил 1.0)
        self.DEFAULT_STICK_INTERVAL = 3  # Интервал спавна палок (в кадрах)
        self.wave_speed = self.DEFAULT_WAVE_SPEED
        self.stick_spawn_interval = self.DEFAULT_STICK_INTERVAL
        # --------------------------------------

        self.particles = []
        self.particle_colors = [
            (255, 50, 50),
            (255, 100, 100),
            (255, 150, 150),
        ]
        self.shoot_sound = None
        self.hit_sound = None
        self.win_sound = None
        self.lose_sound = None
        self.background_music = None
        self.sound_enabled = True
        self.game_active = True
        self.game_time = 30.0
        self.start_time = None
        self.paused = False
        self.pause_start_time = None
        self.victory = False

        self.player_hp = 92
        self.max_hp = 92
        self.last_damage_time = 0
        self.damage_interval = 0.1

        self.arena_width = 600
        self.arena_height = 250
        self.arena_left = SCREEN_WIDTH // 2 - self.arena_width // 2
        self.arena_right = SCREEN_WIDTH // 2 + self.arena_width // 2
        self.arena_bottom = SCREEN_HEIGHT // 2 - self.arena_height // 2
        self.arena_top = SCREEN_HEIGHT // 2 + self.arena_height // 2
        self.original_arena_left = self.arena_left
        self.original_arena_right = self.arena_right
        self.original_arena_bottom = self.arena_bottom
        self.original_arena_top = self.arena_top

        self.heart_x = SCREEN_WIDTH // 2
        self.heart_y = SCREEN_HEIGHT // 2
        self.heart_size = 25
        self.heart_speed = 200
        self.heart_texture = None
        self.heart_texture2 = None
        self.heart_rotation = 0

        self.heart_pulse = 0.0
        self.heart_pulse_speed = 2.5
        self.heart_pulse_min = 0.9
        self.heart_pulse_max = 1.0

        self.bullets = []
        self.bullet_timer = 0
        self.bullet_spawn_rate = 0.6
        self.bullets_dodged = 0
        self.total_bullets = 0
        self.bullet_radius = 35

        self.heart_sprite = None
        self.bullet_sprites = arcade.SpriteList()

        self.decor_exists = True
        self.decor_x = 50
        self.decor_y = SCREEN_HEIGHT - 50
        self.decor_radius = 15
        self.decor_color = arcade.color.GOLD
        self.decor_angle = 0

        self.keys_pressed = set()

        self.batch = None
        self.timer_text = None
        self.instruction_text = None
        self.pause_title_text = None
        self.pause_batch = None
        self.pause_buttons = []

        self.stats_text = None
        self.hp_text = None

        self.story_active = False
        self.story_step = 0
        self.story_timer = 0
        self.story_text = ""
        self.sun_has_eyes = False
        self.sun_is_angry = False
        self.sun_is_red = False
        self.sun_size_multiplier = 1.0
        self.sun_target_x = None
        self.sun_target_y = None
        self.sun_move_speed = 400
        self.sun_at_center = False
        self.sun_return_timer = 0
        self.sun_return_delay = 0.2
        self.sun_original_y = 0
        self.sun_first_move_done = False
        self.sun_original_speed = 200

        self.camera = arcade.camera.Camera2D()
        self.camera_zoom_target = 1.0
        self.camera_zoom = 1.0
        self.camera_zoom_speed = 2.0

        self.hard_mode = False
        self.hard_mode_timer = 0
        self.hard_mode_message = ""
        self.hard_mode_message_timer = 0
        self.hard_mode_text = None

        self.first_wave_complete = False
        self.first_phase_duration = 15.0  # Первая фаза 15 секунд
        self.first_phase_timer = 0

        self.sun_exhausted = False
        self.sun_exhaust_timer = 0
        self.sun_exhaust_time = 30.0  # Вторая фаза 30 секунд

        self.camera_target_sun = False

        # Диалоговое окно
        self.dialog_box_visible = False
        self.dialog_text = ""
        self.dialog_timer = 0
        self.dialog_duration = 0
        self.dialog_text_object = None

        # Третья фаза
        self.phase_3_active = False
        self.phase_3_timer = 0
        self.phase_3_duration = 15.0
        self.phase_3_step = 0
        self.phase_3_wait_for_bullets = False
        self.phase_3_step7_duration = 30.0  # Четвертая фаза 30 секунд
        self.phase_3_step7_message_shown = False  # Флаг для показа "я устал"
        self.gravity_enabled = False
        self.gravity_direction = "down"
        self.heart_velocity_x = 0
        self.heart_velocity_y = 0
        self.gravity_strength = 200
        self.shake_timer = 0
        self.shake_amount = 0
        self.camera_follow_heart = False
        self.arena_wall_move_speed = 500
        self.sticks = []
        self.phase_3_texture_changed = False
        self.phase_3_heart_grounded = False
        self.sun_pre_attack_y = 0
        self.jump_power = 0
        self.jump_key_pressed = False
        self.jump_time = 0
        self.max_jump_time = 0.5
        self.max_jump_height = 0
        self.stick_spawn_counter = 0
        self.stick_x_offset = 0
        self.phase_3_wait_timer = 0
        self.can_jump_this_ground = True  # Можно ли прыгнуть в текущем нахождении на земле
        self.jump_lock = False  # Блокировка прыжка

    def setup(self):
        try:
            possible_paths = [
                "materials/images/heart.png",
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

        try:
            self.heart_texture2 = arcade.load_texture("materials/images/heartN2.png")
            print("Текстура сердца heartN2 загружена")
        except:
            print("Файл heartN2.png не найден")
            self.heart_texture2 = None

        try:
            self.shoot_sound = arcade.load_sound("materials/sounds/shoot.wav")
            self.hit_sound = arcade.load_sound("materials/sounds/hit.mp3")
            self.win_sound = arcade.load_sound("materials/sounds/win.wav")
            self.lose_sound = arcade.load_sound("materials/sounds/lose.wav")
        except Exception as e:
            print(f"Ошибка при загрузке звуков: {e}")
            self.sound_enabled = False

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

        self.timer_text = arcade.Text(
            f"0.0 сек",
            SCREEN_WIDTH - 100,
            40,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        self.instruction_text = arcade.Text(
            "Уклоняйтесь от пуль! ESC - пауза",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        self.stats_text = arcade.Text(
            f"Уклонений: 0",
            20,
            80,
            arcade.color.LIGHT_GREEN,
            20,
            batch=self.batch
        )

        self.hp_text = arcade.Text(
            f"HP: {self.player_hp}/{self.max_hp}",
            20,
            50,
            arcade.color.WHITE,
            20,
            batch=self.batch
        )

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

        self.camera.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.camera.zoom = 1.0

        self.reset_game()

    def reset_game(self):
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
        self.heart_rotation = 0
        self.decor_angle = 0
        self.decor_x = 50
        self.decor_y = SCREEN_HEIGHT - 50
        self.decor_color = arcade.color.GOLD

        self.story_active = False
        self.story_step = 0
        self.story_timer = 0
        self.story_text = ""
        self.dialog_box_visible = False
        self.dialog_text = ""
        self.dialog_timer = 0
        self.dialog_text_object = None
        self.sun_has_eyes = False
        self.sun_is_angry = False
        self.sun_is_red = False
        self.sun_size_multiplier = 1.0
        self.sun_target_x = None
        self.sun_target_y = None
        self.sun_at_center = False
        self.sun_return_timer = 0
        self.sun_original_y = 0
        self.sun_first_move_done = False
        self.camera_zoom_target = 1.0
        self.camera_zoom = 1.0
        self.hard_mode = False
        self.hard_mode_timer = 0
        self.hard_mode_message = ""
        self.hard_mode_message_timer = 0
        self.hard_mode_text = None

        self.first_wave_complete = False
        self.first_phase_timer = 0

        self.sun_exhausted = False
        self.sun_exhaust_timer = 0
        self.sun_exhaust_time = 30.0

        if self.heart_sprite:
            self.heart_sprite.center_x = self.heart_x
            self.heart_sprite.center_y = self.heart_y

        self.timer_text.text = f"0.0 сек"
        self.stats_text.text = f"Уклонений: 0"
        self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

        self.camera_target_sun = False
        self.camera.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.camera.zoom = 1.0
        self.camera_zoom = 1.0
        self.camera_zoom_target = 1.0

        # Показываем инструкцию при старте
        if self.instruction_text:
            self.instruction_text.text = "Уклоняйтесь от пуль! ESC - пауза"

        # Сброс параметров третьей фазы
        self.phase_3_active = False
        self.phase_3_timer = 0
        self.phase_3_step = 0
        self.phase_3_wait_for_bullets = False
        self.phase_3_step7_message_shown = False
        self.gravity_enabled = False
        self.gravity_direction = "down"
        self.heart_velocity_x = 0
        self.heart_velocity_y = 0
        self.shake_timer = 0
        self.shake_amount = 0
        self.camera_follow_heart = False
        self.sticks = []
        self.phase_3_texture_changed = False
        self.phase_3_heart_grounded = False
        self.sun_pre_attack_y = 0
        self.jump_power = 0
        self.jump_key_pressed = False
        self.jump_time = 0
        self.max_jump_height = (self.arena_top - self.arena_bottom) * 0.8
        self.stick_spawn_counter = 0
        self.stick_x_offset = 0
        self.jump_lock = False

        # ИСПРАВЛЕНИЕ: Используем константы из __init__, а не жесткие значения
        self.wave_speed = self.DEFAULT_WAVE_SPEED
        self.stick_spawn_interval = self.DEFAULT_STICK_INTERVAL

    def show_dialog(self, text, duration=4.0):  # Все диалоги по 4 секунды
        """Показывает диалоговое окно с текстом на указанное время"""
        self.dialog_box_visible = True
        self.dialog_text = text
        self.dialog_timer = 0
        self.dialog_duration = duration

        # Создаем Text объект для диалога
        self.dialog_text_object = arcade.Text(
            text,
            0, 0,  # Временные координаты, обновятся в draw_dialog_box
            arcade.color.WHITE,
            20,
            width=360,
            multiline=True,
            align="center",
            font_name="Comic Sans MS"
        )

        # Прячем инструкцию во время диалога
        if self.instruction_text:
            self.instruction_text.text = ""

    def hide_dialog(self):
        """Скрывает диалоговое окно и возвращает инструкцию"""
        self.dialog_box_visible = False
        self.dialog_text = ""
        self.dialog_text_object = None

        # Возвращаем инструкцию, только если игра активна, не на паузе и не в режиме истории
        if self.instruction_text and not self.paused and self.game_active and not self.story_active:
            self.instruction_text.text = "Уклоняйтесь от пуль! ESC - пауза"

    def draw_dialog_box(self):
        """Отрисовывает диалоговое окно в стиле поля сердечка, перекрывающее арену"""
        if not self.dialog_box_visible or not self.dialog_text_object:
            return

        self.camera.use()

        # Большое окно, перекрывающее нижнюю часть арены
        box_width = 400
        box_height = 120
        box_x = self.decor_x - box_width // 2
        box_y = self.decor_y - 180

        # Черный фон как у поля
        arcade.draw_lrbt_rectangle_filled(
            box_x, box_x + box_width,
            box_y, box_y + box_height,
            (0, 0, 0, 220)
        )

        # Белая рамка как у поля
        arcade.draw_lrbt_rectangle_outline(
            box_x, box_x + box_width,
            box_y, box_y + box_height,
            arcade.color.WHITE, 3
        )

        # Обновляем позицию текста и рисуем
        self.dialog_text_object.x = box_x + 20
        self.dialog_text_object.y = box_y + box_height // 2 - 15
        self.dialog_text_object.draw()

    def draw_star(self, x, y, size, color):
        """Рисует звезду как у солнца"""
        for i in range(5):
            angle = self.decor_angle + i * 72
            dx = math.cos(math.radians(angle)) * size * 2
            dy = math.sin(math.radians(angle)) * size * 2
            arcade.draw_line(x, y, x + dx, y + dy, color, 2)
        arcade.draw_circle_filled(x, y, size, color)

    def on_draw(self):
        self.clear()
        self.camera.use()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        if self.decor_exists:
            if self.sun_is_red:
                sun_color = arcade.color.RED
            else:
                sun_color = arcade.color.GOLD

            current_radius = self.decor_radius * self.sun_size_multiplier

            for i in range(5):
                angle = self.decor_angle + i * 72
                dx = math.cos(math.radians(angle)) * current_radius * 1.5
                dy = math.sin(math.radians(angle)) * current_radius * 1.5
                arcade.draw_line(
                    self.decor_x, self.decor_y,
                    self.decor_x + dx, self.decor_y + dy,
                    sun_color, 3
                )

            arcade.draw_circle_filled(
                self.decor_x, self.decor_y,
                current_radius,
                sun_color
            )

            if self.sun_has_eyes:
                arcade.draw_circle_filled(
                    self.decor_x - current_radius * 0.4,
                    self.decor_y + current_radius * 0.3,
                    current_radius * 0.2,
                    arcade.color.BLACK
                )
                arcade.draw_circle_filled(
                    self.decor_x + current_radius * 0.4,
                    self.decor_y + current_radius * 0.3,
                    current_radius * 0.2,
                    arcade.color.BLACK
                )
                pupil_color = arcade.color.RED if self.sun_is_angry else arcade.color.WHITE
                arcade.draw_circle_filled(
                    self.decor_x - current_radius * 0.4,
                    self.decor_y + current_radius * 0.3,
                    current_radius * 0.1,
                    pupil_color
                )
                arcade.draw_circle_filled(
                    self.decor_x + current_radius * 0.4,
                    self.decor_y + current_radius * 0.3,
                    current_radius * 0.1,
                    pupil_color
                )

        # Отрисовка палочек с звездочками
        for stick in self.sticks:
            stick_width = self.heart_size * 0.6

            if stick["type"] == "top":
                arcade.draw_lrbt_rectangle_filled(
                    stick["x"] - stick_width / 2,
                    stick["x"] + stick_width / 2,
                    self.arena_top - stick["height"],
                    self.arena_top,
                    arcade.color.WHITE
                )
                self.draw_star(stick["x"], self.arena_top - stick["height"], 6, arcade.color.RED)

            elif stick["type"] == "bottom":
                arcade.draw_lrbt_rectangle_filled(
                    stick["x"] - stick_width / 2,
                    stick["x"] + stick_width / 2,
                    self.arena_bottom,
                    self.arena_bottom + stick["height"],
                    arcade.color.WHITE
                )
                self.draw_star(stick["x"], self.arena_bottom + stick["height"], 6, arcade.color.RED)

        # ЧЕРНЫЕ ПРЯМОУГОЛЬНИКИ (только во время летящих палочек)
        if self.phase_3_active and self.phase_3_step == 5:
            arcade.draw_lrbt_rectangle_filled(
                0, self.arena_left,
                0, SCREEN_HEIGHT,
                arcade.color.BLACK
            )
            arcade.draw_lrbt_rectangle_filled(
                self.arena_right, SCREEN_WIDTH,
                0, SCREEN_HEIGHT,
                arcade.color.BLACK
            )

        arcade.draw_lrbt_rectangle_outline(
            self.arena_left, self.arena_right,
            self.arena_bottom, self.arena_top,
            SQUARE_COLOR, 3
        )

        for bullet in self.bullets:
            arcade.draw_circle_filled(bullet["x"], bullet["y"], self.bullet_radius, arcade.color.YELLOW)
            arcade.draw_circle_outline(bullet["x"], bullet["y"], self.bullet_radius, arcade.color.ORANGE, 3)

        draw_x = self.heart_x
        draw_y = self.heart_y
        if self.shake_timer > 0:
            draw_x += random.randint(-self.shake_amount, self.shake_amount)
            draw_y += random.randint(-self.shake_amount, self.shake_amount)

        if self.heart_texture2 and self.phase_3_texture_changed:
            pulse_progress = (math.sin(self.heart_pulse) + 1) / 2
            pulse_scale = self.heart_pulse_min + (self.heart_pulse_max - self.heart_pulse_min) * pulse_progress

            texture = self.heart_texture2
            if self.gravity_direction == "right":
                texture = texture.rotate_90(-1)

            visual_width = self.heart_size * 1.8 * pulse_scale
            visual_height = self.heart_size * 1.8 * pulse_scale

            offset_x = 17
            offset_y = 17

            x = draw_x - visual_width / 2 + offset_x
            y = draw_y - visual_height / 2 + offset_y
            rect = Rect(x=x, y=y, width=visual_width, height=visual_height)
            arcade.draw_texture_rect(texture, rect)
        elif self.heart_texture:
            pulse_progress = (math.sin(self.heart_pulse) + 1) / 2
            pulse_scale = self.heart_pulse_min + (self.heart_pulse_max - self.heart_pulse_min) * pulse_progress
            visual_width = self.heart_size * 1.8 * pulse_scale
            visual_height = self.heart_size * 1.8 * pulse_scale

            offset_x = 17
            offset_y = 17

            x = draw_x - visual_width / 2 + offset_x
            y = draw_y - visual_height / 2 + offset_y
            rect = Rect(x=x, y=y, width=visual_width, height=visual_height)
            arcade.draw_texture_rect(self.heart_texture, rect)
        else:
            pulse_progress = (math.sin(self.heart_pulse) + 1) / 2
            pulse_scale = self.heart_pulse_min + (self.heart_pulse_max - self.heart_pulse_min) * pulse_progress
            radius = self.heart_size * 0.8 * pulse_scale
            arcade.draw_circle_filled(draw_x, draw_y, radius, arcade.color.RED)
            arcade.draw_circle_outline(draw_x, draw_y, radius, arcade.color.WHITE, 1)

        for p in self.particles:
            alpha = int(255 * (p["lifetime"] / p["max_lifetime"]))
            color_with_alpha = (p["color"][0], p["color"][1], p["color"][2], alpha)
            arcade.draw_circle_filled(p["x"], p["y"], p["size"], color_with_alpha)

        hp_bar_y = self.arena_bottom - 40
        hp_bar_width = 400
        hp_bar_height = 20
        hp_bar_x = SCREEN_WIDTH // 2 - hp_bar_width // 2

        arcade.draw_lrbt_rectangle_filled(
            hp_bar_x, hp_bar_x + hp_bar_width,
            hp_bar_y, hp_bar_y + hp_bar_height,
            (60, 60, 60)
        )

        hp_percentage = self.player_hp / self.max_hp
        hp_fill_width = hp_bar_width * hp_percentage

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

        arcade.draw_lrbt_rectangle_outline(
            hp_bar_x, hp_bar_x + hp_bar_width,
            hp_bar_y, hp_bar_y + hp_bar_height,
            arcade.color.WHITE, 2
        )

        arcade.draw_lrbt_rectangle_filled(
            SCREEN_WIDTH - 150, SCREEN_WIDTH - 20,
            20, 60,
            (0, 0, 0, 150)
        )

        self.batch.draw()
        self.draw_dialog_box()

        if self.hard_mode_message and self.hard_mode_message_timer > 0 and self.hard_mode_text:
            self.hard_mode_text.draw()

        if self.paused:
            self.window.use()
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, PAUSE_OVERLAY_COLOR)
            self.pause_title_text.draw()
            for button in self.pause_buttons:
                button.draw()
            self.pause_batch.draw()
            self.camera.use()

    def update_camera(self, delta_time):
        if not self.camera:
            return

        zoom_diff = self.camera_zoom_target - self.camera_zoom
        if abs(zoom_diff) > 0.01:
            self.camera_zoom += zoom_diff * self.camera_zoom_speed * delta_time
        else:
            self.camera_zoom = self.camera_zoom_target

        self.camera.zoom = self.camera_zoom

        if self.camera_follow_heart:
            target_x = SCREEN_WIDTH // 2
            target_y = SCREEN_HEIGHT // 2
        elif self.camera_target_sun:
            target_x = self.decor_x
            target_y = self.decor_y
        else:
            target_x = SCREEN_WIDTH // 2
            target_y = SCREEN_HEIGHT // 2
            if self.sun_at_center and self.camera_zoom > 1.0:
                target_y = int(target_y * 0.7)

        current_x, current_y = self.camera.position
        smooth_speed = 4.0
        new_x = current_x + (target_x - current_x) * smooth_speed * delta_time
        new_y = current_y + (target_y - current_y) * smooth_speed * delta_time
        self.camera.position = (new_x, new_y)

    def update_sun_movement(self, delta_time):
        if self.sun_target_x is None or self.sun_target_y is None:
            return

        self.camera_target_sun = True

        dx = self.sun_target_x - self.decor_x
        dy = self.sun_target_y - self.decor_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 5:
            if distance > 0:
                dx /= distance
                dy /= distance
            self.decor_x += dx * self.sun_move_speed * delta_time
            self.decor_y += dy * self.sun_move_speed * delta_time
        else:
            self.decor_x = self.sun_target_x
            self.decor_y = self.sun_target_y
            self.sun_at_center = True
            self.sun_target_x = None
            self.sun_target_y = None

    def update_story(self, delta_time):
        self.story_timer += delta_time

        if self.story_step == 1:
            if self.sun_at_center:
                self.sun_has_eyes = True
                self.show_dialog("Пора повеселиться!", 4.0)  # 4 секунды
                self.story_step = 2
                self.story_timer = 0
                self.camera_zoom_target = 1.8
        elif self.story_step == 2:
            if self.story_timer >= 4.0:  # 4 секунды
                self.show_dialog("Может я не так силён, но...", 4.0)  # 4 секунды
                self.story_step = 3
                self.story_timer = 0
                self.camera_zoom_target = 2.0
        elif self.story_step == 3:
            if self.story_timer >= 4.0:  # 4 секунды
                self.sun_is_angry = True
                self.sun_is_red = True
                self.sun_size_multiplier = 1.8
                self.show_dialog("Я постараюсь >:)", 4.0)  # 4 секунды
                self.story_step = 4
                self.story_timer = 0
        elif self.story_step == 4:
            if self.story_timer >= 4.0:  # 4 секунды
                self.hide_dialog()
                self.hard_mode = True
                self.hard_mode_timer = 0
                self.hard_mode_message = "ТЕБЕ КОНЕЦ, МЕЛОЧЬ!"
                self.hard_mode_message_timer = 3.0

                # Создаем Text объект для сообщения хард мода
                self.hard_mode_text = arcade.Text(
                    self.hard_mode_message,
                    SCREEN_WIDTH // 2,
                    115,
                    arcade.color.RED,
                    36,
                    anchor_x="center",
                    anchor_y="center",
                    font_name="Arial",
                    bold=True
                )

                self.story_step = 5
                self.camera_zoom_target = 1.0
                self.control_locked = False
                self.camera_target_sun = False
        elif self.story_step == 5:
            self.story_active = False

    def update_hard_mode(self, delta_time):
        self.hard_mode_timer += delta_time

        if not self.sun_exhausted and self.hard_mode_timer >= self.sun_exhaust_time:
            self.sun_exhausted = True
            self.sun_exhaust_timer = 0
            self.phase_3_wait_for_bullets = True
            self.hard_mode_message = ""
            self.hard_mode_text = None

        if self.phase_3_wait_for_bullets and len(self.bullets) == 0:
            self.start_phase_3()

        if self.sun_exhausted:
            self.sun_exhaust_timer += delta_time

        if self.hard_mode_message_timer > 0:
            self.hard_mode_message_timer -= delta_time
            if self.hard_mode_message_timer <= 0:
                self.hard_mode_text = None
                self.hard_mode_message = ""

        if not self.sun_exhausted and self.hard_mode_timer >= 3.0:
            self.bullet_timer += delta_time
            if self.bullet_timer >= 0.4:
                self.create_bullet()
                if random.random() < 0.3:
                    self.create_bullet()
                self.bullet_timer = 0
                self.total_bullets += 1

    def start_phase_3(self):
        """Запуск третьей фазы"""
        self.phase_3_active = True
        self.phase_3_timer = 0
        self.phase_3_step = 1
        self.phase_3_wait_for_bullets = False
        self.phase_3_step7_message_shown = False  # Сбрасываем флаг сообщения

        # Прибавляем 0.5 * максимального хп
        self.player_hp = min(self.max_hp, self.player_hp + int(self.max_hp * 0.5))
        self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

        # Выводим красным текстом "А теперь.."
        self.hard_mode_message = "А теперь.."
        self.hard_mode_message_timer = 2.0
        self.hard_mode_text = arcade.Text(
            self.hard_mode_message,
            SCREEN_WIDTH // 2,
            115,
            arcade.color.RED,
            36,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )

        # Сохраняем оригинальную позицию солнца
        self.sun_original_y = self.decor_y
        self.sun_pre_attack_y = self.decor_y + 30

        # Используем обычную скорость солнца
        self.sun_move_speed = 200

        # Первый рывок - поднимается выше
        self.sun_target_x = self.decor_x
        self.sun_target_y = self.sun_pre_attack_y
        self.camera_target_sun = True
        self.sun_first_move_done = False

    def update_phase_3(self, delta_time):
        """Обновление третьей фазы"""
        self.phase_3_timer += delta_time

        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            if self.shake_timer <= 0:
                self.shake_amount = 0

        # Шаг 1: Солнце поднимается выше
        if self.phase_3_step == 1:
            if abs(self.decor_y - self.sun_pre_attack_y) < 5 and self.sun_target_y is not None:
                self.phase_3_step = 2
                # Резкий рывок в самый низ
                self.sun_target_x = self.decor_x
                self.sun_target_y = self.arena_top - 20
                self.sun_move_speed = 400
        # Шаг 2: Солнце резко вниз
        elif self.phase_3_step == 2:
            if abs(self.decor_y - self.sun_target_y) < 5 and self.sun_target_y is not None:
                # В этот момент меняем текстуру и включаем гравитацию
                if not self.phase_3_texture_changed:
                    self.phase_3_texture_changed = True
                    self.gravity_enabled = True
                    self.gravity_direction = "down"
                    self.heart_velocity_y = -300
                    # Прижимаем к полу
                    visual_height = self.heart_size * 1.8
                    self.heart_y = self.arena_bottom + visual_height / 2
                    # Эффект удара об пол
                    self.shake_timer = 0.5
                    self.shake_amount = 12
                    self.phase_3_heart_grounded = True

                self.phase_3_step = 3
                # Возвращаем солнце на место
                self.sun_target_x = self.decor_x
                self.sun_target_y = self.sun_original_y
                self.sun_move_speed = 200
        # Шаг 3: Солнце возвращается обратно
        elif self.phase_3_step == 3:
            if abs(self.decor_y - self.sun_original_y) < 5 and self.sun_target_y is not None:
                self.phase_3_step = 4
                # Солнце делает рывок вправо
                self.sun_target_x = self.decor_x + 100
                self.sun_target_y = self.decor_y
                self.sun_move_speed = 300
        # Шаг 4: Солнце движется вправо
        elif self.phase_3_step == 4:
            if abs(self.decor_x - self.sun_target_x) < 5 and self.sun_target_x is not None:
                self.phase_3_step = 5
                # Меняем гравитацию на право
                self.gravity_direction = "right"
                self.heart_velocity_x = 200
                self.heart_velocity_y = 0
                self.camera_follow_heart = True
                # Скрываем надпись "А теперь.." в середине третьей фазы
                self.hard_mode_message = ""
                self.hard_mode_text = None
                # Сбрасываем позицию палок
                self.sticks = []
                self.stick_spawn_counter = 0
                self.stick_x_offset = 0
                self.phase_3_timer = 0
                self.sun_move_speed = 200
        # Шаг 5: Основная фаза - палки двигаются влево
        elif self.phase_3_step == 5:
            # Двигаем палки влево с увеличенной скоростью
            for stick in self.sticks:
                stick["x"] -= self.arena_wall_move_speed * delta_time

            # Удаляем палки за левой границей
            self.sticks = [stick for stick in self.sticks if stick["x"] > self.arena_left - 50]

            # Спавн новых палок
            self.stick_spawn_counter += 1
            if self.stick_spawn_counter >= self.stick_spawn_interval:
                self.stick_spawn_counter = 0
                self.stick_x_offset += 3.0  # 3 пикселя между палками

                # Создаем новую пару палок
                self.add_stick_pair(self.arena_right + self.stick_x_offset)

            # Проверяем столкновения
            self.check_stick_collisions()

            # Сердце всегда по середине по горизонтали
            visual_width = self.heart_size * 1.8
            self.heart_x = self.arena_left + (self.arena_right - self.arena_left) / 2

            # Завершаем фазу палок
            if self.phase_3_timer >= self.phase_3_duration:
                # Полностью останавливаем движение палок
                self.sticks = []

                # Возвращаем нормальное движение сердца (отключаем гравитацию)
                self.gravity_enabled = False
                self.heart_velocity_x = 0
                self.heart_velocity_y = 0

                # Меняем картинку сердца на первую
                self.phase_3_texture_changed = False

                # Солнце делает рывок вверх (как в начале третьей фазы)
                self.sun_target_x = self.decor_x
                self.sun_target_y = self.sun_pre_attack_y  # рывок вверх
                self.sun_move_speed = 400
                self.camera_target_sun = True

                self.phase_3_timer = 0
                self.phase_3_step = 6

        # Шаг 6: Возвращаем солнце обратно
        elif self.phase_3_step == 6:
            if abs(self.decor_y - self.sun_pre_attack_y) < 5:
                self.sun_target_x = SCREEN_WIDTH // 2
                self.sun_target_y = SCREEN_HEIGHT - 150
                self.sun_move_speed = 200
                self.camera_target_sun = False

                # Переходим к повтору второй фазы (пули), но остаёмся в phase_3
                self.phase_3_step = 7
                self.phase_3_timer = 0
                self.bullet_spawn_rate = 0.4
                self.bullets = []
                self.phase_3_step7_message_shown = False  # Сбрасываем флаг для сообщения "я устал"

        # Шаг 7: Повтор второй фазы (пули) - четвертая фаза 30 секунд
        elif self.phase_3_step == 7:
            self.phase_3_timer += delta_time

            # Показываем "я устал" на 20-й секунде
            if self.phase_3_timer >= 20.0 and not self.phase_3_step7_message_shown:
                self.phase_3_step7_message_shown = True
                self.hard_mode_message = "я устал"
                self.hard_mode_message_timer = 2.0
                self.hard_mode_text = arcade.Text(
                    self.hard_mode_message,
                    SCREEN_WIDTH // 2,
                    115,
                    arcade.color.RED,
                    36,
                    anchor_x="center",
                    anchor_y="center",
                    font_name="Arial",
                    bold=True
                )

            # Стрельба пулями как во второй фазе
            self.bullet_timer += delta_time
            if self.bullet_timer >= self.bullet_spawn_rate:
                self.create_bullet()
                if random.random() < 0.3:
                    self.create_bullet()
                self.bullet_timer = 0
                self.total_bullets += 1

            # Проверка урона от пуль
            current_time = time.time()
            collision_detected = False

            for bullet in self.bullets:
                distance = math.sqrt((bullet["x"] - self.heart_x) ** 2 + (bullet["y"] - self.heart_y) ** 2)
                current_heart_radius = self.heart_size * self.heart_pulse_max
                if distance < current_heart_radius + self.bullet_radius:
                    collision_detected = True
                    break

            if collision_detected:
                if current_time - self.last_damage_time >= self.damage_interval:
                    self.player_hp -= 1
                    self.last_damage_time = current_time
                    self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

                    if self.sound_enabled and self.hit_sound:
                        arcade.play_sound(self.hit_sound, volume=0.25)

                    self.create_hit_particles(self.heart_x, self.heart_y)

                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_active = False
                        self.victory = False
                        self.end_game()
                        return

            # Завершаем фазу пуль через 30 секунд
            if self.phase_3_timer >= self.phase_3_step7_duration:
                # Очищаем пули и переходим к следующему шагу
                self.bullets = []
                self.phase_3_step = 8
                self.phase_3_timer = 0

                # Если дошли до конца – победа
                self.victory = True
                self.game_active = False
                self.end_game()

        # Обработка гравитации
        if self.gravity_enabled and self.game_active and not self.paused:
            if self.gravity_direction == "down":
                visual_height = self.heart_size * 1.8
                bottom_boundary = self.arena_bottom + visual_height / 2
                top_boundary = self.arena_top - visual_height / 2

                # Проверка: на полу ли сердце (с небольшим допуском)
                on_ground = abs(self.heart_y - bottom_boundary) < 2

                # Если на полу - снимаем блокировку прыжка
                if on_ground:
                    self.jump_lock = False

                # Прыжок: только если на полу, нет блокировки и нажата вверх
                if on_ground and not self.jump_lock and (
                        arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed):
                    self.heart_velocity_y = 150
                    # Важно: не добавляем импульс повторно, пока держим кнопку

                # Гравитация всегда действует вниз
                self.heart_velocity_y -= self.gravity_strength * delta_time
                self.heart_y += self.heart_velocity_y * delta_time

                # Границы арены
                if self.heart_y < bottom_boundary:
                    self.heart_y = bottom_boundary
                    self.heart_velocity_y = 0
                if self.heart_y > top_boundary:
                    self.heart_y = top_boundary
                    self.heart_velocity_y = 0

            elif self.gravity_direction == "right":
                # Гравитация вправо
                self.heart_velocity_x += self.gravity_strength * delta_time
                self.heart_x += self.heart_velocity_x * delta_time

                # Ограничиваем по границам
                visual_width = self.heart_size * 1.8
                right_boundary = self.arena_right - visual_width / 2
                if self.heart_x > right_boundary:
                    self.heart_x = right_boundary
                    self.heart_velocity_x = 0

                left_boundary = self.arena_left + visual_width / 2
                if self.heart_x < left_boundary:
                    self.heart_x = left_boundary
                    self.heart_velocity_x = 0

    def add_stick_pair(self, x):
        """Добавляет пару палок с пустым пространством 35% и медленной волной от 5% до 95%"""
        stick_width = self.heart_size * 0.6
        arena_height = self.arena_top - self.arena_bottom

        # МЕДЛЕННАЯ ВОЛНА - используем wave_speed
        # Пустое пространство движется от 5% до 95% высоты арены
        wave_pos = 0.5 + 0.45 * math.sin(self.phase_3_timer * self.wave_speed)

        # УВЕЛИЧЕННОЕ ПУСТОЕ ПРОСТРАНСТВО - 35% от высоты арены
        empty_height = arena_height * 0.35

        # Центр пустого пространства
        empty_center_y = self.arena_bottom + arena_height * wave_pos

        # Верхняя граница пустого пространства
        empty_top = empty_center_y + empty_height / 2
        # Нижняя граница пустого пространства
        empty_bottom = empty_center_y - empty_height / 2

        # Верхняя палочка - от верха арены до верхней границы пустого пространства
        top_height = self.arena_top - empty_top
        if top_height > 5:  # Минимальная высота
            self.sticks.append({
                "x": x,
                "type": "top",
                "height": top_height,
                "width": stick_width,
                "active": True,
                "last_hit": 0  # ИСПРАВЛЕНИЕ: Храним время удара внутри палки
            })

        # Нижняя палочка - от нижней границы пустого пространства до низа арены
        bottom_height = empty_bottom - self.arena_bottom
        if bottom_height > 5:  # Минимальная высота
            self.sticks.append({
                "x": x,
                "type": "bottom",
                "height": bottom_height,
                "width": stick_width,
                "active": True,
                "last_hit": 0  # ИСПРАВЛЕНИЕ: Храним время удара внутри палки
            })

    def check_stick_collisions(self):
        """Проверка столкновений с палочками (Исправленная версия)"""
        current_time = time.time()
        heart_radius = self.heart_size * self.heart_pulse_max

        for stick in self.sticks:
            if not stick["active"]:
                continue

            collision = False

            if stick["type"] == "top":
                if (abs(self.heart_x - stick["x"]) < (heart_radius + stick["width"] / 2) and
                        self.heart_y + heart_radius > self.arena_top - stick["height"]):
                    collision = True

            elif stick["type"] == "bottom":
                if (abs(self.heart_x - stick["x"]) < (heart_radius + stick["width"] / 2) and
                        self.heart_y - heart_radius < self.arena_bottom + stick["height"]):
                    collision = True

            if collision:
                # Проверяем кулдаун внутри самой палки
                if current_time - stick.get("last_hit", 0) >= self.damage_interval:
                    self.player_hp -= 1
                    self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

                    # Обновляем время удара для ЭТОЙ конкретной палки
                    stick["last_hit"] = current_time

                    if self.sound_enabled and self.hit_sound:
                        arcade.play_sound(self.hit_sound, volume=0.25)

                    self.create_hit_particles(self.heart_x, self.heart_y)

                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_active = False
                        self.victory = False
                        self.end_game()
                        return

    def on_update(self, delta_time):
        if not self.game_active or self.paused:
            return

        self.update_camera(delta_time)
        self.heart_pulse += delta_time * self.heart_pulse_speed
        self.decor_angle += delta_time * 45

        # Обновление таймера диалога
        if self.dialog_box_visible:
            self.dialog_timer += delta_time
            if self.dialog_timer >= self.dialog_duration:
                self.hide_dialog()

        if self.heart_sprite:
            self.heart_sprite.center_x = self.heart_x
            self.heart_sprite.center_y = self.heart_y

        particles_to_remove = []
        for i, p in enumerate(self.particles):
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["lifetime"] -= delta_time
            p["dy"] -= 0.1
            if p["lifetime"] <= 0:
                particles_to_remove.append(i)
        for i in sorted(particles_to_remove, reverse=True):
            self.particles.pop(i)

        current_time = time.time()

        if self.start_time:
            elapsed = current_time - self.start_time
            self.timer_text.text = f"{elapsed:.1f} сек"

        # Первая фаза - 15 секунд
        if not self.first_wave_complete:
            self.first_phase_timer += delta_time
            self.bullet_timer += delta_time
            if self.bullet_timer >= self.bullet_spawn_rate:
                self.create_bullet()
                self.bullet_timer = 0
                self.total_bullets += 1

            if self.first_phase_timer >= self.first_phase_duration:
                self.first_wave_complete = True
                self.story_active = True
                self.story_step = 1
                self.story_timer = 0
                self.sun_target_x = SCREEN_WIDTH // 2
                self.sun_target_y = SCREEN_HEIGHT - 100
                self.sun_move_speed = 200
                if self.instruction_text:
                    self.instruction_text.text = ""

        if self.story_active:
            self.update_story(delta_time)

        self.update_sun_movement(delta_time)

        if self.phase_3_active:
            self.update_phase_3(delta_time)
        elif self.hard_mode:
            self.update_hard_mode(delta_time)

        # Движение с клавиатуры
        speed = self.heart_speed * delta_time

        visual_width = self.heart_size * 1.8
        visual_height = self.heart_size * 1.8

        left_boundary = self.arena_left + visual_width / 2
        right_boundary = self.arena_right - visual_width / 2
        bottom_boundary = self.arena_bottom + visual_height / 2
        top_boundary = self.arena_top - visual_height / 2

        if self.gravity_direction == "right" and self.phase_3_step == 5:
            # В режиме гравитации вправо - движение вверх/вниз клавишами ВЛЕВО/ВПРАВО (наоборот)
            if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
                self.heart_y = max(bottom_boundary, self.heart_y - speed)  # ВЛЕВО = ВНИЗ
                self.heart_velocity_y = 0
            if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
                self.heart_y = min(top_boundary, self.heart_y + speed)  # ВПРАВО = ВВЕРХ
                self.heart_velocity_y = 0
            # Горизонтальное движение заблокировано полностью
            self.heart_velocity_x = 0
        elif self.phase_3_step == 6:
            # В режиме прыжков - движение влево/вправо
            if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
                self.heart_x = max(left_boundary, self.heart_x - speed)
            if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
                self.heart_x = min(right_boundary, self.heart_x + speed)
            # Прыжок клавишей ВВЕРХ - зарядка прыжка
            if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
                if self.heart_y <= bottom_boundary + 1:
                    self.jump_time += delta_time
                    if self.jump_time > self.max_jump_time:
                        self.jump_time = self.max_jump_time
            else:
                if self.jump_time > 0 and self.heart_y <= bottom_boundary + 1:
                    # Совершаем прыжок при отпускании
                    jump_power = (self.jump_time / self.max_jump_time) * 700
                    self.heart_velocity_y = jump_power
                    self.jump_time = 0
        else:
            # Обычный режим
            if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
                self.heart_x = max(left_boundary, self.heart_x - speed)
            if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
                self.heart_x = min(right_boundary, self.heart_x + speed)
            if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
                self.heart_y = min(top_boundary, self.heart_y + speed)
            if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
                self.heart_y = max(bottom_boundary, self.heart_y - speed)

        # ХИТБОКС В ЦЕНТРЕ
        if not self.phase_3_active:
            collision_detected = False

            for bullet in self.bullets:
                distance = math.sqrt((bullet["x"] - self.heart_x) ** 2 + (bullet["y"] - self.heart_y) ** 2)
                current_heart_radius = self.heart_size * self.heart_pulse_max
                if distance < current_heart_radius + self.bullet_radius:
                    collision_detected = True
                    break

            if collision_detected:
                if current_time - self.last_damage_time >= self.damage_interval:
                    self.player_hp -= 1
                    self.last_damage_time = current_time
                    self.hp_text.text = f"HP: {self.player_hp}/{self.max_hp}"

                    if self.sound_enabled and self.hit_sound:
                        arcade.play_sound(self.hit_sound, volume=0.25)

                    self.create_hit_particles(self.heart_x, self.heart_y)

                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_active = False
                        self.victory = False
                        self.end_game()
                        return

        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            bullet["x"] += bullet["dx"] * bullet["speed"] * delta_time
            bullet["y"] += bullet["dy"] * bullet["speed"] * delta_time

            if (bullet["x"] < -100 or bullet["x"] > SCREEN_WIDTH + 100 or
                    bullet["y"] < -100 or bullet["y"] > SCREEN_HEIGHT + 100):
                bullets_to_remove.append(i)
                self.bullets_dodged += 1
                self.stats_text.text = f"Уклонений: {self.bullets_dodged}"

        for i in sorted(bullets_to_remove, reverse=True):
            self.bullets.pop(i)

    def create_hit_particles(self, x, y):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(3, 8)
            lifetime = random.uniform(0.5, 1.5)
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
        side = random.randint(0, 3)

        if side == 0:
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            start_y = SCREEN_HEIGHT + 50
        elif side == 1:
            start_x = SCREEN_WIDTH + 50
            start_y = random.randint(50, SCREEN_HEIGHT - 50)
        elif side == 2:
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            start_y = -50
        else:
            start_x = -50
            start_y = random.randint(50, SCREEN_HEIGHT - 50)

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

        if self.sound_enabled and self.shoot_sound:
            arcade.play_sound(self.shoot_sound, volume=0.3)

    def end_game(self):
        elapsed = time.time() - self.start_time if self.start_time else 0

        self.game_stats = {
            "victory": self.victory,
            "time_survived": elapsed,
            "bullets_dodged": self.bullets_dodged,
            "total_bullets": self.total_bullets,
            "hp_remaining": self.player_hp,
            "sun_exhausted": self.sun_exhausted
        }

        if self.sound_enabled:
            if self.victory and self.win_sound:
                arcade.play_sound(self.win_sound)
            elif not self.victory and self.lose_sound:
                arcade.play_sound(self.lose_sound)

        arcade.schedule(self.show_results, 2.0)

    def show_results(self, delta_time):
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
            # Запрещаем паузу, если солнце движется или идёт диалог
            if self.sun_target_x is not None or self.dialog_box_visible:
                return  # Игнорируем ESC

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

        # Если отпустили вверх в воздухе - блокируем прыжки до земли
        if key in [arcade.key.UP, arcade.key.W]:
            visual_height = self.heart_size * 1.8
            bottom_boundary = self.arena_bottom + visual_height / 2
            if abs(self.heart_y - bottom_boundary) >= 2:  # в воздухе
                self.jump_lock = True

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
