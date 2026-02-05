import arcade
from pyglet.graphics import Batch
from .beautiful_button import BeautifulButton
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, BACKGROUND_COLOR

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
                # Импорт GameView только здесь
                from .game_view import GameView
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)
            elif self.settings_button.check_click(x, y):
                # Импорт SettingsView только здесь
                from .settings_view import SettingsView
                settings_view = SettingsView()
                settings_view.setup()
                self.window.show_view(settings_view)
            elif self.exit_button.check_click(x, y):
                arcade.exit()