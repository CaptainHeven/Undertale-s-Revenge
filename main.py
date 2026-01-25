import arcade
import math
import random
import time
from pyglet.graphics import Batch

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
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

    def __init__(self, center_x, center_y, width, height, text, font_size=26):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.hover_animation = 0
        self.text_object = None

    def create_text_object(self, batch):
        self.text_object = arcade.Text(
            self.text,
            self.center_x,
            self.center_y,
            BUTTON_TEXT_COLOR,
            self.font_size,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True,
            batch=batch
        )

    def draw(self):
        if self.is_hovered:
            self.hover_animation = min(1.0, self.hover_animation + 0.1)
        else:
            self.hover_animation = max(0.0, self.hover_animation - 0.1)

        mix_amount = self.hover_animation
        r = int(BUTTON_COLOR[0] * (1 - mix_amount) + BUTTON_HOVER_COLOR[0] * mix_amount)
        g = int(BUTTON_COLOR[1] * (1 - mix_amount) + BUTTON_HOVER_COLOR[1] * mix_amount)
        b = int(BUTTON_COLOR[2] * (1 - mix_amount) + BUTTON_HOVER_COLOR[2] * mix_amount)
        current_color = (r, g, b)

        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, current_color)

        border_color = (180, 180, 220, 100 + int(100 * self.hover_animation))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, border_color, 2)

        if self.text_object:
            if self.is_hovered:
                self.text_object.color = (255, 255, 200)
            else:
                self.text_object.color = BUTTON_TEXT_COLOR

    def check_hover(self, x, y):
        self.is_hovered = (
                self.center_x - self.width / 2 < x < self.center_x + self.width / 2 and
                self.center_y - self.height / 2 < y < self.center_y + self.height / 2
        )
        return self.is_hovered

    def check_click(self, x, y):
        return self.check_hover(x, y)


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.batch = None
        self.title_text = None
        self.subtitle_text = None

    def setup(self):
        self.batch = Batch()

        button_y = SCREEN_HEIGHT // 2 + BUTTON_HEIGHT

        self.play_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ИГРАТЬ"
        )
        self.play_button.create_text_object(self.batch)
        self.buttons.append(self.play_button)

        self.settings_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - (BUTTON_HEIGHT + BUTTON_SPACING),
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "НАСТРОЙКИ"
        )
        self.settings_button.create_text_object(self.batch)
        self.buttons.append(self.settings_button)

        self.exit_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - 2 * (BUTTON_HEIGHT + BUTTON_SPACING),
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ"
        )
        self.exit_button.create_text_object(self.batch)
        self.buttons.append(self.exit_button)

        self.title_text = arcade.Text(
            "ГЛАВНОЕ МЕНЮ",
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

        self.subtitle_text = arcade.Text(
            "Управляйте точкой стрелками, ESC - пауза",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 160,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

    def on_draw(self):
        self.clear()

        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        for button in self.buttons:
            button.draw()

        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
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

    def __init__(self):
        super().__init__()
        self.buttons = []
        self.batch = None
        self.title_text = None
        self.message_text = None

    def setup(self):
        self.batch = Batch()

        # Кнопка "Назад"
        self.back_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "НАЗАД"
        )
        self.back_button.create_text_object(self.batch)
        self.buttons.append(self.back_button)

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

        self.message_text = arcade.Text(
            "сун",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.LIGHT_GRAY,
            32,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

    def on_draw(self):
        self.clear()

        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        self.back_button.draw()
        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.back_button.check_click(x, y):
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.state = "PLAYER_TURN"
        self.player_hp = 20
        self.enemy_hp = 30

        self.square_size = 320
        self.square_left = SCREEN_WIDTH // 2 - self.square_size // 2
        self.square_right = SCREEN_WIDTH // 2 + self.square_size // 2
        self.square_bottom = SCREEN_HEIGHT // 2 - self.square_size // 2
        self.square_top = SCREEN_HEIGHT // 2 + self.square_size // 2

        self.heart_x = SCREEN_WIDTH // 2
        self.heart_y = SCREEN_HEIGHT // 2
        self.heart_size = 20

        self.enemy_x = SCREEN_WIDTH // 2
        self.enemy_y = self.square_top + 150
        self.ghost_base_y = self.square_top + 150

        self.bullets = []
        self.bullet_timer = 0
        self.bullet_phase_timer = 0
        self.bullet_phase_duration = 10
        self.is_bullet_phase_active = False

        self.ghost_move_timer = 0
        self.ghost_move_speed = 1.5
        self.ghost_move_range = 30

        self.hit_animation_timer = 0
        self.is_hit = False

        self.keys_pressed = set()
        self.menu_options = ["АТАКА"]
        self.selected_option = 0

        self.attack_timer = 0
        self.attack_active = False

        self.paused = False
        self.pause_buttons = []
        self.pause_start_time = None

        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_active = True

        self.batch = None
        self.hp_text = None
        self.menu_texts = []
        self.time_text = None
        self.instruction_text = None
        self.pause_title_text = None
        self.pause_batch = None

    def setup(self):
        self.batch = Batch()

        self.hp_text = arcade.Text(
            f"HP: {self.player_hp}/20",
            50,
            SCREEN_HEIGHT - 50,
            arcade.color.WHITE,
            24,
            batch=self.batch
        )

        self.enemy_hp_text = arcade.Text(
            f"Враг HP: {self.enemy_hp}",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 50,
            arcade.color.WHITE,
            24,
            batch=self.batch
        )

        menu_y = 200
        for i, option in enumerate(self.menu_options):
            color = arcade.color.YELLOW if i == self.selected_option else arcade.color.WHITE
            text = arcade.Text(
                option,
                50,
                menu_y,
                color,
                24,
                batch=self.batch
            )
            self.menu_texts.append(text)
            menu_y -= 40

        self.time_text = arcade.Text(
            "Время: 0.0 сек",
            SCREEN_WIDTH - 150,
            SCREEN_HEIGHT - 30,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="left",
            batch=self.batch
        )

        self.instruction_text = arcade.Text(
            "ESC - пауза",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.LIGHT_GRAY,
            16,
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

        self.finish_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            button_y - BUTTON_HEIGHT // 2 - BUTTON_SPACING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ЗАВЕРШИТЬ ИГРУ"
        )
        self.finish_button.create_text_object(self.pause_batch)
        self.pause_buttons.append(self.finish_button)

        # Сброс
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_active = True
        self.pause_start_time = None
        self.ghost_move_timer = 0
        self.hit_animation_timer = 0
        self.is_hit = False
        self.is_bullet_phase_active = False

    def on_draw(self):
        self.clear()

        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        arcade.draw_lrbt_rectangle_outline(
            self.square_left, self.square_right,
            self.square_bottom, self.square_top,
            SQUARE_COLOR, 3
        )

        ghost_color = (255, 100, 100, 200) if self.is_hit else (100, 100, 200, 180)
        arcade.draw_circle_filled(self.enemy_x, self.enemy_y, 50, ghost_color)
        arcade.draw_circle_filled(self.enemy_x - 15, self.enemy_y + 10, 8, (255, 255, 255, 200))
        arcade.draw_circle_filled(self.enemy_x + 15, self.enemy_y + 10, 8, (255, 255, 255, 200))
        arcade.draw_circle_filled(self.enemy_x - 15, self.enemy_y + 10, 4, (0, 0, 0, 200))
        arcade.draw_circle_filled(self.enemy_x + 15, self.enemy_y + 10, 4, (0, 0, 0, 200))

        if len(self.bullets) > 0:
            for bullet in self.bullets:
                arcade.draw_circle_filled(bullet["x"], bullet["y"], 15, arcade.color.YELLOW)

        if self.state == "BULLET_HELL":
            arcade.draw_circle_filled(self.heart_x, self.heart_y, self.heart_size, arcade.color.RED)
            arcade.draw_circle_outline(self.heart_x, self.heart_y, self.heart_size, arcade.color.DARK_RED, 3)

        if not self.paused and self.state == "PLAYER_TURN":
            arcade.draw_lrbt_rectangle_filled(30, 350, 150, 250, (0, 0, 0, 150))

        hp_width = 200 * (self.player_hp / 20)
        arcade.draw_lrbt_rectangle_filled(50, 50 + hp_width, SCREEN_HEIGHT - 80, SCREEN_HEIGHT - 60, arcade.color.GREEN)
        arcade.draw_lrbt_rectangle_outline(50, 250, SCREEN_HEIGHT - 80, SCREEN_HEIGHT - 60, arcade.color.WHITE, 2)

        enemy_hp_width = 200 * (self.enemy_hp / 30)
        arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH - 250, SCREEN_WIDTH - 250 + enemy_hp_width, SCREEN_HEIGHT - 80,
                                          SCREEN_HEIGHT - 60, arcade.color.RED)
        arcade.draw_lrbt_rectangle_outline(SCREEN_WIDTH - 250, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 80,
                                           SCREEN_HEIGHT - 60, arcade.color.WHITE, 2)

        if self.attack_active and not self.paused:
            indicator_x = 100 + (self.attack_timer % 200)
            arcade.draw_lrbt_rectangle_filled(100, 300, SCREEN_HEIGHT // 2 - 10, SCREEN_HEIGHT // 2 + 10,
                                              arcade.color.GRAY)
            arcade.draw_lrbt_rectangle_filled(indicator_x - 5, indicator_x + 5, SCREEN_HEIGHT // 2 - 20,
                                              SCREEN_HEIGHT // 2 + 20, arcade.color.YELLOW)
            arcade.draw_text(
                "Нажми ПРОБЕЛ в нужный момент!",
                SCREEN_WIDTH // 2 - 150,
                SCREEN_HEIGHT // 2 + 50,
                arcade.color.WHITE,
                20
            )

        if self.start_time and self.game_active and not self.paused:
            self.elapsed_time = time.time() - self.start_time
            self.time_text.text = f"Время: {self.elapsed_time:.1f} сек"

        self.batch.draw()

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, PAUSE_OVERLAY_COLOR)
            self.pause_title_text.draw()
            for button in self.pause_buttons:
                button.draw()
            self.pause_batch.draw()

    def on_update(self, delta_time):
        if self.game_active and not self.paused:
            self.ghost_move_timer += delta_time
            new_y = self.ghost_base_y + math.sin(self.ghost_move_timer * self.ghost_move_speed) * self.ghost_move_range
            min_y = self.square_top + 100
            self.enemy_y = max(min_y, new_y)

            if self.is_hit:
                self.hit_animation_timer -= delta_time
                if self.hit_animation_timer <= 0:
                    self.is_hit = False

            if self.state == "BULLET_HELL":
                speed = 300 * delta_time

                if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
                    self.heart_x = max(self.square_left + self.heart_size, self.heart_x - speed)
                if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
                    self.heart_x = min(self.square_right - self.heart_size, self.heart_x + speed)
                if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
                    self.heart_y = min(self.square_top - self.heart_size, self.heart_y + speed)
                if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
                    self.heart_y = max(self.square_bottom + self.heart_size, self.heart_y - speed)

                if self.is_bullet_phase_active:
                    self.bullet_phase_timer += delta_time
                    self.bullet_timer += delta_time

                    if self.bullet_timer > 0.3 and self.bullet_phase_timer < self.bullet_phase_duration:
                        self.create_bullet()
                        self.bullet_timer = 0

                bullets_to_remove = []
                for i, bullet in enumerate(self.bullets):
                    bullet["x"] += bullet["dx"] * bullet["speed"] * delta_time
                    bullet["y"] += bullet["dy"] * bullet["speed"] * delta_time

                    distance = math.sqrt((bullet["x"] - self.heart_x) ** 2 + (bullet["y"] - self.heart_y) ** 2)
                    if distance < self.heart_size + 15:
                        self.player_hp -= 2
                        bullets_to_remove.append(i)
                        self.hp_text.text = f"HP: {self.player_hp}/20"

                    if (bullet["x"] < -100 or bullet["x"] > SCREEN_WIDTH + 100 or
                            bullet["y"] < -100 or bullet["y"] > SCREEN_HEIGHT + 100):
                        bullets_to_remove.append(i)

                for i in sorted(bullets_to_remove, reverse=True):
                    self.bullets.pop(i)

                if self.is_bullet_phase_active and self.bullet_phase_timer >= self.bullet_phase_duration:
                    self.is_bullet_phase_active = False

                if not self.is_bullet_phase_active and len(self.bullets) == 0:
                    self.state = "PLAYER_TURN"
                    self.bullet_phase_timer = 0

            elif self.attack_active:
                self.attack_timer += delta_time * 100

            if self.player_hp <= 0:
                self.player_hp = 0
                self.end_battle("ПОРАЖЕНИЕ")
            elif self.enemy_hp <= 0:
                self.enemy_hp = 0
                self.end_battle("ПОБЕДА")

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
            int(self.square_left + 20),
            int(self.square_right - 20)
        )
        target_y = random.randint(
            int(self.square_bottom + 20),
            int(self.square_top - 20)
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

        if not self.paused:
            if self.state == "PLAYER_TURN":
                if key == arcade.key.ENTER or key == arcade.key.SPACE:
                    self.attack_active = True
                    self.attack_timer = 0

            if self.state == "BULLET_HELL":
                if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D,
                           arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S]:
                    self.keys_pressed.add(key)

            elif self.attack_active:
                if key == arcade.key.SPACE:
                    indicator_pos = 100 + (self.attack_timer % 200)
                    target_pos = 250
                    accuracy = 1.0 - abs(target_pos - indicator_pos) / 100

                    damage = int(10 * max(0.2, accuracy))
                    self.enemy_hp -= damage
                    self.enemy_hp_text.text = f"Враг HP: {self.enemy_hp}"

                    self.is_hit = True
                    self.hit_animation_timer = 0.3

                    self.attack_active = False
                    self.state = "ENEMY_TURN"

                    arcade.schedule(self.start_enemy_turn, 1.0)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D,
                   arcade.key.UP, arcade.key.W, arcade.key.DOWN, arcade.key.S]:
            self.keys_pressed.discard(key)

    def update_menu_colors(self):
        for i, text in enumerate(self.menu_texts):
            text.color = arcade.color.YELLOW if i == self.selected_option else arcade.color.WHITE

    def select_menu_option(self):
        if self.menu_options[self.selected_option] == "АТАКА":
            self.attack_active = True
            self.attack_timer = 0

    def start_enemy_turn(self, delta_time):
        arcade.unschedule(self.start_enemy_turn)
        self.state = "BULLET_HELL"
        self.is_bullet_phase_active = True
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_phase_timer = 0

    def end_battle(self, result):
        self.game_active = False
        arcade.schedule(self.show_results, 2.0)

    def show_results(self, delta_time):
        arcade.unschedule(self.show_results)
        result_view = ResultView(self.elapsed_time)
        result_view.setup()
        self.window.show_view(result_view)

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
            elif self.finish_button.check_click(x, y):
                self.game_active = False
                if self.pause_start_time:
                    pause_duration = time.time() - self.pause_start_time
                    self.start_time += pause_duration
                result_view = ResultView(self.elapsed_time)
                result_view.setup()
                self.window.show_view(result_view)


class ResultView(arcade.View):

    def __init__(self, elapsed_time):
        super().__init__()
        self.elapsed_time = elapsed_time
        self.menu_button = None
        self.batch = None
        self.title_text = None
        self.session_text = None
        self.time_text = None

    def setup(self):
        self.batch = Batch()

        self.menu_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ В МЕНЮ"
        )
        self.menu_button.create_text_object(self.batch)

        self.title_text = arcade.Text(
            "РЕЗУЛЬТАТ ПОПЫТКИ",
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

        self.session_text = arcade.Text(
            "Сессия длилась",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 30,
            arcade.color.LIGHT_GRAY,
            32,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

        self.time_text = arcade.Text(
            f"{self.elapsed_time:.1f} секунд",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 30,
            arcade.color.WHITE,
            40,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True,
            batch=self.batch
        )

    def on_draw(self):
        self.clear()

        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)

        self.menu_button.draw()
        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.menu_button:
            self.menu_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.menu_button:
            if self.menu_button.check_click(x, y):
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenuView()
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()

