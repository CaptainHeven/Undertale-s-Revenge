import arcade
from pyglet.graphics import Batch
from .beautiful_button import BeautifulButton
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BACKGROUND_COLOR

class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.batch = None
        self.title_text = None
        self.message_text = None

    def setup(self):
        self.batch = Batch()

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
                # Импорт MainMenuView только здесь
                from .main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)