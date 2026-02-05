import arcade
from pyglet.graphics import Batch
from .beautiful_button import BeautifulButton
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BACKGROUND_COLOR

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
                # Импорт MainMenuView только здесь
                from .main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)