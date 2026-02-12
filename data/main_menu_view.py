import arcade
import random
from pyglet.graphics import Batch
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount
from data.beautiful_button import BeautifulButton
from data.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, BACKGROUND_COLOR

# ========== ТЕКСТУРЫ ДЛЯ ЧАСТИЦ ==========
PARTICLE_TEXTURES = [
    arcade.make_circle_texture(4, (255, 200, 100, 255)),  # жёлтый
    arcade.make_circle_texture(5, (255, 150, 50, 255)),   # оранжевый
    arcade.make_circle_texture(3, (255, 100, 50, 255)),   # красно-оранжевый
    arcade.make_circle_texture(4, (255, 220, 150, 255)),  # светло-жёлтый
]


def particle_factory(center_x, center_y):
    """Создаёт одну частицу"""
    texture = random.choice(PARTICLE_TEXTURES)
    particle = FadeParticle(
        filename_or_texture=texture,
        change_xy=(random.uniform(-30, 30), random.uniform(-30, 30)),
        lifetime=random.uniform(2.0, 3.0),
        mutation_callback=None
    )
    particle.center_x = center_x
    particle.center_y = center_y
    return particle


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.batch = None
        self.title_text = None
        self.emitter = None

    def setup(self):
        self.batch = Batch()

        button_y = SCREEN_HEIGHT // 2 + BUTTON_HEIGHT

        # ===== МУЗЫКА =====
        if hasattr(self.window, 'background_music') and self.window.background_music:
            self.background_music = self.window.background_music
            if hasattr(self.window, 'music_enabled'):
                self.sound_enabled = self.window.music_enabled
            if hasattr(self.window, 'music_volume'):
                self.background_music.volume = self.window.music_volume
            if self.sound_enabled:
                self.background_music.play(volume=self.background_music.volume, loop=True)
            else:
                self.background_music.pause()

        # ===== КНОПКИ =====
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

        # ===== ЗАГОЛОВОК =====
        self.title_text = arcade.Text(
            "THE GAME",
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
        
        self.setup_emitter()

    def setup_emitter(self):
        """Создаёт эмиттер, который постоянно генерирует частицы по всему экрану"""

        def emit_position(emitter):
            """Генерирует частицы в случайных позициях экрана"""
            return random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)

        self.emitter = Emitter(
            center_xy=(0, 0),  # не используется, т.к. есть emit_position
            emit_controller=EmitInterval(0.02),  # частица каждые 0.05 сек
            particle_factory=lambda e: particle_factory(*emit_position(e))
        )

    def on_draw(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)
        if self.emitter:
            self.emitter.draw()

        for button in self.buttons:
            button.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        # Обновляем эмиттер
        if self.emitter:
            self.emitter.update(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.play_button.check_click(x, y):
                from data.game_view import GameView
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)
            elif self.settings_button.check_click(x, y):
                from data.settings_view import SettingsView
                settings_view = SettingsView()
                settings_view.setup()
                self.window.show_view(settings_view)
            elif self.exit_button.check_click(x, y):
                arcade.exit()
